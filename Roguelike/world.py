import pygame
from region import Region


class World:
    def __init__(self, player_position, npc_positions, region_size):
        self.player_position = player_position
        self.npc_positions = npc_positions
        self.region_size = region_size
        self.regions = set()  # We need to create an empty set first because calling self.get_relevant_regions() needs this to be defined as a set instead of as None
        self.regions = self.get_relevant_regions()
        self.creatures = []  # List of creatures in the world

    def get_relevant_regions(self):
        """Generate a list of relevant regions based on the current player and NPC positions."""
        new_relevant_regions = set()

        # Find the regions relevant to the player's position
        player_region_x = self.player_position[0] // self.region_size
        player_region_y = self.player_position[1] // self.region_size
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_relevant_regions.add(Region.get_or_create((player_region_x + dx) * self.region_size,
                                                              (player_region_y + dy) * self.region_size,
                                                              self.region_size))

        # Add regions for NPCs
        for npc_position in self.npc_positions:
            npc_region_x = npc_position[0] // self.region_size
            npc_region_y = npc_position[1] // self.region_size
            new_relevant_regions.add(Region.get_or_create(npc_region_x * self.region_size,
                                                          npc_region_y * self.region_size,
                                                          self.region_size))

        # Mark previous regions that are no longer relevant as invalid
        current_regions_set = set(self.regions)
        for region in current_regions_set - new_relevant_regions:
            Region.mark_as_invalid(region.world_x, region.world_y, region.size)

        return new_relevant_regions

    def update_positions(self, new_player_position, new_npc_positions):
        """
        Update the player's and NPCs' positions, and refresh the list of relevant regions.
        """
        self.player_position = new_player_position
        self.npc_positions = new_npc_positions
        self.regions = self.get_relevant_regions()

    def render(self, screen, center_x, center_y, tileset):
        # Render regions
        for region in self.regions:
            region.render(screen, center_x, center_y, tileset)

        # Render creatures:
        for creature in self.creatures:
            index = creature[0]
            position = creature[1]
            tileset.render(screen, tileset.CREATURE, index, position[0], position[1], self.player_position[0], self.player_position[1])
            
        # Render player:
        tileset.render(screen, tileset.CREATURE, 0, self.player_position[0], self.player_position[1], self.player_position[0], self.player_position[1])

    def add_creature(self, name, x, y):
        """Add a creature to the region."""
        self.creatures.append((name, (x,y)))

    def remove_creature(self, name, x, y):
        """Remove a creature from the region."""
        self.creatures.remove((name, (x,y)))

    def get_creatures(self):
        """Get all creatures in the region."""
        return self.creatures