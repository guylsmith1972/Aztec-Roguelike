# from noise import get_noise
from native_code import generate_noise
from spritesheet import SpriteSheet
from terrain_generator import generate_seeds, fill_chunk
import configuration
import gpu
import plotting as plt


def main():
    display = gpu.initialize_opengl_context(100, 100);
    spritesheet = SpriteSheet(configuration.get('spritesheets.terrain', 'Assets/Terrain'), 8, 8)
    region_definitions = configuration.get('world.generator.cells.weights', [
        ('dirt', 0.3),
        ('granite', 9),
        ('grass', 9),
        ('grass-thick', 2),
        ('stones-small', 2),
        ('stones-medium', 2)
    ])
    
    voronoi_cell_count = 10000
    view_size = 512

    noise = generate_noise(1024, 5, 1, 42)
    
    seeds = generate_seeds(spritesheet, region_definitions, 10000, 10000, voronoi_cell_count, 234, 266, 6437)

    locality, _ = fill_chunk(seeds, 1064, 0, view_size, noise)

    black_white_cmap = plt.custom_colormap([[0, '#000000'], [1.0, '#ffffff']])
    
    plt.add_figure('noise', noise, cmap=black_white_cmap, vmin=0, vmax=1)
    plt.add_figure('locality', locality, cmap='tab20', vmin=0, vmax=6)
    plt.show_plots()


if __name__ == '__main__':
    main()
    