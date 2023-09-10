from matplotlib.colors import BoundaryNorm, ListedColormap, LinearSegmentedColormap, LogNorm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def custom_colormap(color_key):
    # Convert HEX colors to RGB tuples
    colors = [(value, hex_to_rgb(color)) for value, color in color_key]
    
    # Create a colormap
    cmap = LinearSegmentedColormap.from_list("custom", colors, N=256)
    
    return cmap

def hex_to_rgb(hex_color):
    # Convert HEX color to RGB tuple
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))


def add_figure(name, data, cmap, vmin=0, vmax=1, norm=None):
    plt.figure(name)
    if norm is None:
        plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    else:
        plt.imshow(data, cmap=cmap, norm=norm)
    # plt.title = name
    plt.colorbar() 
    

def histogram_plot(name, data):
    flattened_data = data.flatten()

    # Generate the histogram
    plt.figure(f'{name} Histogram')
    plt.hist(flattened_data, bins='auto', edgecolor='black', alpha=0.7)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)


def remove_outliers(data, factor=1.5):
    """
    Removes outliers from a numpy array using the IQR method.
    
    :param data: Numpy array of data
    :param factor: Multiplication factor for the IQR. Default is 1.5, which is typical for outliers.
    :return: Filtered numpy array without outliers.
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    
    return data[(data >= lower_bound) & (data <= upper_bound)]


def plot_with_transparency(name, base_data, base_cmap, base_vmin, base_vmax, overlay_data):
    _, ax = plt.subplots()

    # Display the first array with a colormap
    cax = ax.imshow(base_data, cmap=base_cmap, vmin=base_vmin, vmax=base_vmax)

    # Display the second array on top of the first
    # We create a RGBA image where R,G,B is set to (0,0,1) for blue and A (alpha) is the values from array2
    blue_rgba = np.zeros((overlay_data.shape[0], overlay_data.shape[1], 4))
    blue_rgba[:, :, 2] = 1.0  # Set blue channel to 1
    blue_rgba[:, :, 3] = np.clip(overlay_data, 0, 1)  # Set alpha channel from array2 values
    ax.imshow(blue_rgba, cmap='Blues', interpolation='nearest')

    plt.colorbar(cax)


def plot_2d_histogram(x_data, y_data, x_label='X-axis', y_label='Y-axis', title='2D Histogram (Log Scale)', bins=500):
    # Compute the 2D histogram
    H, xedges, yedges = np.histogram2d(x_data.ravel(), y_data.ravel(), bins=bins)
    
    # Display the histogram with logarithmic color scale
    plt.figure(title)
    plt.imshow(H.T, origin='lower', cmap='inferno', interpolation='nearest', aspect='auto',
               extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], norm=LogNorm())
    plt.colorbar(label='Log(Number of points)')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    

def show_plots():
    plt.show()
    