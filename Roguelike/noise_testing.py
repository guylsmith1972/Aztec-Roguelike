# from noise import get_noise
from native_code import generate_noise
from noisy_voronoi import noisy_voronoi
import gpu
import plotting as plt
import random
import time


def generate_seeds(n):
    result = []
    
    for _ in range(n):
        a = random.randint(-5000, 6000)
        b = random.randint(-5000, 6000)
        c = random.uniform(1, 2)
        d = random.uniform(0.75, 0.9)
        
        result.append((a, b, c, d))
    
    return result


def main():
    display = gpu.initialize_opengl_context(100, 100);
    print(f'Created display: {display}')
    
    seed_count = 10000
    view_size = 512    

    start_time = time.perf_counter()
    noise = generate_noise(1024, 5, 1, 42)
    end_time = time.perf_counter()
    
    noise_generation_time = end_time - start_time

    seeds = generate_seeds(seed_count)

    start_time = time.perf_counter()
    locality, trimmed_seeds = noisy_voronoi(noise, seeds, view_size, view_size, ((view_size-1) * 0.5, (view_size-1) * 0.5))
    end_time = time.perf_counter()
    
    voronoi_time = end_time - start_time
    
    print(f'noise generation: {noise_generation_time}')
    print(f'voronoi generation: {voronoi_time}')
    
    print(locality)

    black_white_cmap = plt.custom_colormap([[0, '#000000'], [1.0, '#ffffff']])
    
    plt.add_figure('noise', noise, cmap=black_white_cmap, vmin=0, vmax=1)
    plt.add_figure('locality', locality, cmap='tab20', vmin=0, vmax=len(trimmed_seeds)-1)
    plt.show_plots()


if __name__ == '__main__':
    main()
    