import math
import pygame
from region import Region
import terrain


class World:
    def __init__(self, screen, player_position, region_size, spritesheets):
        self.terrain_types = terrain.Terrain(spritesheets['terrain'])
        self.player_position = player_position
        self.creatures = []  # List of creatures in the world
        self.spritesheets = spritesheets
        self.region_size = region_size
        self.regions = set()  # We need to create an empty set first because calling self.get_relevant_regions() needs this to be defined as a set instead of as None
        self.regions = self.get_relevant_regions(screen)
        
    def set_spritesheets(self, spritesheets):
        self.spritesheets = spritesheets
        self.terrain_types = terrain.Terrain(spritesheets['terrain'])
            
    def get_spritesheets(self):
        return self.spritesheets

    def get_relevant_regions(self, screen):
        """Generate a list of relevant regions based on the current player and NPC positions."""
        new_relevant_regions = set()

        region_width = self.region_size * self.spritesheets['terrain'].tile_width
        region_height = self.region_size * self.spritesheets['terrain'].tile_height

        # Find the regions relevant to the player's position
        player_region_x = self.player_position[0] // self.region_size
        player_region_y = self.player_position[1] // self.region_size
        for dx in range(-math.floor(screen.get_width() / region_width / 2) - 1, math.ceil(screen.get_width() / region_width / 2) + 1):
            for dy in range(-math.floor(screen.get_height() / region_height / 2) - 1, math.ceil(screen.get_height() / region_height / 2) + 1):
                new_relevant_regions.add(Region.get_or_create((player_region_x + dx) * self.region_size,
                                                              (player_region_y + dy) * self.region_size,
                                                              self.region_size,
                                                              self))

        # Add regions for creatures
        for creature_position in self.creatures:
            creature_region_x = creature_position[0] // self.region_size
            creature_region_y = creature_position[1] // self.region_size
            new_relevant_regions.add(Region.get_or_create(creature_region_x * self.region_size,
                                                          creature_region_y * self.region_size,
                                                          self.region_size,
                                                          self))
            
        # Mark previous regions that are no longer relevant as invalid
        current_regions_set = set(self.regions)
        for region in current_regions_set - new_relevant_regions:
            Region.mark_as_invalid(region.world_x, region.world_y, region.size)

        return new_relevant_regions

    def update_positions(self, screen, new_player_position):
        """
        Update the player's and NPCs' positions, and refresh the list of relevant regions.
        """
        self.player_position = new_player_position
        self.regions = self.get_relevant_regions(screen)

    def render(self, screen, center_x, center_y):
        # Render regions
        for region in self.regions:
            region.render(screen, center_x, center_y)

        # # Render creatures:
        # for creature in self.creatures:
        #     index = creature[0]
        #     position = creature[1]
        #     tileset.render(screen, tileset.CREATURE, index, position[0], position[1], self.player_position[0], self.player_position[1])
            
        # Render player:
        self.spritesheets['avatars'].render(screen, 0, self.player_position[0], self.player_position[1], self.player_position[0], self.player_position[1])
        
    def is_passable_at(self, world_x, world_y):
        for region in self.regions:
            if region.contains_position(world_x, world_y):
                terrain_index = region.get_terrain_index_at(world_x, world_y)
                print(f'world x,y: {world_x}, {world_y} produced index {terrain_index}')
                if not self.terrain_types.is_passable(terrain_index):
                    return False
                
        for creature in self.creatures:
            position = creature[1]
            if position[0] == world_x and position[1] == world_y:
                return False
            
        return True

    def add_creature(self, name, x, y):
        """Add a creature to the region."""
        self.creatures.append((name, (x,y)))

    def remove_creature(self, name, x, y):
        """Remove a creature from the region."""
        self.creatures.remove((name, (x,y)))

    def get_creatures(self):
        """Get all creatures in the region."""
        return self.creatures
