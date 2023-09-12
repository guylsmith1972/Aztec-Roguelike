import bidict
import json
import math
import os
import pygame

from gpu_texture import Texture
from PIL import Image


class SpriteSheet:
    def __init__(self, directory, tile_width=32, tile_height=32):
        self.directory = directory
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.sheet_map = bidict.bidict(json.load(open(f'{directory}/spritemap.json', 'r')))
        self.sheet_path = self._find_or_create_sheet()
        self.sheet_image = pygame.image.load(self.sheet_path)
        pil_image = Image.frombytes("RGBA", self.sheet_image.get_size(), pygame.image.tostring(self.sheet_image, "RGBA"))
        self.texture = Texture({"type": "image", "data": pil_image}, wrap_s='clamp', wrap_t='clamp')

    def cleanup(self):
        self.texture.cleanup()

    def _create_image_grid(self, directory, output_path):
        # Step 1: Collect all image paths in the directory
        image_paths = [os.path.join(f'{directory}/originals', f) for f in os.listdir(f'{directory}/originals') if f.endswith(('.png', '.jpg', '.jpeg'))]
    
        # Step 2: Load each image and scale it down
        scaled_images = [Image.open(path).resize((self.tile_width, self.tile_height)) for path in image_paths]
    
        # Step 3: Calculate the grid size
        num_images = len(scaled_images)
        cols = int(num_images**0.5)
        rows = num_images // cols + (1 if num_images % cols != 0 else 0)
    
        # Step 4: Create a blank image to paste the smaller images
        output_image = Image.new('RGB', (self.tile_width * cols, self.tile_height * rows))
    
        # Step 5: Paste each scaled-down image into the grid
        for i, img in enumerate(scaled_images):
            x = i % cols
            y = i // cols
            output_image.paste(img, (x * self.tile_width, y * self.tile_height))
    
        # Step 6: Save the final image
        output_image.save(output_path)
        
        # Step 7: Save the mapping to a JSON file
        filename_to_index = {}
        for i, path in enumerate(image_paths):
            filename_to_index[os.path.basename(path).split('.')[0]] = i
        with open(os.path.join(directory, 'spritemap.json'), 'w') as json_file:
            json.dump(filename_to_index, json_file, indent=2)

    def _find_or_create_sheet(self):
        # Check for an existing _sheet.png image
        for filename in os.listdir(self.directory):
            if filename == f'spritesheet_{self.tile_width}_{self.tile_height}.png':
                return os.path.join(self.directory, filename)

        # If no existing sheet, create a new one
        sheet_path = os.path.join(self.directory, f'spritesheet_{self.tile_width}_{self.tile_height}.png')
        self._create_image_grid(self.directory, sheet_path)
        return sheet_path

    def get_dimensions_in_tiles(self):
        # Get the total dimensions of the spritesheet image in pixels
        image_width, image_height = self.sheet_image.get_size()

        # Calculate the dimensions in tiles by dividing the total dimensions by the dimensions of each tile
        tiles_width = image_width // self.tile_width
        tiles_height = image_height // self.tile_height

        return (tiles_width, tiles_height)
    
    def get_index(self, tile_name):
        return self.sheet_map[tile_name] if tile_name in self.sheet_map else -1
    
    def get_name(self, tile_index):
        return self.sheet_map.inverse[tile_index]
    
    def get_all_terrain_names(self):
        return self.sheet_map.keys()

    def screen_to_world(self, screen, screen_x, screen_y, center_x, center_y):
        world_x = (screen_x - (screen.get_width() - self.tile_width) / 2) / self.tile_width + center_x
        world_y = (screen_y - (screen.get_height() - self.tile_height) / 2) / self.tile_height + center_y
        return math.floor(world_x), math.floor(world_y)
