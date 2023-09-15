from collections import Counter
from collections import defaultdict
import random
from native_code import generate_noise
from PIL import Image
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.stats import gamma, norm
from sklearn.cluster import KMeans
import json
import math
import matplotlib.pyplot as plt
import numpy as np



def average_temperature(latitude):
    """Returns the average annual temperature for a given latitude using the degree-5 polynomial fit in degrees centigrade."""
    # Coefficients for the degree-5 polynomial fit
    coeffs = [1.5435006954728608e-08, -2.29404014570294e-06, 0.0001733786920218803, -0.015368722900020351, 0.10005898261116034, 28.701268982733453]
    
    return sum(c * (latitude ** (len(coeffs) - 1 - i)) for i, c in enumerate(coeffs))


def average_rainfall(latitude):
    """Returns the average annual rainfall for a given latitude using the degree-5 polynomial fit in mm/year."""
    # Coefficients for the degree-5 polynomial fit
    coeffs = [2.9541885404048885e-06, -0.0007424099658586523, 0.0666726220340469, -2.311146020713387, 0.09303772684647389, 1583.7591013105796]
    
    return sum(c * (latitude ** (len(coeffs) - 1 - i)) for i, c in enumerate(coeffs))


def temp_std_deviation(latitude):
    """Returns the standard deviation in temperature for a given latitude using the degree-5 polynomial fit."""
    # Coefficients for the degree-5 polynomial fit
    coeffs = [-9.153318077803795e-10, 2.309132515082305e-07, -2.1416684002497494e-05, 0.0008870917412107778, 0.024347097982108757, 1.4862076138964038]
    
    return sum(c * (latitude ** (len(coeffs) - 1 - i)) for i, c in enumerate(coeffs))


def rainfall_std_deviation(latitude):
    """Returns the standard deviation in rainfall for a given latitude using the degree-5 polynomial fit."""
    # Coefficients for the degree-5 polynomial fit
    coeffs = [3.5536411360884604e-08, -1.017633598061689e-05, 0.000993808049535639, -0.03289944810876433, -0.6655054516085374, 79.56064073226537]
    
    return sum(c * (latitude ** (len(coeffs) - 1 - i)) for i, c in enumerate(coeffs))


def generate_rainfall_from_uniform(u, mu, sigma):
    # Calculate shape (k) and scale (theta) parameters for the Gamma distribution
    k = (mu / sigma) ** 2
    theta = sigma ** 2 / mu
    
    # Convert the uniform random number to a rainfall amount using the inverse of the Gamma CDF
    rainfall = gamma.ppf(u, k, scale=theta)
    
    return rainfall


def generate_climate_data(latitude, rand_temp, rand_rainfall):
    """
    Generates a temperature and rainfall tuple based on latitude and random values.
    
    Parameters:
    - latitude: the geographical latitude
    - rand_temp: a random number between 0 and 1 for temperature adjustment
    - rand_rainfall: a random number between 0 and 1 for rainfall adjustment
    
    Returns:
    - A tuple (temperature, rainfall)
    """
    avg_temp = average_temperature(latitude)
    avg_rainfall = average_rainfall(latitude)
    
    std_dev_temp = temp_std_deviation(latitude) * 3
    std_dev_rainfall = rainfall_std_deviation(latitude) * 2
    
    # Convert the uniform random values to a normal distribution for temperature
    z_temp = norm.ppf(rand_temp)
    adjusted_temp = avg_temp + z_temp * std_dev_temp
    
    # Convert the uniform random value to a Gamma distribution for rainfall
    adjusted_rainfall = generate_rainfall_from_uniform(rand_rainfall, avg_rainfall, std_dev_rainfall)
    
    return (adjusted_temp, adjusted_rainfall)


TROPICAL_RAINFOREST = 0
TROPICAL_SEASONAL_FOREST_SAVANNA = 1
SUBTROPICAL_DESERT = 2
TEMPERATE_RAINFOREST = 3
TEMPERATE_SEASONAL_FOREST = 4
WOODLAND_SHRUBLAND = 5
TEMPERATE_DESERT = 6
BOREAL_FOREST_TAIGA = 7
TUNDRA = 8
POLAR_DESERT_FROST_DESERT = 9

