from noise import get_noise
from noisy_voronoi import noisy_voronoi
import gpu
import plotting as plt
import random


def generate_seeds(n=100):
    result = []
    
    for _ in range(n):
        a = random.randint(0, 1000)
        b = random.randint(0, 1000)
        c = random.uniform(0.5, 5)
        d = 1  # random.uniform(0, 1)
        
        result.append((a, b, c, d))
    
    return result

def main():
    display = gpu.initialize_opengl_context(100, 100);
    print(f'Created display: {display}')

    noise = get_noise(512, 1, 0.5)

    seeds = generate_seeds()
    
    locality = noisy_voronoi(noise, seeds, 1024, 1024)
    
    print(locality)

    black_white_cmap = plt.custom_colormap([[0, '#000000'], [1.0, '#ffffff']])
    
    plt.add_figure('noise', noise, cmap=black_white_cmap, vmin=0, vmax=1)
    plt.add_figure('locality', locality, cmap='tab20', vmin=0, vmax=99)
    plt.show_plots()


if __name__ == '__main__':
    main()
    