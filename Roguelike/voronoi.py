import math
import random
import numpy as np
import matplotlib.pyplot as plt
import opensimplex

# Constants
WIDTH, HEIGHT = 200, 200
SEED_COUNT = 50


def iterative_voronoi(width, height, seeds, weights):
    ownership = np.zeros((height, width))
    distances = np.zeros((height, width))
    pending = set()
    
    def get_weakest_neighbor(x, y):        
        weakest = ( 100000, (-1, -1))
        for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            dx = d[0]
            dy = d[1]
            xx = x + dx
            if xx < 0 or xx >= width:
                continue
            yy = y + dy
            if yy < 0 or yy >= height:
                continue
            distance = distances[yy][xx]
            if distance == 0:
                continue
            if distance < weakest[0]:
                weakest = (distance, (xx, yy))
        return weakest

    def add_neighbors(x, y):
        reference_distance = distances[y][x]
        for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            dx = d[0]
            dy = d[1]
            xx = x + dx
            if xx < 0 or xx >= width:
                continue
            yy = y + dy
            if yy < 0 or yy >= height:
                continue
            distance = distances[yy][xx]
            if distance == 0 or distance > reference_distance:
                pending.add((xx, yy))

    for index in range(len(seeds)):
        seed = seeds[index]
        ownership[seed[1]][seed[0]] = index
        distances[seed[1]][seed[0]] = 1
        add_neighbors(seed[0], seed[1])

    count = 0
    while len(pending) > 0 and count < 1000000:
        candidate = pending.pop()
        weakest = get_weakest_neighbor(*candidate)
        if weakest[1][0] == -1 or weakest[1][1] == -1:
            continue
        owner = ownership[weakest[1][1]][weakest[1][0]]
        delta = weights[int(owner)] * random.random()
        distances[candidate[1]][candidate[0]] = weakest[0] + delta
        ownership[candidate[1]][candidate[0]] = owner
        add_neighbors(*candidate)
        count += 1
    
    print(f'ending count: {count}')

    return ownership

# Generate Voronoi diagram influenced only by weights
def weight_influenced_voronoi(width, height, seeds, weights):
    image = np.zeros((width, height))
    for x in range(width):
        for y in range(height):
            distances = [np.linalg.norm(np.array((x, y)) - np.array(seed)) * weight for seed, weight in zip(seeds, weights)]
            image[x, y] = np.argmin(distances)
    return image

# Generate seeds and their weights
np.random.seed(42)  # for reproducibility
seeds = [(np.random.randint(0, WIDTH), np.random.randint(0, HEIGHT)) for _ in range(SEED_COUNT)]
weights = [np.random.uniform(0.8, 1.2) for _ in range(SEED_COUNT)]

# Generate Voronoi diagram
voronoi_map = iterative_voronoi(WIDTH, HEIGHT, seeds, weights)

# Plot
plt.figure(figsize=(10, 10))
plt.imshow(voronoi_map, cmap='tab20')
# plt.scatter(*zip(*seeds), c='red')
plt.title('Weight-Influenced Voronoi Diagram')
plt.show()
