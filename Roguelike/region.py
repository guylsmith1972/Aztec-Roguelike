from collections import deque
import math
import random
from item import Item

import configuration
import numpy as np
import opensimplex
import pygame


# Vectorize the get_tile_index function
_vectorized_get_tile_index = None


class Region:
    _region_cache = {}  # Cache for regions
    _region_validity = {}  # Validity status of regions
    _invalid_regions_LRU = deque()  # LRU queue for invalid regions

    def __init__(self, world_x, world_y, size, world):
        self.world = world
        self.world_x = world_x
        self.world_y = world_y
        self.size = size
        self.items = []  # List of movable objects in the region
        self.features = []  # List of immobile objects in the region
        self._dirty = True  # True if the terrain_image needs to be generated
        self.prerendered_image = None
        self.tile_width = world.get_spritesheets()['terrain'].tile_width
        self.tile_height = world.get_spritesheets()['terrain'].tile_height
        self.terrain_indices = self.generate_terrain()
        
    @staticmethod
    def generate_vectorized_getter(spritesheet):
        def generate_getter():
            # Hardcode the values for each tile name
            granite_val = spritesheet.get_index('granite')
            stones_medium_val = spritesheet.get_index('stones-medium')
            stones_small_val = spritesheet.get_index('stones-small')
            dirt_val = spritesheet.get_index('dirt')
            grass_val = spritesheet.get_index('grass')
            grass_thick_val = spritesheet.get_index('grass-thick')
    
            def corrected_optimized_get_tile_name(n):
                if n < -0.9:
                    return granite_val
                elif n < -0.8:
                    return stones_medium_val
                elif n < -0.7:
                    return stones_small_val
                elif n < -0.6:
                    return dirt_val
                elif n < 0.2:
                    return grass_val
                else:
                    return grass_thick_val
    
            return corrected_optimized_get_tile_name
        
        global _vectorized_get_tile_index
        _vectorized_get_tile_index = np.vectorize(generate_getter())

    @classmethod
    def get_or_create(cls, world_x, world_y, size, world):
        """Retrieve region from cache or create a new one if it doesn't exist."""
        key = (world_x, world_y, size)
        if key in cls._region_cache:
            # Mark the region as valid if it was previously invalid
            cls._region_validity[key] = True
            if key in cls._invalid_regions_LRU:
                cls._invalid_regions_LRU.remove(key)
        else:
            if len(cls._invalid_regions_LRU) > configuration.get('max_invalid_regions'):
                # Remove the least-recently-used invalid region
                oldest_invalid_key = cls._invalid_regions_LRU.popleft()
                del cls._region_cache[oldest_invalid_key]
                del cls._region_validity[oldest_invalid_key]
            
            cls._region_cache[key] = cls(world_x, world_y, size, world)
            cls._region_validity[key] = True
        
        return cls._region_cache[key]

    @classmethod
    def mark_as_invalid(cls, world_x, world_y, size):
        """Mark a region as invalid."""
        key = (world_x, world_y, size)
        if key in cls._region_cache:
            cls._region_validity[key] = False
            cls._invalid_regions_LRU.append(key)

    def __hash__(self):
        return hash((self.world_x, self.world_y, self.size))

    def __eq__(self, other):
        if isinstance(other, Region):
            return self.world_x == other.world_x and self.world_y == other.world_y and self.size == other.size
        return False

    def generate_terrain(self):
        terrain_spritesheet = self.world.get_spritesheets()['terrain']
        if _vectorized_get_tile_index is None:
            Region.generate_vectorized_getter(terrain_spritesheet)
            
        # Create numpy arrays for x and y coordinates
        x_coords = np.arange(self.world_x, self.world_x + self.size) / 15.0
        y_coords = np.arange(self.world_y, self.world_y + self.size) / 15.0

        # Generate the noise values for the entire grid using the 1D arrays
        noise_values = opensimplex.noise2array(x_coords, y_coords)

        # Use the vectorized function on the entire noise_values array
        terrain_indices = _vectorized_get_tile_index(noise_values)
        
        # add a randomly-placed wall
        terrain_indices[math.floor(random.random() * self.size)][math.floor(random.random() * self.size)] = terrain_spritesheet.get_index('wall')
        
        return terrain_indices

    def prerender(self):
        terrain_spritesheet = self.world.get_spritesheets()['terrain']

        # Cache constant values outside the loop
        tile_width = terrain_spritesheet.tile_width
        tile_height = terrain_spritesheet.tile_height

        # Create a new surface to render the region to
        surface_width = self.size * tile_width
        surface_height = self.size * tile_height
        region_surface = pygame.Surface((surface_width, surface_height))

        # Flatten the terrain_indices for reduced indexing overhead
        flattened_indices = [index for row in self.terrain_indices for index in row]

        # Render the entire region to the surface using single loop iteration
        for idx, tile_index in enumerate(flattened_indices):
            x = (idx % self.size) * tile_width
            y = (idx // self.size) * tile_height
            terrain_spritesheet.blit_to_surface(region_surface, tile_index, x, y)

        return region_surface

    def render(self, screen, center_x, center_y):
        terrain_spritesheet = self.world.get_spritesheets()['terrain']

        # Check if the region needs to be prerendered
        if self._dirty or self.tile_width != terrain_spritesheet.tile_width or self.tile_height != terrain_spritesheet.tile_height:
            self.prerendered_image = self.prerender()
            self._dirty = False
            self.tile_width = terrain_spritesheet.tile_width
            self.tile_height = terrain_spritesheet.tile_height
    
        # Calculate the screen's position based on the center coordinates
        screen_x = (self.world_x - center_x) * self.tile_width + (screen.get_width() - self.tile_width) / 2
        screen_y = (self.world_y - center_y) * self.tile_height + (screen.get_height() - self.tile_height) / 2
    
        # Blit the prerendered image to the screen
        screen.blit(self.prerendered_image, (screen_x, screen_y))

    def get_terrain_index_at(self, world_x, world_y):
        # Calculate relative coordinates within the region
        rel_x = world_x - self.world_x
        rel_y = world_y - self.world_y
        print(f'fetching index from {rel_x}, {rel_y}')
        return self.terrain_indices[rel_y][rel_x]

    def contains_position(self, x, y):
        return self.world_x <= x < self.world_x + self.size and self.world_y <= y < self.world_y + self.size
    
    def is_passable_at(self, world_x, world_y):
        return True
 
    def add_item(self, name, description, tile_index, x, y, quantity=1):
        item = Item(name, description, tile_index, quantity)
        self.items.append((item, (x, y)))
        self._dirty = True
    
    def remove_item(self, name, x, y):
        for item, position in self.items:
            if item.name == name and position == (x, y):
                self.items.remove((item, position))
                self._dirty = True
                break

    def get_items(self):
        return self.items

    def add_feature(self, tile_index, x, y):
        self.features.append((tile_index, (x,y)))
        self._dirty = True

    def remove_feature(self, tile_index, x, y):
        self.features.remove((tile_index, (x,y)))
        self._dirty = True

    def get_features(self):
        return self.features
