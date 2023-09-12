


class Terrain:
    def __init__(self, terrain_spritesheet):
        terrain_types_map = {}
        def set_terrain_type(name, passable):
            terrain_types_map[terrain_spritesheet.get_index(name)] = [name, passable]
            
        # Default all terrain types to passable
        terrain_names = terrain_spritesheet.get_all_terrain_names()
        for name in terrain_names:
            set_terrain_type(name, True)

        # Now override the non-default terrain types
        set_terrain_type('wall', False)

        # Convert the map to an array        
        self.terrain_types = [None] * len(terrain_types_map)
    
        # Fill the list based on the order of the keys
        for key, value in terrain_types_map.items():
             self.terrain_types[key] = value

    def is_passable(self, terrain_index):
        return self.terrain_types[int(terrain_index)][1]
    