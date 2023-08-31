import enum
import numpy as np

# Redefining the EcosystemType enum and associated functions
class EcosystemType(enum.Enum):
    MOUNTAINS = 1
    FORESTS = 2
    PLAINS = 3
    SWAMPS = 4
    OCEANS = 5
    POPULATED_AREAS = 6

ECOSYSTEM_WEIGHT_RANGES = {
    EcosystemType.MOUNTAINS: (0.9, 1.1),
    EcosystemType.FORESTS: (0.8, 1.2),
    EcosystemType.PLAINS: (0.85, 1.15),
    EcosystemType.SWAMPS: (0.8, 1.2),
    EcosystemType.OCEANS: (0.95, 1.05),
    EcosystemType.POPULATED_AREAS: (0.9, 1.1)
}

def generate_weight_for_ecosystem(ecosystem_type):
    weight_range = ECOSYSTEM_WEIGHT_RANGES[ecosystem_type]
    return np.random.uniform(weight_range[0], weight_range[1])

# Redefining the Cloud, Region, and RegionManager classes as previously described
class Cloud:
    def __init__(self):
        self.cloud_data = {}
        
    def _get_region_coordinates(self, x, y):
        region_size = 200
        region_x = x // region_size
        region_y = y // region_size
        return (region_x, region_y)
    
    def add_seed(self, x, y, ecosystem_type):
        region_coords = self._get_region_coordinates(x, y)
        weight = generate_weight_for_ecosystem(ecosystem_type)
        if region_coords not in self.cloud_data:
            self.cloud_data[region_coords] = []
        self.cloud_data[region_coords].append((x, y, ecosystem_type, weight))
        
    def get_seeds_for_region(self, region_x, region_y):
        return self.cloud_data.get((region_x, region_y), [])
    
    def region_has_seeds(self, region_x, region_y):
        return (region_x, region_y) in self.cloud_data
    
    def generate_seeds_for_region(self, region_x, region_y, num_seeds=10):
        region_size = 200
        for _ in range(num_seeds):
            x = np.random.randint(region_x * region_size, (region_x + 1) * region_size)
            y = np.random.randint(region_y * region_size, (region_y + 1) * region_size)
            ecosystem_type = np.random.choice(list(EcosystemType))
            self.add_seed(x, y, ecosystem_type)

class Region:
    def __init__(self, ownership_data):
        self.ownership_data = ownership_data

class RegionManager:
    def __init__(self, cloud):
        self.cloud = cloud
        self.regions = {}
        
    def _get_neighboring_regions(self, region_x, region_y):
        neighbors = [
            (region_x - 1, region_y - 1), (region_x, region_y - 1), (region_x + 1, region_y - 1),
            (region_x - 1, region_y),                                 (region_x + 1, region_y),
            (region_x - 1, region_y + 1), (region_x, region_y + 1), (region_x + 1, region_y + 1)
        ]
        return neighbors
        
    def request_region(self, region_x, region_y):
        if (region_x, region_y) in self.regions:
            return self.regions[(region_x, region_y)]
        
        for neighbor in self._get_neighboring_regions(region_x, region_y):
            if not self.cloud.region_has_seeds(*neighbor):
                self.cloud.generate_seeds_for_region(*neighbor)
        
        seeds = []
        for region_coords in [(region_x, region_y)] + self._get_neighboring_regions(region_x, region_y):
            seeds.extend(self.cloud.get_seeds_for_region(*region_coords))
        
        new_region = Region(seeds)
        self.regions[(region_x, region_y)] = new_region
        
        return new_region

# Test the RegionManager
cloud = Cloud()
cloud.generate_seeds_for_region(0, 0)
region_manager = RegionManager(cloud)
requested_region = region_manager.request_region(0, 0)
print(requested_region.ownership_data)
