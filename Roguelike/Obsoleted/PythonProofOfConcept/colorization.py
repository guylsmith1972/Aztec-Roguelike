import numpy as np

def interpolate_color(color1, color2, alpha):
    """
    Interpolate between two colors.
    :param color1: First color as an (R, G, B) tuple.
    :param color2: Second color as an (R, G, B) tuple.
    :param alpha: The weight of the second color, between 0 and 1.
    :return: Interpolated color as an (R, G, B) tuple.
    """
    r = int(color1[0] * (1 - alpha) + color2[0] * alpha)
    g = int(color1[1] * (1 - alpha) + color2[1] * alpha)
    b = int(color1[2] * (1 - alpha) + color2[2] * alpha)
    return r, g, b

def map_value_to_color(value, colormap):
    """
    Map a value to a color using the given colormap.
    :param value: The value to map.
    :param colormap: The colormap, a list of (value, color) tuples.
    :return: Color as an (R, G, B) tuple.
    """
    # If the value is exactly in the colormap, return the corresponding color.
    for v, color in colormap:
        if value == v:
            return color

    # Otherwise, find the two closest values in the colormap.
    for i in range(len(colormap) - 1):
        v1, color1 = colormap[i]
        v2, color2 = colormap[i + 1]
        if v1 <= value <= v2:
            # Interpolate the color based on the relative position of the value.
            alpha = (value - v1) / (v2 - v1)
            return interpolate_color(color1, color2, alpha)

    # If the value is outside the range of the colormap, return the closest color.
    if value < colormap[0][0]:
        return colormap[0][1]
    return colormap[-1][1]

def colorize_array(data, colormap):
    """
    Colorize a 2D numpy array using a colormap.
    :param data: 2D numpy array of float values between -1 and 1.
    :param colormap: The colormap, a list of (value, color) tuples.
    :return: 2D numpy array of RGB values.
    """
    rows, cols = data.shape
    output = np.zeros((rows, cols, 3), dtype=np.uint8)
    for i in range(rows):
        for j in range(cols):
            output[i, j] = map_value_to_color(data[i, j], colormap)
    return output
