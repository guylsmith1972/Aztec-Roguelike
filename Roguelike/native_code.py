
import numpy as np
import ctypes

# Load the DLL
_dll = ctypes.CDLL("./AztecClientBL.dll") 

# Define the Point structure for the seeds
class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

# Define the function signature
_dll.iterative_voronoi.restype = ctypes.POINTER(ctypes.c_int)
_dll.iterative_voronoi.argtypes = [
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(Point), ctypes.c_int,
    ctypes.POINTER(ctypes.c_double)
]
_dll.free_voronoi_map.argtypes = [ctypes.POINTER(ctypes.c_int)]

def generate_voronoi_map(left, top, width, height, seeds, weights):
    """Generate a Voronoi map using the provided DLL.
    
    Parameters:
    - left, top, width, height: Dimensions of the area.
    - seeds: List of seed points as (x, y) tuples.
    - weights: List of weights for each seed.
    
    Returns:
    - numpy array representing the Voronoi map.
    """
    seed_count = len(seeds)
    
    # Convert seeds and weights to ctypes structures
    seed_array = (Point * seed_count)(*[Point(s[0], s[1]) for s in seeds])
    weights_array = (ctypes.c_double * seed_count)(*weights)
    
    # Call the DLL function
    voronoi_map_ptr = _dll.iterative_voronoi(left, top, width, height, seed_array, seed_count, weights_array)
    
    # Convert the voronoi_map_ptr to a numpy array
    voronoi_map_np = np.zeros((height, width), dtype=np.int32)
    for y in range(height):
        for x in range(width):
            voronoi_map_np[y, x] = voronoi_map_ptr[y * width + x]
    
    # Free the allocated memory
    _dll.free_voronoi_map(voronoi_map_ptr)
    
    return voronoi_map_np
