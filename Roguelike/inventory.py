class Inventory:
    def __init__(self, capacity=None):
        self.items = []
        self.capacity = capacity

    def add(self, item):
        if self.capacity and len(self.items) >= self.capacity:
            return False  # Inventory full
        self.items.append(item)
        return True

    def remove(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def has_item(self, item_name):
        return any(item.name == item_name for item in self.items)

    def get_all_items(self):
        return self.items

    def is_full(self):
        if self.capacity:
            return len(self.items) >= self.capacity
        return False

    def __repr__(self):
        return f"Inventory(items={self.items}, capacity={self.capacity})"
