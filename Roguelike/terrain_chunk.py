from collections import deque
from tkinter import SE
from item import Item

import configuration
import numpy as np
import opensimplex
import pygame


# Vectorized version of the get_tile_index function
_vectorized_get_tile_index = None


class TerrainChunk:
    _terrain_chunk_cache = {}  # Cache for terrain_chunks
    _terrain_chunk_validity = {}  # Validity status of terrain_chunks
    _invalid_terrain_chunks_LRU = deque()  # LRU queue for invalid terrain_chunks

    def __init__(self, world_x, world_y, size, world):
        self.world = world
        self.world_x = world_x
        self.world_y = world_y
        self.size = size
        self.items = []  # List of movable objects in the terrain_chunk
        self.features = []  # List of immobile objects in the terrain_chunk
        self._dirty = True  # True if the terrain_image needs to be generated
        self.prerendered_image = None
        self.tile_width = world.get_spritesheets()['terrain'].tile_width
        self.tile_height = world.get_spritesheets()['terrain'].tile_height
        self.terrain_indices = None
        self.generate_terrain()
        
    @staticmethod
    def generate_vectorized_getter(spritesheet):
        def generate_getter():
            # Hardcode the values for each tile name
            granite = spritesheet.get_index('granite')
            stones_medium = spritesheet.get_index('stones-medium')
            stones_small = spritesheet.get_index('stones-small')
            dirt = spritesheet.get_index('dirt')
            grass = spritesheet.get_index('grass')
            grass_thick = spritesheet.get_index('grass-thick')
    
            def corrected_optimized_get_tile_name(n):
                if n < -0.9:
                    return granite
                elif n < -0.8:
                    return stones_medium
                elif n < -0.7:
                    return stones_small
                elif n < -0.6:
                    return dirt
                elif n < 0.2:
                    return grass
                else:
                    return grass_thick
    
            return corrected_optimized_get_tile_name
        
        global _vectorized_get_tile_index
        _vectorized_get_tile_index = np.vectorize(generate_getter())

    @classmethod
    def get_or_create(cls, world_x, world_y, size, world):
        """Retrieve terrain_chunk from cache or create a new one if it doesn't exist."""
        key = (world_x, world_y, size)
        if key in cls._terrain_chunk_cache:
            # Mark the terrain_chunk as valid if it was previously invalid
            cls._terrain_chunk_validity[key] = True
            if key in cls._invalid_terrain_chunks_LRU:
                cls._invalid_terrain_chunks_LRU.remove(key)
        else:
            if len(cls._invalid_terrain_chunks_LRU) > configuration.get('max_invalid_terrain_chunks'):
                # Remove the least-recently-used invalid terrain_chunk
                oldest_invalid_key = cls._invalid_terrain_chunks_LRU.popleft()
                del cls._terrain_chunk_cache[oldest_invalid_key]
                del cls._terrain_chunk_validity[oldest_invalid_key]
            
            cls._terrain_chunk_cache[key] = cls(world_x, world_y, size, world)
            cls._terrain_chunk_validity[key] = True
        
        return cls._terrain_chunk_cache[key]

    @classmethod
    def mark_as_invalid(cls, world_x, world_y, size):
        """Mark a terrain_chunk as invalid."""
        key = (world_x, world_y, size)
        if key in cls._terrain_chunk_cache:
            cls._terrain_chunk_validity[key] = False
            cls._invalid_terrain_chunks_LRU.append(key)

    def __hash__(self):
        return hash((self.world_x, self.world_y, self.size))

    def __eq__(self, other):
        if isinstance(other, TerrainChunk):
            return self.world_x == other.world_x and self.world_y == other.world_y and self.size == other.size
        return False
    
    def set_terrain_at(self, x, y, terrain_index):
        self.terrain_indices[y][x] = terrain_index

    def generate_terrain(self):
        terrain_spritesheet = self.world.get_spritesheets()['terrain']
        if _vectorized_get_tile_index is None:
            TerrainChunk.generate_vectorized_getter(terrain_spritesheet)
            
        # Create numpy arrays for x and y coordinates
        x_coords = np.arange(self.world_x, self.world_x + self.size) / 15.0
        y_coords = np.arange(self.world_y, self.world_y + self.size) / 15.0

        # Generate the noise values for the entire grid using the 1D arrays
        noise_values = opensimplex.noise2array(x_coords, y_coords)

        # Use the vectorized function on the entire noise_values array
        self.terrain_indices = _vectorized_get_tile_index(noise_values)
        
        # Call into the world object to allow it to modify the chunk
        self.world.modify_chunk(self)

    def prerender(self):
        terrain_spritesheet = self.world.get_spritesheets()['terrain']

        # Cache constant values outside the loop
        tile_width = terrain_spritesheet.tile_width
        tile_height = terrain_spritesheet.tile_height

        # Create a new surface to render the terrain_chunk to
        surface_width = self.size * tile_width
        surface_height = self.size * tile_height
        terrain_chunk_surface = pygame.Surface((surface_width, surface_height))

        # Flatten the terrain_indices for reduced indexing overhead
        flattened_indices = [index for row in self.terrain_indices for index in row]

        # Render the entire terrain_chunk to the surface using single loop iteration
        for idx, tile_index in enumerate(flattened_indices):
            x = (idx % self.size) * tile_width
            y = (idx // self.size) * tile_height
            terrain_spritesheet.blit_to_surface(terrain_chunk_surface, tile_index, x, y)

        return terrain_chunk_surface

    def render(self, screen, center_x, center_y):
        terrain_spritesheet = self.world.get_spritesheets()['terrain']

        # Check if the terrain_chunk needs to be prerendered
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
        # Calculate relative coordinates within the terrain_chunk
        rel_x = world_x - self.world_x
        rel_y = world_y - self.world_y
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
