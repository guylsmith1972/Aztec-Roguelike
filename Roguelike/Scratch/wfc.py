import colors
import heapq
import pygame
import numpy as np
import random

from PIL import Image


class WaveFunctionCollapse:
    """
    A class to implement the Wave Function Collapse algorithm which generates a larger output pattern 
    based on the constraints of a given sample pattern.
    """
    
    def __init__(self, constraints, output_size):
        """
        Initializes the WaveFunctionCollapse with given constraints and desired output size.
        
        Parameters:
        - constraints (dict): A dictionary of constraints where each tile maps to its allowed neighbors.
        - output_size (tuple): A tuple (rows, cols) indicating the size of the desired output pattern.
        """
        
        self.constraints = constraints
        self.output_size = output_size
        self.tiles = list(constraints.keys())
        self.initialize_output()
        
    @staticmethod
    def generate_constraints_from_sample(sample):
        """
        Generates constraints based on a sample pattern.
        
        Parameters:
        - sample (list[list[int]]): 2D grid representing the sample pattern.
        
        Returns:
        - dict: Dictionary where each tile maps to its allowed neighbors.
        """
        constraints = {}
        rows, cols = len(sample), len(sample[0])

        for i in range(rows):
            for j in range(cols):
                tile = sample[i][j]
                if tile not in constraints:
                    constraints[tile] = {"R": [], "B": []}
            
                if j + 1 < cols and sample[i][j + 1] not in constraints[tile]["R"]:
                    constraints[tile]["R"].append(sample[i][j + 1])

                if i + 1 < rows and sample[i + 1][j] not in constraints[tile]["B"]:
                    constraints[tile]["B"].append(sample[i + 1][j])

        return constraints
        
    def initialize_output(self):
        """
        Initializes the output grid and entropy heap.
        """
        self.output = np.array([[set(self.tiles) for _ in range(self.output_size[1])]
                                for _ in range(self.output_size[0])])
        self.entropy_heap = [(len(self.output[i, j]), (i, j)) for i in range(self.output_size[0]) 
                                                              for j in range(self.output_size[1])]
        heapq.heapify(self.entropy_heap)
        
    def pop_lowest_entropy_cell(self):
        """
        Pops and returns the coordinates of the cell with the lowest entropy from the heap.
        
        Returns:
        - tuple: (row, col) coordinates of the cell with the lowest entropy or None if heap is empty.
        """
        while self.entropy_heap:
            entropy, cell = heapq.heappop(self.entropy_heap)
            if entropy == len(self.output[cell[0], cell[1]]):
                return cell
        return None
    
    def collapse_cell(self, cell_coords):
        """
        Collapses a cell to a single tile based on its possible states.
        
        Parameters:
        - cell_coords (tuple): (row, col) coordinates of the cell to be collapsed.
        
        Returns:
        - bool: True if the cell was successfully collapsed, False otherwise.
        """
        i, j = cell_coords
        if not self.output[i, j]:
            self.initialize_output()
            return False
        self.output[i, j] = set([random.choice(list(self.output[i, j]))])
        return True
        
    def propagate(self, cell_coords):
        """
        Propagates the constraints to neighboring cells after a cell has been collapsed.
        
        Parameters:
        - cell_coords (tuple): (row, col) coordinates of the collapsed cell.
        """
        i, j = cell_coords
        chosen_tile = list(self.output[i, j])[0]

        if j + 1 < self.output.shape[1]:
            self.output[i, j + 1] = self.output[i, j + 1].intersection(self.constraints[chosen_tile]["R"])
            heapq.heappush(self.entropy_heap, (len(self.output[i, j + 1]), (i, j + 1)))
        if i + 1 < self.output.shape[0]:
            self.output[i + 1, j] = self.output[i + 1, j].intersection(self.constraints[chosen_tile]["B"])
            heapq.heappush(self.entropy_heap, (len(self.output[i + 1, j]), (i + 1, j)))
            
    def run(self):
        """
        Runs the Wave Function Collapse algorithm to generate the output pattern.
        
        Returns:
        - np.array: 2D numpy array representing the generated pattern.
        """
        restarts = 0
        max_restarts = 10 
        while restarts < max_restarts:
            cell = self.pop_lowest_entropy_cell()
            if cell is None:
                break
            if not self.collapse_cell(cell):
                restarts += 1
                continue
            self.propagate(cell)
        return self.output


def main():
    image = pygame.image.load('Assets/Sprites/Terrain/originals/cobble-colored.png')
    pil_image = Image.frombytes("RGBA", image.get_size(), pygame.image.tostring(image, "RGBA"))
    print('getting average colors')
    color_list = colors.get_average_colors(pil_image, 32)
    print('assigning clusters')
    tiled_image = colors.assign_clusters_to_pixels(pil_image, color_list)
    print('getting constraints')
    constraints = WaveFunctionCollapse.generate_constraints_from_sample(tiled_image)
    print('creating wfc')
    wfc = WaveFunctionCollapse(constraints, (64, 64))
    print('doing wfc')
    out = wfc.run()
    print(out)
    

if __name__ == '__main__':
    main()
    