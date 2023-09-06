from bidict import bidict
from matplotlib.colors import BoundaryNorm, ListedColormap, LinearSegmentedColormap
from native_code import generate_noisy_region_map, get_region_info, generate_heightmap, generate_regions_with_borders, find_river_paths
import configuration
import erosion
import gpu
import json
import math
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import utility


# Constants
topology = configuration.get(
    "topology",
    {
        "deep ocean": [0, -1, -0.9],
        "continental shelf": [1, -0.1, -0.09],
        "littoral": [2, -0.9, 0],
        "islands": [3, -0.9, 0],
        "land": [4, 0, 1],
        "lowlands": [5, 0.01, 0.3],
        "highlands": [6, 0.3, 0.6],
        "mountains": [7, 0.6, 1],
    },
)

ordered_topology = {i[0]: i for _, i in topology.items()}
print(json.dumps(ordered_topology, indent=2))
topology_codes = bidict({name: topology[name][0] for name in topology})

DEEP_OCEAN = topology_codes["deep ocean"]
CONTINENTAL_SHELF = topology_codes["continental shelf"]
LITTORAL = topology_codes["littoral"]
ISLANDS = topology_codes["islands"]
LAND = topology_codes["land"]
LOWLANDS = topology_codes["lowlands"]
HIGHLANDS = topology_codes["highlands"]
MOUNTAINS = topology_codes["mountains"]

world_width = configuration.get("world_width", 2048)
world_height = configuration.get("world_height", 1024)
world_zone_count = configuration.get("world_zone_count", 3000)
world_octaves = configuration.get("world_octaves", 4)
world_noise_divisor = configuration.get("world_noise_divisor", 100)
world_horizontal_stretch = configuration.get("world_horizontal_stretch", 1.5)

ocean_zone_count = configuration.get("ocean_zone_count", 30)
ocean_ratio = configuration.get("ocean_ratio", 0.55)
ocean_octaves = configuration.get("ocean_octaves", 2)
ocean_noise_divisor = configuration.get("ocean_noise_divisor", 100)
ocean_horizontal_stretch = configuration.get("ocean_horizontal_stretch", 1)

island_zone_count = configuration.get("island_zone_count", 150000)
island_survival_rate = configuration.get("island_survival_rate", 0.3)
island_octaves = configuration.get("island_octaves", 4)
island_noise_divisor = configuration.get("island_noise_divisor", 100)
island_horizontal_stretch = configuration.get("island_horizontal_stretch", 1)

mountain_zone_count = configuration.get("mountain_zone_count", 30)
mountain_survival_rate = configuration.get("mountain_survival_rate", 0.5)
mountain_octaves = configuration.get("mountain_octaves", 1)
mountain_noise_divisor = configuration.get("mountain_noise_divisor", 20)
mountain_horizontal_stretch = configuration.get("mountain_horizontal_stretch", 1)
hills_cutoff_top = configuration.get("hills_cutoff_top", 0.8)
mountain_cutoff_top = configuration.get("mountain_cutoff_top", 0.6)
mountain_cutoff_bottom = configuration.get("mountain_cutoff_bottom", 0.4)
hills_cutoff_bottom = configuration.get("hills_cutoff_bottom", 0.2)


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
    ocean_map_np, _ = make_map(
        ocean_zone_count,
        ocean_octaves,
        ocean_noise_divisor,
        ocean_horizontal_stretch,
    )

    ocean_remap = []
    for i in range(world_cells):
        ocean_remap.append(1 if i < ocean_count else 0)

    remapped_ocean = transform_array(ocean_map_np, ocean_remap)

    histogram = histogram_of_ones(regions, ownership_np, remapped_ocean)

    continental_shelf_cutoff = configuration.get("continental_shelf_cutoff", 0.25)
    islands_cutoff = configuration.get("islands_cutoff", 0.05)

    world_remap = []
    for region_id, region in regions.items():
        ocean_type = None
        coverage = histogram[region_id]
        if coverage > 0:
            percentage = coverage / region["area"]
            if percentage == 1:
                ocean_type = DEEP_OCEAN
            elif percentage >= continental_shelf_cutoff:
                ocean_type = CONTINENTAL_SHELF
            elif percentage > islands_cutoff:
                ocean_type = LITTORAL
            else:
                ocean_type = ISLANDS
            region["category"] = topology_codes.inverse[ocean_type]
        new_value = LAND if ocean_type is None else ocean_type
        world_remap.append(new_value)

    return transform_array(ownership_np, world_remap)


