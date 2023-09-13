from Obsoleted.PythonProofOfConcept.ecosystems import Region
from noisy_voronoi import noisy_voronoi
from lcg import LCG


def generate_seeds(spritesheet, region_definitions, width, height, voronoi_cell_count, rng_seed_x, rng_seed_y, rng_seed_chooser):
    lcg_x = LCG(rng_seed_x)
    lcg_y = LCG(rng_seed_y)
    lcg_chooser = LCG(rng_seed_chooser)
    seeds = []
    
    half_width = width / 2
    half_height = height / 2    

    for _ in range(voronoi_cell_count):
        choice = int(lcg_chooser.random_range(0, len(region_definitions)))
        a = lcg_x.random_range(-half_width, half_width)
        b = lcg_y.random_range(-half_height, half_height)
        c = region_definitions[choice][1]
        d = spritesheet.get_index(region_definitions[choice][0])
        
        seeds.append((a, b, c, d))

    return seeds


def fill_chunk(seeds, x, y, size, noise):
    return noisy_voronoi(noise, seeds, x, y, size, size)
