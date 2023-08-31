import numpy as np
import matplotlib.pyplot as plt
import ctypes

# Load the DLL
dll = ctypes.CDLL("./AztecClientBL.dll") 

# Define the Point structure for the seeds
class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

# Define the function signature
dll.iterative_voronoi.restype = ctypes.POINTER(ctypes.c_int)
dll.iterative_voronoi.argtypes = [
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(Point), ctypes.c_int,
    ctypes.POINTER(ctypes.c_double)
]

# Constants
WIDTH, HEIGHT = 400, 200
SEED_COUNT = 15
LEFT, TOP = 500, 500

# Generate seeds and their weights
seed_array = (Point * SEED_COUNT)(*[Point(LEFT + np.random.randint(0, WIDTH), TOP + np.random.randint(0, HEIGHT)) for _ in range(SEED_COUNT)])
weights_np = np.random.uniform(0.8, 1.2, SEED_COUNT)
weights_array = (ctypes.c_double * SEED_COUNT)(*weights_np)

# Call the DLL function
voronoi_map_ptr = dll.iterative_voronoi(LEFT, TOP, WIDTH, HEIGHT, seed_array, SEED_COUNT, weights_array)

# Convert the voronoi_map_ptr to a numpy array
voronoi_map_np = np.zeros((HEIGHT, WIDTH), dtype=np.int32)
for y in range(HEIGHT):
    for x in range(WIDTH):
        voronoi_map_np[y, x] = voronoi_map_ptr[y * WIDTH + x]

# Free the allocated memory
dll.free_voronoi_map(voronoi_map_ptr)

# Plot
plt.figure(figsize=(10, 10))
plt.imshow(voronoi_map_np, cmap='tab20')
plt.title('Weight-Influenced Voronoi Diagram')
plt.show()

