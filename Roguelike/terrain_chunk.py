from collections import deque
from gpu_shader import get_shader, RENDER
from gpu_texture import Texture
from item import Item
import configuration
import numpy as np


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
        self.terrain_indices = None
        self.generate_terrain()
        self.terrain_texture = Texture({"type": "numpy", "data_format": "R", "data": {"red": self.terrain_indices}},
                                       min_filter='nearest', mag_filter='nearest', wrap_s='clamp', wrap_t='clamp')

    def cleanup(self):
        self.terrain_texture.cleanup()

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
            if len(cls._invalid_terrain_chunks_LRU) > configuration.get('terrain.max_invalid_chunks', 100):
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
        self.terrain_indices = self.world.get_chunk_values(self.world_x, self.world_y, self.size)   

        # Call into the world object to allow it to modify the chunk
        self.world.modify_chunk(self)

    def render(self, display, center_x, center_y):
        terrain_spritesheet = self.world.get_spritesheets()['terrain']     
        tile_width = terrain_spritesheet.tile_width
        tile_height = terrain_spritesheet.tile_height
        shader = get_shader(RENDER, 'tile_grid_renderer')
        shader.use()
        
        target_width, target_height = tile_width * self.size, tile_height * self.size
    
        shader.set_uniform('spritesheet', 'sampler2D', terrain_spritesheet.texture.texture, 0)
        shader.set_uniform('tile_indices', 'sampler2D', self.terrain_texture.texture, 1)

        shader.set_uniform('target_dimensions_in_pixels', '2i', target_width, target_height)
        spritesheet_dimensions = terrain_spritesheet.get_dimensions_in_tiles()
        shader.set_uniform('spritesheet_dimensions_in_tiles', '2i', *spritesheet_dimensions)
        shader.set_uniform('tile_dimensions_in_pixels', '2i', tile_width, tile_height)
    
        # Render the shader to the pygame screen at display, screen_y
        screen_x = int((self.world_x - center_x) * tile_width + (display.get_width() - tile_width) / 2)
        screen_y = int((self.world_y - center_y) * tile_height + (display.get_height() - tile_height) / 2)
        shader.render(screen_x, screen_y, target_width, target_height)

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
