import numpy as np


def normalize_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    
    normalized_arr = (arr - min_val) / (max_val - min_val)
    return normalized_arr


def get_noise(size, roughness, initial_value):
    # Initialize grid with NaN values
    grid = np.full((size, size), np.nan)
    
    # Set initial corner value
    grid[0, 0] = initial_value

    step = size

    while step > 1:
        half_step = step // 2

        # Diamond step with wrapping
        for x in range(0, size, step):
            for y in range(0, size, step):
                avg = (grid[x, y] + grid[(x+step)%size, y] + grid[x, (y+step)%size] + grid[(x+step)%size, (y+step)%size]) / 4.0
                grid[(x+half_step)%size, (y+half_step)%size] = avg + (np.random.rand() - 0.5) * roughness * step

        # Square step with wrapping
        for x in range(0, size, half_step):
            for y in range((x + half_step) % step, size, step):  # Offset to avoid overwriting diamond centers
                total = grid[(x - half_step) % size, y] \
                      + grid[(x + half_step) % size, y] \
                      + grid[x, (y - half_step) % size] \
                      + grid[x, (y + half_step) % size]

                avg = total / 4
                grid[x, y] = avg + (np.random.rand() - 0.5) * roughness * step

        step //= 2

    return normalize_array(grid)