def create_islands(coverage_map_np):
    island_map_np, island_seeds = make_map(
        island_zone_count,
        island_octaves,
        island_noise_divisor,
        island_horizontal_stretch,
    )
    
    island_remap = []
    max_index = math.floor(island_zone_count * island_survival_rate)
    for i in range(island_zone_count):
        island_remap.append(LAND if i < max_index else LITTORAL)

    # Contains 1 for islands, 0 for not-islands
    remapped_islands = transform_array(island_map_np, island_remap)

    return np.where(coverage_map_np == ISLANDS, remapped_islands, coverage_map_np)


def create_mountains(coverage_map_np, ownership_map, regions):
    mountain_zones_np, _ = make_map(
        mountain_zone_count,
        mountain_octaves,
        mountain_noise_divisor,
        mountain_horizontal_stretch,
    )

    mountain_remap = []
    mountain_survivors = math.floor(mountain_zone_count * mountain_survival_rate)
    for i in range(mountain_zone_count):
        mountain_remap.append(1 if i < mountain_survivors else 0)

    remapped_mountains = transform_array(mountain_zones_np, mountain_remap)

    histogram = histogram_of_ones(regions, ownership_map, remapped_mountains)

    world_remap = []
    for region_id, region in regions.items():
        land_type = coverage_map_np[region["seed"][1]][region["seed"][0]]
        if land_type == LAND:
            coverage = histogram[region_id]
            # print(f'coverage: {coverage}, area: {region["area"]}')
            percentage = coverage / region["area"]
            if percentage > hills_cutoff_top:
                land_type = LOWLANDS
            elif percentage > mountain_cutoff_top:
                land_type = HIGHLANDS
            elif percentage > mountain_cutoff_bottom:
                land_type = MOUNTAINS
            elif percentage > hills_cutoff_bottom:
                land_type = HIGHLANDS
            else:
                land_type = LOWLANDS
            region["category"] = topology_codes.inverse[land_type]

        world_remap.append(land_type)

    return transform_array(ownership_map, world_remap)


def make_map(seed_count, octaves, noise_divisor, horizontal_stretch):
    seeds = [
        (np.random.randint(0, world_width), np.random.randint(0, world_height))
        for _ in range(seed_count)
    ]
    weights = list(np.random.uniform(1.2, 1.6, seed_count))

    # Call the wrapper function
    map_np = generate_noisy_region_map(
        world_width,
        world_height,
        seeds,
        weights,
        octaves,
        noise_divisor,
        horizontal_stretch,
    )
    return map_np, seeds


def rotate_map(coverage_map_np, international_date_line=None):
    if international_date_line is None:
        ocean_histogram = np.sum(coverage_map_np < LAND, axis=0)
        n = utility.max_index_with_neighboring_avg(ocean_histogram, window_size=100)
    else:
        n = international_date_line

    _, cols = coverage_map_np.shape
    new_cols = (np.arange(cols) + n) % world_width
    rotated_map = coverage_map_np[:, new_cols]
    return np.ascontiguousarray(rotated_map), n


def custom_colormap(color_key):
    # Convert HEX colors to RGB tuples
    colors = [(value, hex_to_rgb(color)) for value, color in color_key]
    
    # Create a colormap
    cmap = LinearSegmentedColormap.from_list("custom", colors, N=256)
    
    return cmap

