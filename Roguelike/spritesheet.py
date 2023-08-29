import math
import os
import pygame

from PIL import Image
import numpy as np
from sklearn.cluster import KMeans


class SpriteSheet:
    def __init__(self, directory, tile_width=32, tile_height=32):
        self.directory = directory
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.sheet_path = self._find_or_create_sheet()
        self.sheet_image = pygame.image.load(self.sheet_path)

    def _create_image_grid(self, directory, output_path):
        # Step 1: Collect all image paths in the directory
        image_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('spritesheet_')]
    
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

    def _find_or_create_sheet(self):
        # Check for an existing _sheet.png image
        for filename in os.listdir(self.directory):
            if filename == f'spritesheet_{self.tile_width}_{self.tile_height}.png':
                return os.path.join(self.directory, filename)

        # If no existing sheet, create a new one
        sheet_path = os.path.join(self.directory, f'spritesheet_{self.tile_width}_{self.tile_height}.png')
        self._create_image_grid(self.directory, sheet_path)
        return sheet_path

    def render(self, screen, tile_index, world_x, world_y, center_x, center_y):
        screen_x = (world_x - center_x) * self.tile_width + (screen.get_width() - self.tile_width) / 2
        screen_y = (world_y - center_y) * self.tile_height + (screen.get_height() - self.tile_height) / 2
        cols = self.sheet_image.get_width() // self.tile_width
        row = tile_index // cols
        col = tile_index % cols

        # Determine the source rectangle for the tile
        source_rect = pygame.Rect(col * self.tile_width, row * self.tile_height, self.tile_width, self.tile_height)
        
        # Blit (copy) the tile from the sprite sheet onto the screen at the specified location
        screen.blit(self.sheet_image, (screen_x, screen_y), source_rect)

    def screen_to_world(self, screen, screen_x, screen_y, center_x, center_y):
        world_x = (screen_x - (screen.get_width() - self._tile_size) / 2) / self._tile_size + center_x
        world_y = (screen_y - (screen.get_height() - self._tile_size) / 2) / self._tile_size + center_y
        return math.floor(world_x), math.floor(world_y)
