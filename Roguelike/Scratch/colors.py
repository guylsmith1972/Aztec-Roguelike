import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

def get_average_colors(image: Image.Image, n: int) -> list:
    """Return a list of n average RGB values using K-means clustering on the given image."""
    
    # Convert image to RGB array
    img_array = np.array(image)
    if img_array.shape[-1] == 4:  # Check for alpha channel
        img_array = img_array[:, :, :-1]
    
    # Reshape the image data into a list of RGB values
    rgb_values = img_array.reshape(-1, 3)
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=n)
    kmeans.fit(rgb_values)
    cluster_centers = kmeans.cluster_centers_
    
    # Convert cluster centers to integer RGB values
    avg_colors = [tuple(map(int, center)) for center in cluster_centers]
    
    return avg_colors

def assign_clusters_to_pixels(image: Image.Image, cluster_colors: list) -> np.ndarray:
    """Assign cluster IDs to each pixel of the image based on the given cluster colors."""
    
    # Convert image to RGB array
    img_array = np.array(image)
    if img_array.shape[-1] == 4:  # Check for alpha channel
        img_array = img_array[:, :, :-1]
    
    # Initialize an empty array for cluster IDs
    cluster_ids = np.zeros(img_array.shape[:2], dtype=np.int32)
    
    # Assign each pixel to the closest cluster
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            pixel = img_array[i, j]
            distances = [np.linalg.norm(pixel - np.array(color)) for color in cluster_colors]
            cluster_ids[i, j] = np.argmin(distances)
    
    return cluster_ids
