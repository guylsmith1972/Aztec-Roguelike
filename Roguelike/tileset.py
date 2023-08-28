import pygame


# Defining the Tileset class

class Tileset:
    TERRAIN = 0
    ITEM = 1
    FEATURE = 2
    CREATURE = 3
    
    tile_definitions = {
        TERRAIN: [
            ('grass', (0, 255, 0)),
            ('rock', (128, 128, 128)),
            ],
        ITEM: [
            ('sword', (255, 215, 0)),
            ('shield', (192, 192, 192)),
        ],
        FEATURE: [
            ('tree', (34, 139, 34)),
            ('wall', (0, 0, 0))
        ], 
        CREATURE: [
            ('player', (255, 0, 0))
        ]
    }
    
    def __init__(self, tile_size):
        self._tile_size = int(tile_size)
        
    def tile_size(self):
        return self._tile_size
    
    def render(self, screen, tile_type, tile_index, world_x, world_y, center_x, center_y):
        color = self.tile_definitions[tile_type][tile_index][1]
        screen_x = (world_x - center_x) * self._tile_size + (screen.get_width() - self._tile_size) / 2
        screen_y = (world_y - center_y) * self._tile_size + (screen.get_height() - self._tile_size) / 2
        pygame.draw.rect(screen, color, (screen_x, screen_y, self._tile_size, self._tile_size))

    def screen_to_world(self, screen, screen_x, screen_y, center_x, center_y):
        world_x = (screen_x - (screen.get_width() - self._tile_size) / 2) / self._tile_size + center_x
        world_y = (screen_y - (screen.get_height() - self._tile_size) / 2) / self._tile_size + center_y
        return int(world_x), int(world_y)
