
import math
import random
import numpy as np
import ctypes

# Load the DLL
dll = ctypes.CDLL("./AztecClientBL.dll") 

import ctypes

# Define the constants and structures as per the provided definitions
MAX_NEIGHBORS = 20

class Location(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int),
                ("y", ctypes.c_int)]

class RegionInfo(ctypes.Structure):
    _fields_ = [("area", ctypes.c_int),
                ("neighbors", ctypes.c_int * MAX_NEIGHBORS),
                ("neighbor_count", ctypes.c_int)]

# Define function prototypes
dll.generate_regions.argtypes = [
    ctypes.c_int,  # width
    ctypes.c_int,  # height
    ctypes.POINTER(Location), # seeds
    ctypes.c_int,  # seed_count
    ctypes.POINTER(ctypes.c_float),  # weights
    ctypes.c_int,  # octaves
    ctypes.c_float,  # noise_divisor
    ctypes.c_float,  # horizontal_stretch
    ctypes.POINTER(ctypes.c_int),  # ownership
    ctypes.POINTER(ctypes.c_float)  # distances
]

dll.generate_regions_with_borders.argtypes = [
    ctypes.POINTER(ctypes.c_int),  # ownership
    ctypes.c_int,  # num_owners
    ctypes.c_int,  # width
    ctypes.c_int,  # height
    ctypes.c_int,  # octaves
    ctypes.c_float,  # noise_divisor
    ctypes.c_float,  # horizontal_stretch
    ctypes.POINTER(ctypes.c_float),  # distances
    ctypes.POINTER(ctypes.c_float)  # normalized
]
        

dll.generate_heightmap.argtypes = [
    ctypes.POINTER(ctypes.c_float),  # minimum_values
    ctypes.POINTER(ctypes.c_float),  # maximum_values
    ctypes.c_int,  # width
    ctypes.c_int,  # height
    ctypes.c_int,  # octaves
    ctypes.c_float,  # noise_divisor
    ctypes.POINTER(ctypes.c_float)  # heightmap
]

dll.calculate_region_info.argtypes = [
    ctypes.POINTER(ctypes.c_int),  # ownership
    ctypes.c_int,  # width
    ctypes.c_int,  # height
    ctypes.c_int  # seed_count
]
dll.calculate_region_info.restype = ctypes.POINTER(RegionInfo)

dll.find_river_paths.argtypes = [
    ctypes.POINTER(ctypes.c_float),  # heightmap
    ctypes.c_int,                    # width
    ctypes.c_int,                    # height
    ctypes.POINTER(ctypes.c_int)     # water_volume
]

dll.find_river_paths.argtypes = [
    ctypes.POINTER(ctypes.c_float),  # float* heights
    ctypes.c_int,                    # int width
    ctypes.c_int,                    # int height
    ctypes.POINTER(ctypes.c_float)   # float* water_volume
]

dll.remap.argtypes = [
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_int
]
dll.remap.restype = ctypes.POINTER(ctypes.c_int)

dll.free_array_1d.argtypes = [ctypes.POINTER(ctypes.c_int)]

dll.free_region_info_array.argtypes = [ctypes.POINTER(RegionInfo)]


# Helper function remains unchanged
def convert_1d_to_numpy_2d(one_dee, width, height):
    two_dee_np = np.zeros((height, width), dtype=np.int32)
    for y in range(height):
        for x in range(width):
            two_dee_np[y, x] = one_dee[y * width + x]
            
    return two_dee_np

# Updated to reflect new function signature and float type
def generate_noisy_region_map(width, height, seeds, weights, octaves, noise_divisor, horizontal_stretch):
    seed_count = len(seeds)
    
    seed_array = (Location * seed_count)(*[Location(s[0], s[1]) for s in seeds])
    weights_array = (ctypes.c_float * seed_count)(*weights)
    
    ownership_array = (ctypes.c_int * (width * height))()
    distances_array = (ctypes.c_float * (width * height))()

    dll.generate_regions(width, height, seed_array, seed_count, weights_array, octaves, noise_divisor, horizontal_stretch, ownership_array, distances_array)
    
    voronoi_map_np = convert_1d_to_numpy_2d(ownership_array, width, height)

    # In this case, we don't free the ownership_array and distances_array because they are managed by Python's garbage collector
    
    return voronoi_map_np

# This function remains mostly unchanged
def get_region_info(ownership, width, height, seeds):
    seed_count = len(seeds)
    
    region_info_ptr = dll.calculate_region_info(ownership.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), width, height, seed_count)
    
    region_info_list = {}
    for i in range(seed_count):
        region = region_info_ptr[i]
        region_info_list[i] = {
            "seed": seeds[i],
            "area": region.area,
            "neighbors": [region.neighbors[j] for j in range(region.neighbor_count)],
            "category": None
        }
    
    dll.free_region_info_array(region_info_ptr)
    
    return region_info_list

# Updated to reflect float type
def generate_heightmap(minimum_altitudes, maximum_altitudes, width, height, octaves, noise_divisor):
    min_vals_flat = minimum_altitudes.flatten().astype(np.float32)
    max_vals_flat = maximum_altitudes.flatten().astype(np.float32)
    
    output = np.zeros((width * height,), dtype=np.float32)

    dll.generate_heightmap(
        min_vals_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        max_vals_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        width,
        height,
        octaves,
        noise_divisor,
        output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    )
    
    output = output.reshape((height, width))
    
    return output

def generate_regions_with_borders(ownership, num_owners, width, height, octaves, noise_divisor, horizontal_stretch):
    # Create arrays to hold the output data
    distances = np.zeros((width * height,), dtype=np.float32)
    normalized = np.zeros((width * height,), dtype=np.float32)

    # Call the DLL function
    dll.generate_regions_with_borders(
        ownership.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        num_owners,
        width,
        height,
        octaves,
        ctypes.c_float(noise_divisor),
        ctypes.c_float(horizontal_stretch),
        distances.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        normalized.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    )

    return distances.reshape((height, width)), normalized.reshape((height, width))

def find_river_paths(heights):
    # Convert the input heightmap to a numpy array with float32 type (which corresponds to float in C++)
    heights_np = np.array(heights, dtype=np.float32)

    # Get the width and height of the heightmap
    height, width = heights_np.shape

    # Create an empty water_volume array initialized to zero
    water_volume_np = np.zeros((height, width), dtype=np.float32)

    # Call the C++ function
    dll.find_river_paths(
        heights_np.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        width,
        height,
        water_volume_np.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    )

    return water_volume_np
