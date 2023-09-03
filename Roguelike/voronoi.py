from collections import defaultdict
from copy import deepcopy
import math
from matplotlib.colors import ListedColormap, BoundaryNorm
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
PLAINS = 5
HILLS = 6
MOUNTAINS = 7

world_width = configuration.get('world_width', 2048)
world_height = configuration.get('world_height', 1024)
world_zone_count = configuration.get('world_zone_count', 1500)
world_wrap_horizontal =  configuration.get('world_wrap_horizontal', 1)
world_octaves = configuration.get('world_octaves', 4)
world_noise_divisor = configuration.get('world_noise_divisor', 100)
world_horizontal_stretch =  configuration.get('world_horizontal_stretch', 1.5)

ocean_zone_count = configuration.get('ocean_zone_count', 100)
ocean_ratio = configuration.get('ocean_ratio', 0.55)
ocean_octaves = configuration.get('ocean_octaves', 2)
ocean_noise_divisor = configuration.get('ocean_noise_divisor', 100)
ocean_horizontal_stretch =  configuration.get('ocean_horizontal_stretch', 1)

island_zone_count = configuration.get('island_zone_count', 150000)
island_survival_rate = configuration.get('island_survival_rate', 0.05)
island_octaves = configuration.get('island_octaves', 4)
island_noise_divisor = configuration.get('island_noise_divisor', 100)
island_horizontal_stretch =  configuration.get('island_horizontal_stretch', 1)

mountain_zone_count = configuration.get('mountain_zone_count', 30)
mountain_survival_rate = configuration.get('mountain_survival_rate', 0.5)
mountain_octaves = configuration.get('mountain_octaves', 1)
mountain_noise_divisor = configuration.get('mountain_noise_divisor', 20)
mountain_horizontal_stretch =  configuration.get('mountain_horizontal_stretch', 1)
hills_cutoff_top = configuration.get('hills_cutoff', 0.7)
mountain_cutoff_top = configuration.get('mountain_cutoff_top', 0.6)
mountain_cutoff_bottom = configuration.get('mountain_cutoff_bottom', 0.4)
hills_cutoff_bottom = configuration.get('hills_cutoff_bottom', 0.3)


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
    ocean_map_np, _ = make_map(ocean_zone_count, world_wrap_horizontal, ocean_octaves, ocean_noise_divisor, ocean_horizontal_stretch)
    
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

def create_islands(coverage_map_np,world_wrap_horizontal):
    island_map_np, island_seeds = make_map(island_zone_count, world_wrap_horizontal, island_octaves, island_noise_divisor, island_horizontal_stretch)
    island_zones = get_region_info(island_map_np, world_width, world_height, island_seeds, world_wrap_horizontal)
    island_remap = []
    max_index = math.floor(island_zone_count * island_survival_rate)
    for i in range(island_zone_count):
        island_remap.append(LAND if i < max_index else LITTORAL)
        
    # Contains 1 for islands, 0 for not-islands
    remapped_islands = transform_array(island_map_np, island_remap)

    return np.where(coverage_map_np==ISLANDS, remapped_islands, coverage_map_np)


def create_mountains(coverage_map_np, ownership_map, regions, world_wrap_horizontal):
    mountain_zones_np, _ = make_map(mountain_zone_count, world_wrap_horizontal, mountain_octaves, mountain_noise_divisor, mountain_horizontal_stretch)

    mountain_remap = []
    mountain_survivors = math.floor(mountain_zone_count * mountain_survival_rate)
    for i in range(mountain_zone_count):
        mountain_remap.append(1 if i < mountain_survivors else 0)
        
    remapped_mountains = transform_array(mountain_zones_np, mountain_remap)    

    histogram = histogram_of_ones(regions, ownership_map, remapped_mountains)
    
    world_remap = []
    for region_id, region in regions.items():
        land_type = coverage_map_np[region['seed'][1]][region['seed'][0]]
        if land_type == LAND:
            coverage = histogram[region_id]
            percentage = coverage / region['area']
            if percentage > hills_cutoff_top:
                land_type = PLAINS
                region['category'] = 'plains'
            elif percentage > mountain_cutoff_top:
                land_type = HILLS
                region['category'] = 'hills'
            elif percentage > mountain_cutoff_bottom:
                land_type = MOUNTAINS
                region['category'] = 'mountains'
            elif percentage > hills_cutoff_bottom:
                land_type = HILLS
                region['category'] = 'hills'
            else:
                land_type = PLAINS
                region['category'] = 'plains'
        world_remap.append(land_type)

    return transform_array(ownership_map, world_remap)        

def make_map(seed_count, wrap_horizontal, octaves, noise_divisor, horizontal_stretch):
    seeds = [(np.random.randint(0, world_width),  np.random.randint(0, world_height)) for _ in range(seed_count)]
    weights = list(np.random.uniform(1.2, 1.6, seed_count))

    # Call the wrapper function
    map_np = generate_noisy_region_map(0, 0, world_width, world_height, seeds, weights, wrap_horizontal, octaves, noise_divisor, horizontal_stretch)
    return map_np, seeds
        

region_map_np, region_seeds = make_map(world_zone_count, world_wrap_horizontal, world_octaves, world_noise_divisor, world_horizontal_stretch)
regions = get_region_info(region_map_np, world_width, world_height, region_seeds, world_wrap_horizontal)
with_oceans_np = create_oceans(region_map_np, regions, ocean_zone_count, math.floor(ocean_zone_count * ocean_ratio))
mountains_map_np = create_mountains(with_oceans_np, region_map_np, regions, world_wrap_horizontal)
with_islands_np = create_islands(mountains_map_np, world_wrap_horizontal)

colors = ['#3498DB', '#3498DB', '#3498DB', '#DC7633', '#8c564b', '#4CAF50', '#8BC34A', '#A1887F']
cmap = ListedColormap(colors)
boundaries = list(range(len(colors) + 1))
norm = BoundaryNorm(boundaries, cmap.N, clip=True)

plt.figure(figsize=(10, 10))
plt.imshow(with_islands_np, cmap=cmap, norm=norm)
plt.title('')
plt.show()