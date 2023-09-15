import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Delaunay


def create_road_network(points):
    # Perform Delaunay triangulation
    tri = Delaunay(points)
    
    # Plot the points
    plt.scatter(points[:,0], points[:,1])
    
    # Plot the Delaunay triangle edges
    for simplex in tri.simplices:
        plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
    
    plt.show()

# Example usage
points = [[2, 3], [5, 5], [9, 6], [6, 9], [1, 7], [8, 1]]
create_road_network(np.array(points))
