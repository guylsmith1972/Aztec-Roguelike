import bidict
import json
import math
import os
import pygame

from PIL import Image


class SpriteSheet:
    def __init__(self, directory, tile_width=32, tile_height=32):
        self.directory = directory
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.sheet_path = self._find_or_create_sheet()
        self.sheet_image = pygame.image.load(self.sheet_path)
        self.sheet_map = bidict.bidict(json.load(open(f'{directory}/spritemap.json', 'r')))

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
    
    def get_index(self, tile_name):
        return self.sheet_map[tile_name] if tile_name in self.sheet_map else -1
    
    def get_name(self, tile_index):
        return self.sheet_map.inverse[tile_index]

    def render(self, screen, tile_index, world_x, world_y, center_x, center_y):
        screen_x = (world_x - center_x) * self.tile_width + (screen.get_width() - self.tile_width) / 2
        screen_y = (world_y - center_y) * self.tile_height + (screen.get_height() - self.tile_height) / 2

        # Use blit_to_surface() to render the tile on the screen
        self.blit_to_surface(screen, tile_index, screen_x, screen_y)

    def blit_to_surface(self, surface, tile_index, x, y):
        cols = self.sheet_image.get_width() // self.tile_width
        row = tile_index // cols
        col = tile_index % cols

        # Determine the source rectangle for the tile
        source_rect = pygame.Rect(col * self.tile_width, row * self.tile_height, self.tile_width, self.tile_height)
    
        # Blit (copy) the tile from the sprite sheet onto the surface at the specified location
        surface.blit(self.sheet_image, (x, y), source_rect)

    def screen_to_world(self, screen, screen_x, screen_y, center_x, center_y):
        world_x = (screen_x - (screen.get_width() - self.tile_width) / 2) / self.tile_width + center_x
        world_y = (screen_y - (screen.get_height() - self.tile_height) / 2) / self.tile_height + center_y
        return math.floor(world_x), math.floor(world_y)
