import numpy as np
import matplotlib.pyplot as plt
from native_code import generate_noisy_voronoi_map

# Constants
WIDTH, HEIGHT = 1024, 1024
SEED_COUNT = 70
LEFT, TOP = 500, 500

# Generate seeds and their weights
seeds = [(LEFT + np.random.randint(0, WIDTH), TOP + np.random.randint(0, HEIGHT)) for _ in range(SEED_COUNT)]
weights = list(np.random.uniform(0.8, 1.2, SEED_COUNT))

# Call the wrapper function
voronoi_map_np = generate_noisy_voronoi_map(LEFT, TOP, WIDTH, HEIGHT, seeds, weights)

# Plot
plt.figure(figsize=(10, 10))
plt.imshow(voronoi_map_np, cmap='tab20')
plt.title('')
plt.show()
