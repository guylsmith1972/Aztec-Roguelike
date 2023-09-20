from noisy_voronoi import noisy_voronoi
from lcg import LCG
from lru_cache import LRUCache

import configuration


_seed_cache = LRUCache(capacity = configuration.get('world.generator.region.seeds.cache.capacity', 100))

def generate_seeds(spritesheet, x, y):
    region_width = configuration.get('world.generator.region.size.width', 512)
    region_height = configuration.get('world.generator.region.size.height', 512)
    x -= x % region_width
    y -= y % region_height

    global _seed_cache
    cached_result = _seed_cache.get((x, y))
    if cached_result:
        return cached_result

    region_definitions = configuration.get('world.generator.cells.weights', [
        ('dirt', 4),
        ('granite', 5),
        ('grass', 1),
        ('grass-thick', 1),
        ('stones-small', 5),
        ('stones-medium', 5)
    ])
    
    remapped_regions = [spritesheet.get_index(region_definitions[choice][0]) for choice in range(len(region_definitions))]

    seeds_per_region = configuration.get('world.generator.region.seed_count', 4)
    rng_seed_a = configuration.get('world.generator.random.seed.a', 42)
    rng_seed_b = configuration.get('world.generator.random.seed.b', 43)
    rng_seed_c = configuration.get('world.generator.random.seed.c', 44)

    seeds = []
    for dy in [-2, -1, 0, 1, 2]:
        yy = y + dy * region_height
        lcg_y = LCG(yy + rng_seed_a)
        y_seed = lcg_y.random_range(0, 0x7fffffff)
        for dx in [-2, -1, 0, 1, 2]:
            xx = x + dx * region_width
            lcg_x = LCG(xx + rng_seed_b)
            x_seed = lcg_x.random_range(0, 0x7fffffff)
            combined_seed = int(x_seed) ^ int(y_seed) ^ int(rng_seed_c)
            lcg = LCG(combined_seed)
            for _ in range(seeds_per_region):
                choice = int(lcg.random_range(0, len(region_definitions)))
                a = lcg.random_range(xx, xx + region_width)
                b = lcg.random_range(yy, yy + region_height)
                c = region_definitions[choice][1]
                d = remapped_regions[choice]
                seeds.append((a, b, c, d))
    _seed_cache.put((x, y), seeds)
    return seeds


def fill_chunk(seeds, x, y, size, noise):
    return noisy_voronoi(noise, seeds, x, y, size, size, noise_multiplier=1)
