from inventory import Inventory

class Player:
    def __init__(self, world_x=0, world_y=0):
        self.world_x = world_x
        self.world_y = world_y
        self.world = None
        self.inventory = Inventory()

    def move(self, dx, dy):
        new_x = self.world_x + dx
        new_y = self.world_y + dy
        if self.world.is_passable_at(new_x, new_y):
            self.world_x = new_x
            self.world_y = new_y

    def get_position(self):
        return self.world_x, self.world_y