def hex_to_rgb(hex_color):
    # Convert HEX color to RGB tuple
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))


def add_figure(name, data, cmap, vmin=0, vmax=1, norm=None):
    plt.figure(name)
    if norm is None:
        plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    else:
        plt.imshow(data, cmap=cmap, norm=norm)
    # plt.title = name
    plt.colorbar() 
    

def print_array_order(arr, name):
    if arr.flags['C_CONTIGUOUS']:
        print(f"The array {name} is in C-order (row-major).")
    elif arr.flags['F_CONTIGUOUS']:
        print(f"The array {name} is in Fortran-order (column-major).")
    else:
        print(f"The array {name} has a non-standard memory layout.")


def normalize_to_minus1_1(arr):
    x_min = np.min(arr)
    x_max = np.max(arr)
    
    # Handle the case where x_min == x_max to prevent division by zero
    if x_min == x_max:
        return np.full_like(arr, 1.0) if x_max > 0 else np.full_like(arr, -1.0)
    
    m = 2 / (x_max - x_min)
    c = (x_max + x_min) / (x_max - x_min)
    
    return m * arr - c


def main():
    display = gpu.initialize_opengl_context(100, 100);
    
    region_map_np, region_seeds = make_map(
        world_zone_count,
        world_octaves,
        world_noise_divisor,
        world_horizontal_stretch,
    )
    regions = get_region_info(
        region_map_np, world_width, world_height, region_seeds
    )
    with_oceans_np = create_oceans(
        region_map_np,
        regions,
        ocean_zone_count,
        math.floor(ocean_zone_count * ocean_ratio),
    )
    mountains_map_np = create_mountains(
        with_oceans_np, region_map_np, regions
    )
    with_islands_np = create_islands(mountains_map_np)

    with_islands_np, international_date_line = rotate_map(with_islands_np)
    with_oceans_np, _ = rotate_map(with_oceans_np, international_date_line)
    region_map_np, _ = rotate_map(region_map_np, international_date_line)
    
    water_land_coverage_np = transform_array(with_islands_np, [0, 0, 0, 0, 1, 1, 1, 1])
    
    low_altitude_np = transform_array(with_islands_np, [ordered_topology[key][1] for key in sorted(ordered_topology.keys())])
    high_altitude_np = transform_array(with_islands_np, [ordered_topology[key][2] for key in sorted(ordered_topology.keys())])

    blurred_low_altitude_np = utility.gaussian_blur(low_altitude_np, 7)
    blurred_high_altitude_np = utility.gaussian_blur(high_altitude_np, 7)

    _, low_frequency_heightmap = generate_regions_with_borders(water_land_coverage_np, 2, world_width, world_height, 8, 20, 1)
    _, high_frequency_heightmap = generate_regions_with_borders(region_map_np, len(region_seeds), world_width, world_height, 8, 20, 1)
    
    normalized_heightmap = blurred_low_altitude_np + (blurred_high_altitude_np - blurred_low_altitude_np) * (low_frequency_heightmap + high_frequency_heightmap) / 2;

    black_white_cmap = custom_colormap([[0, '#000000'], [1.0, '#ffffff']])
    full_colors_cmap = custom_colormap([[0, '#3498DB'], [0.49999999, '#3498DB'],  [0.5, '#4CAF50'], [0.65, '#8BC34A'], [0.8, '#A1887F'], [1.0, '#ffffff']])
    
    add_figure('low_altitude_np', low_altitude_np, full_colors_cmap, vmin=-1, vmax=1)
    add_figure('high_altitude_np', high_altitude_np, full_colors_cmap, vmin=-1, vmax=1)
    add_figure('blurred_low_altitude_np', blurred_low_altitude_np, full_colors_cmap, vmin=-1, vmax=1)
    add_figure('blurred_high_altitude_np', blurred_high_altitude_np, full_colors_cmap, vmin=-1, vmax=1)
    
    add_figure('low_frequency_heightmap', low_frequency_heightmap, black_white_cmap)
    add_figure('high_frequency_heightmap', high_frequency_heightmap, black_white_cmap)
    add_figure('normalized_heightmap', normalized_heightmap, full_colors_cmap, vmin=-1, vmax=1)

    normalized_rivers = find_river_paths(normalized_heightmap)
    
    add_figure('normalized_rivers', normalized_rivers, black_white_cmap)
    
    colors = ['#3498DB', '#DC7633']
    colors_cmap = ListedColormap(colors)
    boundaries = list(range(len(colors) + 1))
    norm = BoundaryNorm(boundaries, colors_cmap.N, clip=True)
    add_figure('water_land_coverage_np', water_land_coverage_np, colors_cmap, norm=norm)

    altitude_multiplier = 1

    bedrock = (normalized_heightmap + 1) / 2 * altitude_multiplier
    sediment = np.full(bedrock.shape, 0.01) * altitude_multiplier
    water_level = np.full(bedrock.shape, 0.001) * altitude_multiplier
    suspended_sediment = np.full(bedrock.shape, 0.001) * altitude_multiplier
    
    modified_normalized_heights = normalized_heightmap + sediment + suspended_sediment
    
    for i in range(20):
        print('-' * 80)
        print(f'iteration # {i}')
        print(f'bedrock sum: {np.sum(bedrock)} -- contains NaN: {np.any(np.isnan(bedrock))}')
        print(f'sediment sum: {np.sum(sediment)} -- contains NaN: {np.any(np.isnan(sediment))}')
        print(f'water_level sum: {np.sum(water_level)} -- contains NaN: {np.any(np.isnan(water_level))}')
        print(f'suspended_sediment sum: {np.sum(suspended_sediment)} -- contains NaN: {np.any(np.isnan(suspended_sediment))}')
        print(f'total sediment: {np.sum(sediment) + np.sum(suspended_sediment)}')
        
        if np.any(np.isnan(suspended_sediment)):
            break

        bedrock, sediment, water_level, suspended_sediment = erosion.erode(bedrock, sediment, water_level, suspended_sediment, iterations=500)

    bedrock /= altitude_multiplier
    sediment /= altitude_multiplier
    water_level /= altitude_multiplier
    suspended_sediment /= altitude_multiplier
    
    eroded_heightmap = bedrock + sediment + suspended_sediment
    print(f'min eroded height value is {np.min(eroded_heightmap)}')
    print(f'max eroded height value is {np.max(eroded_heightmap)}')
    eroded_heightmap = (eroded_heightmap - np.min(eroded_heightmap)) * (2.0 / (np.max(eroded_heightmap) - np.min(eroded_heightmap))) - 1
    # eroded_heightmap = normalize_to_minus1_1(eroded_heightmap)

    add_figure('eroded_heightmap', eroded_heightmap, full_colors_cmap, vmin=-1, vmax=1)
    add_figure('eroded_heightmap_bw', eroded_heightmap, black_white_cmap, vmin=np.min(eroded_heightmap), vmax=np.max(eroded_heightmap))
    add_figure('suspended_sediment', suspended_sediment, black_white_cmap, vmin=np.min(suspended_sediment), vmax=np.max(suspended_sediment))
    
    add_figure('sediment', sediment, black_white_cmap, vmin=np.min(sediment), vmax=np.max(sediment))
    add_figure('water_level', water_level, black_white_cmap, vmin=np.min(water_level), vmax=np.max(water_level))

    eroded_rivers = find_river_paths(eroded_heightmap)
    add_figure('eroded_rivers', eroded_rivers, black_white_cmap)
    
    delta_height = eroded_heightmap - modified_normalized_heights
    add_figure('delta_height', delta_height, black_white_cmap, vmin=-1)

    plt.show()


if __name__ == "__main__":
    main()
