class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # Actual cache storage
        self.access_order = []  # Keeps track of access order for LRU eviction

    def get(self, key):
        if key in self.cache:
            # Move the accessed key to the end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            # If key already exists, move it to the end
            self.access_order.remove(key)
        else:
            # If cache is full, remove the least recently used entry
            if len(self.access_order) >= self.capacity:
                lru_key = self.access_order.pop(0)
                
                # Check if the object has a cleanup method and call it before deletion
                if hasattr(self.cache[lru_key], 'cleanup') and callable(self.cache[lru_key].cleanup):
                    self.cache[lru_key].cleanup()
                
                del self.cache[lru_key]
        
        # Add the new key and value to the cache and access order
        self.cache[key] = value
        self.access_order.append(key)
    
    # New method to clear the cache
    def clear(self):
        # Before clearing, check and call cleanup method for each item in the cache
        for key, value in self.cache.items():
            if hasattr(value, 'cleanup') and callable(value.cleanup):
                value.cleanup()
        self.cache.clear()
        self.access_order.clear()
