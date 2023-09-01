from collections import defaultdict
from copy import deepcopy
import math
from matplotlib.colors import ListedColormap
from native_code import generate_noisy_region_map, get_region_info
import configuration
import json
import matplotlib.pyplot as plt
import numpy as np

    
# Constants
DEEP_OCEAN = 0
CONTINENTAL_SHELF = 1
LITTORAL = 2
ISLANDS = 3
LAND = 4

world_width = configuration.get('world_width', 2048)
world_height = configuration.get('world_height', 1024)
world_zone_count = configuration.get('world_zone_count', 1500)
world_wrap_horizontal =  configuration.get('world_wrap_horizontal', 1)
max_ocean_cells = configuration.get('max_ocean_cells', 100)
ocean_ratio = configuration.get('ocean_ratio', 0.55)
island_zone_count = configuration.get('island_zone_count', 150000)
island_survival_rate = configuration.get('island_survival_rate', 0.05)
world_octaves = configuration.get('world_octaves', 4)
world_noise_divisor = configuration.get('world_noise_divisor', 20)
island_octaves = configuration.get('island_octaves', 8)
island_noise_divisor = configuration.get('island_noise_divisor', 20)
ocean_octaves = configuration.get('ocean_octaves', 2)
ocean_noise_divisor = configuration.get('ocean_noise_divisor', 100)


def histogram_of_ones(regions, index_array, value_array):
    # Check if the arrays have the same shape
    if index_array.shape != value_array.shape:
        raise ValueError("Both arrays should have the same shape")

    # Initialize the histogram with default values of 0
    histogram = dict.fromkeys(regions, 0)

    # Calculate histogram using numpy's bincount
    counts = np.bincount(index_array.ravel(), weights=value_array.ravel())
    
    # Update the histogram dictionary with the counts
    for i, count in enumerate(counts):
        if i in histogram:  # Update only the keys that are in regions
            histogram[i] = count

    return histogram


def transform_array(A, M):
    return np.array(M)[A]


def create_oceans(ownership_np, regions, world_cells, ocean_count):
    ocean_map_np, _ = make_map(world_width, world_height, max_ocean_cells, world_wrap_horizontal, ocean_octaves, ocean_noise_divisor)
    
    ocean_remap = []
    for i in range(world_cells):
        ocean_remap.append(1 if i < ocean_count else 0)
        
    remapped_ocean = transform_array(ocean_map_np, ocean_remap)
    
    histogram = histogram_of_ones(regions, ownership_np, remapped_ocean)

    
    continental_shelf_cutoff = configuration.get('continental_shelf_cutoff', 0.25)
    islands_cutoff = configuration.get('islands_cutoff', 0.05)
    
    world_remap = []
    for region_id, region in regions.items():
        ocean_type = None
        coverage = histogram[region_id]
        if coverage > 0:
            percentage = coverage / region['area']
            if percentage == 1:
                ocean_type = DEEP_OCEAN
                region['category'] = 'deep ocean'
            elif percentage >= continental_shelf_cutoff:
                ocean_type = CONTINENTAL_SHELF
                region['category'] = 'continental shelf'
            elif percentage > islands_cutoff:
                ocean_type = LITTORAL
                region['category'] = 'littoral'
            else:
                ocean_type = ISLANDS
                region['category'] = 'islands'
        new_value = LAND if ocean_type is None else ocean_type
        world_remap.append(new_value)
        
    return transform_array(ownership_np, world_remap)

def create_islands(coverage_map_np, width, height, world_wrap_horizontal):
    island_map_np, island_seeds = make_map(width, height, island_zone_count, world_wrap_horizontal, island_octaves, island_noise_divisor)
    island_zones = get_region_info(island_map_np, world_width, world_height, island_seeds, world_wrap_horizontal)
    print(f'number of island zones: {len(island_zones)} -- expected number of island zones: {island_zone_count}')
    island_remap = []
    max_index = math.floor(island_zone_count * island_survival_rate)
    for i in range(island_zone_count):
        island_remap.append(LAND if i < max_index else LITTORAL)
        
    # Contains 1 for islands, 0 for not-islands
    remapped_islands = transform_array(island_map_np, island_remap)

    return np.where(coverage_map_np==ISLANDS, remapped_islands, coverage_map_np)


def make_map(width, height, seed_count, wrap_horizontal, octaves, noise_divisor):
    seeds = [(np.random.randint(0, width),  np.random.randint(0, height)) for _ in range(seed_count)]
    weights = list(np.random.uniform(0.8, 1.2, seed_count))

    # Call the wrapper function
    map_np = generate_noisy_region_map(0, 0, width, height, seeds, weights, wrap_horizontal, octaves, noise_divisor)
    return map_np, seeds
        

region_map_np, region_seeds = make_map(world_width, world_height, world_zone_count, world_wrap_horizontal, world_octaves, world_noise_divisor)
regions = get_region_info(region_map_np, world_width, world_height, region_seeds, world_wrap_horizontal)
coverage_map_np = create_oceans(region_map_np, regions, max_ocean_cells, math.floor(max_ocean_cells * ocean_ratio))
island_mask_np = create_islands(coverage_map_np, world_width, world_height, world_wrap_horizontal)

# print(json.dumps(map_info, indent=4))

# Plot
# colors = ['#31618C', '#3498DB', '#8ED6F1', '#DC7633', '#8c564b']
colors = ['#3498DB', '#3498DB', '#3498DB', '#DC7633', '#8c564b']
cmap = ListedColormap(colors)

plt.figure(figsize=(10, 10))
plt.imshow(island_mask_np, cmap=cmap)
plt.title('')
plt.show()