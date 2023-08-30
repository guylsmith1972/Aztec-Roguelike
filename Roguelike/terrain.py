


class Terrain:
    def __init__(self, terrain_spritesheet):

        terrain_types_map = {}
        def add_terrain_type(name, passable):
            terrain_types_map[terrain_spritesheet.get_index(name)] = [name, passable]
            
        add_terrain_type('grass', True)
        add_terrain_type('grass-thick', True)
        add_terrain_type('granite', True)
        add_terrain_type('dirt', True)
        add_terrain_type('stones-small', True)
        add_terrain_type('stones-medium', True)
        add_terrain_type('cobble-colored', True)
        add_terrain_type('herringbone', True)
        add_terrain_type('wall', False)
        
        self.terrain_types = [None] * len(terrain_types_map)
    
        # Fill the list based on the order of the keys
        for key, value in terrain_types_map.items():
             self.terrain_types[key] = value

    def is_passable(self, terrain_index):
        return self.terrain_types[terrain_index][1]
    