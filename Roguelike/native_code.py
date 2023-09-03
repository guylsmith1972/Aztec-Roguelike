
import math
import random
import numpy as np
import ctypes

# Load the DLL
_dll = ctypes.CDLL("./AztecClientBL.dll") 

# Define the Point structure
class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

# Define the function signature for generate_regions
_dll.generate_regions.restype = ctypes.POINTER(ctypes.c_int)
_dll.generate_regions.argtypes = [
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(Point), ctypes.c_int,
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_int,
    ctypes.c_int, ctypes.c_double,
    ctypes.c_double
]

# Define the RegionInfo structure 
class RegionInfo(ctypes.Structure):
    _fields_ = [
        ("area", ctypes.c_int),
        ("neighbors", ctypes.c_int * 20),
        ("neighbor_count", ctypes.c_int)
    ]

# Set up the function signature for calculate_region_info from the DLL
_dll.calculate_region_info.restype = ctypes.POINTER(RegionInfo)
_dll.calculate_region_info.argtypes = [
    ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
]


# Define the function signature for remap
_dll.remap.restype = ctypes.POINTER(ctypes.c_int)
_dll.remap.argtypes = [
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), 
    ctypes.c_int
]


def convert_1d_to_numpy_2d(one_dee, width, height):
    two_dee_np = np.zeros((height, width), dtype=np.int32)
    for y in range(height):
        for x in range(width):
            two_dee_np[y, x] = one_dee[y * width + x]
            
    return two_dee_np


def generate_noisy_region_map(left, top, width, height, seeds, weights, wrap_horizontal, octaves, noise_divisor, horizontal_stretch):
    seed_count = len(seeds)
    
    # Convert seeds and weights to ctypes structures
    seed_array = (Point * seed_count)(*[Point(s[0], s[1]) for s in seeds])
    weights_array = (ctypes.c_double * seed_count)(*weights)
    
    # Call the DLL function
    voronoi_map_ptr = _dll.generate_regions(left, top, width, height, seed_array, seed_count, weights_array, wrap_horizontal, octaves, noise_divisor, horizontal_stretch)
    
    # Convert the voronoi_map_ptr to a numpy array
    voronoi_map_np = convert_1d_to_numpy_2d(voronoi_map_ptr, width, height)
    
    # Free the allocated memory
    _dll.free_array_1d(voronoi_map_ptr)
    
    return voronoi_map_np

def get_region_info(ownership, width, height, seeds, wrap_horizontal):
    seed_count = len(seeds)
    
    # Call the DLL function
    region_info_ptr = _dll.calculate_region_info(ownership.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), 
                                                 width, height, seed_count, wrap_horizontal)
    
    # Process the output to convert it into a Python-friendly format
    region_info_list ={}
    for i in range(seed_count):
        region = region_info_ptr[i]
        region_info_list[i] = {
            "seed": seeds[i],
            "area": region.area,
            "neighbors": [region.neighbors[j] for j in range(region.neighbor_count)],
            "category": None
        }
    
    _dll.free_array_1d(region_info_ptr)
    
    return region_info_list
