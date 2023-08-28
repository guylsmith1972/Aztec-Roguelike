from inventory import Inventory

class Player:
    def __init__(self, world_x=0, world_y=0):
        self.world_x = world_x
        self.world_y = world_y
        self.world = None
        self.inventory = Inventory()

    def move(self, dx, dy):
        """
        Adjusts the player's position based on the given dx and dy offsets. 
        The position changes are not wrapped around in this version since the world 
        dynamically loads relevant regions.
        """
        self.world_x += dx
        self.world_y += dy

    def get_position(self):
        """
        Returns the player's current world coordinates.
        """
        return self.world_x, self.world_y