BIOME_NAMES = {
    TROPICAL_RAINFOREST: "Tropical Rainforest",
    TROPICAL_SEASONAL_FOREST_SAVANNA: "Tropical Seasonal Forest/Savanna",
    SUBTROPICAL_DESERT: "Subtropical Desert",
    TEMPERATE_RAINFOREST: "Temperate Rainforest",
    TEMPERATE_SEASONAL_FOREST: "Temperate Seasonal Forest",
    WOODLAND_SHRUBLAND: "Woodland/Shrubland (Chaparral)",
    TEMPERATE_DESERT: "Temperate Desert",
    BOREAL_FOREST_TAIGA: "Boreal Forest/Taiga",
    TUNDRA: "Tundra",
    POLAR_DESERT_FROST_DESERT: "Polar Desert/Frost Desert"
}


def determine_biome(temp, rain):
    representatives = {
        TROPICAL_RAINFOREST: (25, 2000),
        TROPICAL_SEASONAL_FOREST_SAVANNA: (25, 1000),
        SUBTROPICAL_DESERT: (30, 250),
        TEMPERATE_RAINFOREST: (15, 2000),
        TEMPERATE_SEASONAL_FOREST: (15, 1000),
        WOODLAND_SHRUBLAND: (18, 750),
        TEMPERATE_DESERT: (15, 250),
        BOREAL_FOREST_TAIGA: (0, 500),
        TUNDRA: (-10, 250),
        POLAR_DESERT_FROST_DESERT: (-20, 100)
    }

    # Calculate min and max for normalization
    temp_min = min([temp for temp, _ in representatives.values()])
    temp_max = max([temp for temp, _ in representatives.values()])
    rain_min = min([rain for _, rain in representatives.values()])
    rain_max = max([rain for _, rain in representatives.values()])

    # Normalization functions
    def normalize_temp(temp):
        return (temp - temp_min) / (temp_max - temp_min)

    def normalize_rain(rain):
        return (rain - rain_min) / (rain_max - rain_min)

    # Distance function
    def distance(rep, data):
        dt = rep[0] - data[0]
        dr = rep[1] - data[1]
        return math.sqrt(dt*dt + dr*dr)
    
    # Normalize the input data
    norm_temp = normalize_temp(temp)
    norm_rain = normalize_rain(rain)
    
    # Calculate the distance to each representative
    distances = {biome_id: distance((normalize_temp(rep_temp), normalize_rain(rep_rain)), (norm_temp, norm_rain))
                 for biome_id, (rep_temp, rep_rain) in representatives.items()}
    
    # Return the biome ID with the shortest distance
    return min(distances, key=distances.get)
        

def compute_biomes_from_noise(noise):
    """
    Computes biome values from the given noise array.
    
    Parameters:
    - noise: a 2D numpy array of shape (n, n) containing values in the range [0, 1]
    
    Returns:
    - A 2D numpy array of shape (n/2, n) containing biome constants.
    """
    
    # Calculate the dimensions for the output array
    n = noise.shape[0]
    output_height = n // 2
    
    # Initialize the output array
    climate_data = np.zeros((output_height, n), dtype=int)
    
    # Compute biomes for each coordinate
    for y in range(output_height):
        for x in range(n):
            # Calculate latitude based on y position
            latitude = abs((y / output_height) * 180 - 90)
            
            # Retrieve noise values for temperature and rainfall
            temp_noise = noise[y, x]
            rainfall_noise = noise[y + output_height, x]
            
            temp, rainfall = generate_climate_data(latitude, temp_noise, rainfall_noise)
            
            # Determine the biome for the computed temperature and rainfall
            biome = determine_biome(temp, rainfall)
            
            # Store the biome value in the output array
            climate_data[y, x] = biome
            
    return climate_data


