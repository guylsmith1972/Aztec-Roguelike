
class Movable:
    def __init__(self, item_id, item_type, position):
        self.item_id = item_id          # Unique identifier for the movable
        self.item_type = item_type      # Type or category of the movable (ITEM, CREATURE, PLACEABLE, etc.)
        self.position = position        # (x, y) tuple representing the movable's location in the world

    def __repr__(self):
        return f"Movable(id={self.item_id}, type={self.item_type}, position={self.position})"
