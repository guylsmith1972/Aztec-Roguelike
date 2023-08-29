from item import Item

from collections import deque
import random

import configuration
import opensimplex


class Region:
    _region_cache = {}  # Cache for regions
    _region_validity = {}  # Validity status of regions
    _invalid_regions_LRU = deque()  # LRU queue for invalid regions
    MAX_INVALID_REGIONS = 10  # Threshold for invalid regions

    def __init__(self, world_x, world_y, size):
        self.world_x = world_x
        self.world_y = world_y
        self.size = size
        self.items = []  # List of movable objects in the region
        self.features = []  # List of immobile objects in the region
        self.terrain_indices = self.generate_terrain()

    @classmethod
    def get_or_create(cls, world_x, world_y, size):
        """Retrieve region from cache or create a new one if it doesn't exist."""
        key = (world_x, world_y, size)
        if key in cls._region_cache:
            # Mark the region as valid if it was previously invalid
            cls._region_validity[key] = True
            if key in cls._invalid_regions_LRU:
                cls._invalid_regions_LRU.remove(key)
        else:
            if len(cls._invalid_regions_LRU) >=configuration.get('MAX_INVALID_REGIONS'):
                # Remove the least-recently-used invalid region
                oldest_invalid_key = cls._invalid_regions_LRU.popleft()
                del cls._region_cache[oldest_invalid_key]
                del cls._region_validity[oldest_invalid_key]
            
            cls._region_cache[key] = cls(world_x, world_y, size)
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
        # A simple terrain generation function for demonstration
        # The function can be replaced with a more complex noise-based or algorithmic approach
        terrain = []
        for j in range(self.size):
            row = []
            y = j + self.world_y
            for i in range(self.size):
                x = i + self.world_x
                n = opensimplex.noise2(x / 15.0, y / 15.0)
                if n < -0.8:
                    row.append(1)
                elif n < -0.6:
                    row.append(6)
                elif n < 0.2:
                    row.append(0)
                else:
                    row.append(8)
            
            terrain.append(row)

        # sprinkle random walls around the map
        for _ in range(10):
            x = min(self.size - 1, int(random.random() * self.size))
            y = min(self.size - 1, int(random.random() * self.size))
            self.add_feature(1, x, y)

        return terrain

    def render(self, screen, center_x, center_y, tileset, spritesheets):
        # Calculate screen's top-left and bottom-right world coordinates
        screen_left, screen_top = tileset.screen_to_world(screen, 0, 0, center_x, center_y)
        screen_right, screen_bottom = tileset.screen_to_world(screen, screen.get_width() + tileset.tile_size() - 1, screen.get_height() + tileset.tile_size() - 1, center_x, center_y)

        # Calculate region's top-left and bottom-right world coordinates
        region_left = self.world_x
        region_right = self.world_x + self.size
        region_top = self.world_y
        region_bottom = self.world_y + self.size
    
        # Calculate the overlapping area between the screen and the region
        overlap_left = max(screen_left, region_left)
        overlap_right = min(screen_right, region_right)
        overlap_top = max(screen_top, region_top)
        overlap_bottom = min(screen_bottom, region_bottom)
        
        terrain_spritesheet = spritesheets['terrain']
    
        # Render the overlapping terrain        
        terrain_slice = [
            self.terrain_indices[yy][overlap_left - self.world_x:overlap_right - self.world_x]
            for yy in range(overlap_top - self.world_y, overlap_bottom - self.world_y)
        ]
        for yy, row in enumerate(terrain_slice):
            for xx, tile_index in enumerate(row):
                terrain_spritesheet.render(screen, tile_index, self.world_x + xx + overlap_left - self.world_x, self.world_y + yy + overlap_top - self.world_y, center_x, center_y)
    
        # Render features       
        features_to_render = [(index, (pos[0] + self.world_x, pos[1] + self.world_y)) for index, pos in self.features if overlap_left <= pos[0] + self.world_x < overlap_right and overlap_top <= pos[1] + self.world_y < overlap_bottom]
        for index, position in features_to_render:
            tileset.render(screen, tileset.FEATURE, index, position[0], position[1], center_x, center_y)

        # Render items        
        items_to_render = [(index, (pos[0] + self.world_x, pos[1] + self.world_y)) for index, pos in self.items if overlap_left <= pos[0] + self.world_x < overlap_right and overlap_top <= pos[1] + self.world_y < overlap_bottom]
        for index, position in items_to_render:
            tileset.render(screen, tileset.ITEM, index, position[0], position[1], center_x, center_y)

    def contains_position(self, x, y):
        return self.world_x <= x < self.world_x + self.size and self.world_y <= y < self.world_y + self.size
    
    def is_passable_at(self, world_x, world_y):
        x = world_x - self.world_x
        y = world_y - self.world_y
        for feature in self.features:
            position = feature[1]
            if position[0] == x and position[1] == y:
                return False
        return True
 
    def is_overlapping_with_screen(self, screen, center_x, center_y, tileset):
        # Calculate screen's top-left and bottom-right world coordinates
        screen_left, screen_top = tileset.screen_to_world(screen, 0, 0, center_x, center_y)
        screen_right, screen_bottom = tileset.screen_to_world(screen, screen.get_width() - 1, screen.get_height() - 1, center_x, center_y)

        # Calculate region's top-left and bottom-right world coordinates
        region_left = self.world_x
        region_right = self.world_x + self.size
        region_top = self.world_y
        region_bottom = self.world_y + self.size

        # Check if the two rectangles overlap
        return (screen_left < region_right) and (screen_right > region_left) and \
               (screen_top < region_bottom) and (screen_bottom > region_top)

    def add_item(self, name, description, tile_index, x, y, quantity=1):
        item = Item(name, description, tile_index, quantity)
        self.items.append((item, (x, y)))
    
    def remove_item(self, name, x, y):
        for item, position in self.items:
            if item.name == name and position == (x, y):
                self.items.remove((item, position))
                break

    def get_items(self):
        return self.items

    def add_feature(self, tile_index, x, y):
        self.features.append((tile_index, (x,y)))

    def remove_feature(self, tile_index, x, y):
        self.features.remove((tile_index, (x,y)))

    def get_features(self):
        return self.features