def plot_biomes(biome_array):
    """
    Plots the given biome array using matplotlib with latitude on the y-axis.
    
    Parameters:
    - biome_array: 2D numpy array containing biome constants
    
    Returns:
    - A plotted figure.
    """
    
    # Define colors for the biomes based on the Whittaker Biome Diagram
    biome_colors = {
        TROPICAL_RAINFOREST: 'darkgreen',
        TROPICAL_SEASONAL_FOREST_SAVANNA: 'green',
        SUBTROPICAL_DESERT: 'yellow',
        TEMPERATE_RAINFOREST: 'seagreen',
        TEMPERATE_SEASONAL_FOREST: 'limegreen',
        WOODLAND_SHRUBLAND: 'lime',
        TEMPERATE_DESERT: 'khaki',
        BOREAL_FOREST_TAIGA: 'darkolivegreen',
        TUNDRA: 'lightcyan',
        POLAR_DESERT_FROST_DESERT: 'white'
    }
    
    # Create a colormap
    cmap = plt.cm.colors.ListedColormap([biome_colors[i] for i in range(len(BIOME_NAMES))])

    # Plotting the biome array
    plt.figure(figsize=(10,5))
    plt.imshow(biome_array, cmap=cmap, aspect='auto', extent=[0, biome_array.shape[1], -90, 90])
    
    # Set the y-axis to represent latitudes
    plt.ylabel("Latitude")
    
    # Add colorbar with biome names
    cbar = plt.colorbar(ticks=range(len(BIOME_NAMES)))
    cbar.set_ticklabels([BIOME_NAMES[i] for i in range(len(BIOME_NAMES))])
    
    plt.title("Biomes from Whittaker Diagram")


def count_colors_per_line(image):
    """
    Count the occurrences of each color on each horizontal line of the image.
    
    Args:
    - image (PIL.Image): The image to analyze.
    
    Returns:
    - dict: A dictionary where keys are row numbers and values are dictionaries 
            of color counts for that row.
    """
    width, height = image.size
    pixels = image.load()
    
    # Initialize the results dictionary
    results = {}
    
    index_map = {}
    
    for y in range(height):
        # Use defaultdict for counting colors
        color_counts = defaultdict(int)
        
        for x in range(width):
            color = pixels[x, y]
            if color not in index_map:
                index_map[color] = len(index_map)
            index = index_map[color]
            color_counts[index] += 1
        
        results[y] = dict(color_counts)
    
    return results, index_map


def count_colors_per_line_from_file(filename):
    """
    Load an image from the given filename and count the occurrences of each color 
    on each horizontal line of the image.
    
    Args:
    - filename (str): The path to the image file.
    
    Returns:
    - dict: A dictionary where keys are row numbers and values are dictionaries 
            of color counts for that row.
    """
    # Load the image from the given filename
    image = Image.open(filename)
    
    # Use the previously defined function to get the color counts
    return count_colors_per_line(image)



def remap_indices(color_map):
    def closest_color_index(color):
        """Find the index of the closest color in the color map."""
        min_distance = float('inf')
        closest_index = None

        for index, original_color in color_map.items():
            distance = np.linalg.norm(np.array(original_color[:3]) - np.array(color))
            if distance < min_distance:
                min_distance = distance
                closest_index = index

        return closest_index

    colors = [value[:3] for value in color_map.values()]

    # Reapply K-Means clustering
    kmeans = KMeans(n_clusters=16, random_state=0)
    kmeans.fit(colors)

    # Re-find the representative colors (cluster centroids)
    representative_colors = kmeans.cluster_centers_

    # Map representative colors to their closest original indices
    mapped_indices = {closest_color_index(color, color_map): color.astype(int).tolist() for color in representative_colors}

    mapped_indices


