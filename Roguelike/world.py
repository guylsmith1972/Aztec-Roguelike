from constants import *
from native_code import generate_noise
from terrain_chunk import TerrainChunk
from terrain_generator import generate_seeds, fill_chunk
import configuration
import math
import terrain


class World:
    def __init__(self, screen, player_position, terrain_chunk_size, spritesheets, render_order):
        self.voronoi_seeds = None
        self.noise = None
        self.terrain_types = terrain.Terrain(spritesheets[TYPE_TERRAIN])
        self.player_position = player_position
        self.spritesheets = spritesheets
        self.render_order = render_order
        self.terrain_chunk_size = terrain_chunk_size
        self.terrain_chunks = set()  # We need to create an empty set first because calling self.get_relevant_terrain_chunks() needs this to be defined as a set instead of as None

        self.define_world()
        self.terrain_chunks = self.get_relevant_terrain_chunks(screen)

    def cleanup(self):
        TerrainChunk.cleanup_cache()            

    def define_world(self):
        rng_seed_noise = configuration.get('world.generator.random.seed.noise', 45)
        self.noise = generate_noise(1024, 5, 1, rng_seed_noise)
        
    def get_chunk_values(self, x, y, size):
        terrain_spritesheet = self.get_spritesheets()[TYPE_TERRAIN]
        seeds = generate_seeds(terrain_spritesheet, x, y)
        coverage, _ = fill_chunk(seeds, x, y, size, self.noise)
        return coverage
        
    def set_spritesheets(self, spritesheets):
        self.spritesheets = spritesheets
        self.terrain_types = terrain.Terrain(spritesheets[TYPE_TERRAIN])
            
    def get_spritesheets(self):
        return self.spritesheets

    def get_relevant_terrain_chunks(self, screen):
        """Generate a list of relevant terrain_chunks based on the current player and NPC positions."""
        new_relevant_terrain_chunks = set()

        terrain_chunk_width = self.terrain_chunk_size * self.spritesheets[TYPE_TERRAIN].tile_width
        terrain_chunk_height = self.terrain_chunk_size * self.spritesheets[TYPE_TERRAIN].tile_height

        # Find the terrain_chunks relevant to the player's position
        player_terrain_chunk_x = self.player_position[0] // self.terrain_chunk_size
        player_terrain_chunk_y = self.player_position[1] // self.terrain_chunk_size
        for dx in range(-math.floor(screen.get_width() / terrain_chunk_width / 2) - 1, math.ceil(screen.get_width() / terrain_chunk_width / 2) + 1):
            for dy in range(-math.floor(screen.get_height() / terrain_chunk_height / 2) - 1, math.ceil(screen.get_height() / terrain_chunk_height / 2) + 1):
                new_relevant_terrain_chunks.add(TerrainChunk.get_or_create((player_terrain_chunk_x + dx) * self.terrain_chunk_size,
                                                              (player_terrain_chunk_y + dy) * self.terrain_chunk_size,
                                                              self.terrain_chunk_size,
                                                              self))

        # TODO: Select terrain_chunks for active creatures
            
        # Mark previous terrain_chunks that are no longer relevant as invalid
        current_terrain_chunks_set = set(self.terrain_chunks)
        for terrain_chunk in current_terrain_chunks_set - new_relevant_terrain_chunks:
            TerrainChunk.mark_as_invalid(terrain_chunk.world_x, terrain_chunk.world_y, terrain_chunk.size)

        return new_relevant_terrain_chunks

    def update_positions(self, screen, new_player_position):
        """
        Update the player's and NPCs' positions, and refresh the list of relevant terrain_chunks.
        """
        self.player_position = new_player_position
        self.terrain_chunks = self.get_relevant_terrain_chunks(screen)
        
    def render(self, display, center_x, center_y):
        # Render terrain_chunks
        for terrain_chunk in self.terrain_chunks:
            terrain_chunk.render(display, center_x, center_y)
        
    def is_passable_at(self, world_x, world_y):
        for terrain_chunk in self.terrain_chunks:
            if terrain_chunk.contains_position(world_x, world_y):
                terrain_index = terrain_chunk.get_layer_index_at(TYPE_TERRAIN, world_x, world_y)
                if not self.terrain_types.is_passable(terrain_index):
                    return False
            
        return True

        
        