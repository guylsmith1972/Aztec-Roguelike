class Item:
    def __init__(self, name, description, tile_index, quantity=1):
        self.name = name
        self.description = description
        self.tile_index = tile_index
        self.quantity = quantity

    def __repr__(self):
        return f"Item(name={self.name}, quantity={self.quantity})"

    def use_by(self, user):
        # TODO: perform any special handling for a consumable item or other item that can be used in a solo capacity
        pass
    
    def use_on(self, user, target):
        # TODO: perform any special handling for an item that can be used by the user to affect a target (attack a foe, quech a fire, etc)
        pass
    
