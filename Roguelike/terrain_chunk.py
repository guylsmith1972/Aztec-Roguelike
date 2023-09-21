from collections import deque
from constants import *
from gpu_shader import get_shader, RENDER
from gpu_texture import Texture
from gpu_vertex_array import VertexArray
from gpu_vertex_buffer import get_unit_quad
import configuration
import gpu
import numpy as np


class TerrainChunk:
    _terrain_chunk_cache = {}  # Cache for terrain_chunks
    _terrain_chunk_validity = {}  # Validity status of terrain_chunks
    _invalid_terrain_chunks_LRU = deque()  # LRU queue for invalid terrain_chunks
    
    class Layer:
        def __init__(self):        
            self.indices = None
            self.texture = None
            self._dirty  = True
            
        def cleanup(self):
            if self.texture is not None:
                self.texture.cleanup()
                self.texture = None
                
        def assign_indices(self, indices):
            self.indices = indices
            self._dirty = True
            
        def get_index_at(self, x, y):
            return self.indices[y][x]
        
        def set_index_at(self, x, y, new_index):
            self.indices[y][x] = new_index
            
        def render(self, display, shader, spritesheet, size, world_x, world_y, center_x, center_y):
            if self._dirty:
                self.cleanup()
                self.texture = Texture({"type": "numpy", "data_format": "R", "data": {"red": self.indices}},
                                           min_filter='nearest', mag_filter='nearest', wrap_s='clamp', wrap_t='clamp')
                self._dirty = False
                
            tile_width = spritesheet.tile_width
            tile_height = spritesheet.tile_height
            shader = get_shader(RENDER, 'tile_grid_renderer')
        
            target_width, target_height = tile_width * size, tile_height *size
    
            shader.set_uniform('spritesheet', 'sampler2D', spritesheet.texture.texture, 0)
            shader.set_uniform('tile_indices', 'sampler2D', self.texture.texture, 1)

            shader.set_uniform('target_dimensions_in_pixels', '2i', target_width, target_height)
            spritesheet_dimensions = spritesheet.get_dimensions_in_tiles()
            shader.set_uniform('spritesheet_dimensions_in_tiles', '2i', *spritesheet_dimensions)
            shader.set_uniform('tile_dimensions_in_pixels', '2i', tile_width, tile_height)
            shader.set_uniform('show_grid_lines', '1i', 1 if configuration.get('debug.rendering.show_grid_lines', False) else 0)
            shader.set_uniform('show_chunk_lines', '1i', 1 if configuration.get('debug.rendering.show_chunk_lines', False) else 0)
    
            # Render the shader to the pygame screen at display, screen_y
            screen_x = int((world_x - center_x) * tile_width + (display.get_width() - tile_width) / 2)
            screen_y = int((world_y - center_y) * tile_height + (display.get_height() - tile_height) / 2)
            unit_quad = get_unit_quad()
            vertex_array = VertexArray(shader, {'in_position': unit_quad})
            vertex_array.bind()

            shader.render(display, unit_quad, screen_x, screen_y, target_width, target_height)
            vertex_array.unbind()
            vertex_array.cleanup()
            
    def __init__(self, world_x, world_y, size, world):
        self.world = world
        self.world_x = world_x
        self.world_y = world_y
        self.size = size
        self.layers = {layer_type: TerrainChunk.Layer() for layer_type in world.get_spritesheets()}
        for layer_type in world.render_order:
            indices = self.world.get_chunk_values(self.world_x, self.world_y, self.size) if layer_type == TYPE_TERRAIN else np.full((size, size), -1)
            self.layers[layer_type].assign_indices(indices)

    def cleanup(self):
        for _, layer in self.layers.items():
            if layer is not None:
                layer.cleanup()
                

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
                cls._terrain_chunk_cache[oldest_invalid_key].cleanup()
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
    
    def render(self, display, center_x, center_y):
        shader = get_shader(RENDER, 'tile_grid_renderer')
        shader.use()

        for layer_type in self.world.render_order:
            layer = self.layers[layer_type]
            spritesheet = self.world.get_spritesheets()[layer_type]
            layer.render(display, shader, spritesheet, self.size, self.world_x, self.world_y, center_x, center_y)
            gpu.start_blending()        
        gpu.stop_blending()

    def get_layer_index_at(self, layer_type, world_x, world_y):
        # Calculate relative coordinates within the terrain_chunk
        rel_x = world_x - self.world_x
        rel_y = world_y - self.world_y
        return self.layers[layer_type].get_index_at(rel_x, rel_y)
    
    def set_layer_index_at(self, layer_type, world_x, world_y, new_index):
        rel_x = world_x - self.world_x
        rel_y = world_y - self.world_y
        self.layers[layer_type].set_index_at(rel_x, rel_y, new_index)

    def contains_position(self, x, y):
        return self.world_x <= x < self.world_x + self.size and self.world_y <= y < self.world_y + self.size
    
    def is_passable_at(self, world_x, world_y):
        return True

    @staticmethod
    def cleanup_cache():
        for _, chunk in TerrainChunk._terrain_chunk_cache.items():
            chunk.cleanup()
   