def main():
    def apply_noise(reference, noise):
        # Extract the dimensions of the reference image and noise array
        ref_width, ref_height = reference.size
        noise_height, noise_width = noise.shape
    
        # Create an empty PIL image to store the result
        output = Image.new('RGB', (ref_width, ref_height))
    
        # For each pixel in the output image
        for y in range(ref_height):
            for x in range(ref_width):
                # Calculate the new position in the reference image
                new_x = int(noise[y % noise_height][x % noise_width] * (ref_width - 1))
                new_pixel = reference.getpixel((new_x, y))
                # Set the pixel value in the output image
                output.putpixel((x, y), new_pixel)
    
        return output
    
    img = Image.open('Assets/References/biome_map_revised.png')
    print(img.size)
    noise = generate_noise(4096, 1, 1, seed=random.randint(0, 1000000000))
    foo = apply_noise(img, noise)
    foo.save('Assets/References/random_world.png')


    # # Load the image
    # img = Image.open('Assets/References/biome_map_revised.png')

    # # Convert the image to RGB (just in case it's in another format like RGBA)
    # img_rgb = img.convert('RGB')

    # # Convert the image data to an array
    # data = np.array(img_rgb)

    # # Extract all unique colors from the image
    # unique_colors = np.unique(data.reshape(-1, 3), axis=0)
    
    # print(len(unique_colors))

    # # Flatten the image data for counting
    # flattened_data = data.reshape(-1, 3)

    # # Count the occurrences of each color
    # color_counts = Counter(map(tuple, flattened_data))

    # # Find the 16 most common colors
    # most_common_colors = np.array([color for color, count in color_counts.most_common(16)])
    
    # print(most_common_colors)

    # def find_nearest_color(color, palette):
    #     """Find the nearest color in the palette using Euclidean distance."""
    #     distances = np.sum((palette - color) ** 2, axis=1)
    #     return palette[np.argmin(distances)]

    # # Create an output array of the same shape as the input data
    # output_data = np.zeros_like(data)

    # # Replace each pixel's color with the nearest color from the 16 most common colors
    # for i in range(data.shape[0]):
    #     for j in range(data.shape[1]):
    #         output_data[i, j] = find_nearest_color(data[i, j], most_common_colors)

    # # Convert the output data to an image
    # output_img = Image.fromarray(output_data.astype('uint8'))
    # output_img.save('Assets/References/biome_map_revised.png')

    # # Display the original and modified images side by side
    # original_img = img.resize((img.width // 2, img.height // 2))
    # modified_img = output_img.resize((output_img.width // 2, output_img.height // 2))
    # combined_img = Image.new('RGB', (original_img.width + modified_img.width, original_img.height))
    # combined_img.paste(original_img, (0, 0))
    # combined_img.paste(modified_img, (original_img.width, 0))
    
    # colors_per_line, color_map = count_colors_per_line_from_file('Assets/References/biome_map_revised.png')
    # print(color_map)
    # with open('colors_per_line.json', 'w') as outfile:
    #     json.dump(colors_per_line, outfile, indent=2)        
    # with open('color_map.json', 'w') as outfile:
    #     json.dump({v:k for k, v in color_map.items()}, outfile, indent=2)
        
    # remapped = remap_indices(color_map)
    # print(json.dumps(remapped, indent=2))

    # latitude = 90
    # while latitude >= 0:
    #     print(f'lat {latitude}: {average_temperature(latitude)}C +/-{temp_std_deviation(latitude)}, {average_rainfall(latitude)} mm/year +/{rainfall_std_deviation(latitude)}')
    #     latitude -= 5

    # noise = generate_noise(512, 5, 1, seed=random.randint(0, 1000000000))
    # biomes = compute_biomes_from_noise(noise)
    # print(biomes)
    # plot_biomes(biomes)
    
    # representatives = {
    #     TROPICAL_RAINFOREST: (25, 2000),
    #     TROPICAL_SEASONAL_FOREST_SAVANNA: (25, 1000),
    #     SUBTROPICAL_DESERT: (30, 250),
    #     TEMPERATE_RAINFOREST: (15, 2000),
    #     TEMPERATE_SEASONAL_FOREST: (15, 1000),
    #     WOODLAND_SHRUBLAND: (18, 750),
    #     TEMPERATE_DESERT: (15, 250),
    #     BOREAL_FOREST_TAIGA: (0, 500),
    #     TUNDRA: (-10, 250),
    #     POLAR_DESERT_FROST_DESERT: (-20, 100)
    # }

    # # Compute Voronoi tessellation
    # points = list(representatives.values())
    # vor = Voronoi(points)

    # # Plot
    # fig, ax = plt.subplots(figsize=(10, 8))
    # voronoi_plot_2d(vor, ax=ax, show_vertices=True, show_points=True)

    # # Annotate with labels
    # for biome_id, point in representatives.items():
    #     ax.text(point[0], point[1], BIOME_NAMES[biome_id], fontsize=8)

    # plt.title("Voronoi Diagram of Ecosystem Representatives")
    # plt.xlabel("Temperature C")
    # plt.ylabel("Rainfall (mm/year)")
    # plt.show()


if __name__ == '__main__':
    main()
    