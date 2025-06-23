import rasterio
import matplotlib.pyplot as plt
import math


def degree_to_meters(degree, latitude):
    """Converts degrees to meters, adjusting for the given latitude."""
    meters_per_degree_latitude = 111000  # Average length of a degree of latitude in meters
    meters_per_degree_longitude = meters_per_degree_latitude * math.cos(math.radians(latitude))
    return degree * meters_per_degree_longitude


def main():
    # Replace with the path to your GeoTIFF file
    file_path = 'heightmaps/mt_desert.tif'

    try:
        with rasterio.open(file_path) as src:
            # Print width and height in pixels
            width, height = src.width, src.height
            print(f"Width in pixels: {width}")
            print(f"Height in pixels: {height}")

            # Extract pixel sizes from the affine transform
            transform = src.transform
            pixel_width_deg, pixel_height_deg = transform[0], -transform[4]

            # Calculate approximate central latitude of the raster
            # for more accurate conversion to meters
            central_latitude = src.xy(height // 2, width // 2)[1]

            # Convert pixel size to meters
            pixel_width_m = degree_to_meters(pixel_width_deg, central_latitude)
            pixel_height_m = degree_to_meters(pixel_height_deg, central_latitude)

            print(f"Pixel size - Width: {pixel_width_m}m, Height: {pixel_height_m}m")

            # Calculate and print width and height in meters
            width_meters = width * pixel_width_m
            height_meters = height * pixel_height_m
            print(f"Width in meters: {width_meters}m")
            print(f"Height in meters: {height_meters}m")

            # Read the first band and display
            data = src.read(1)
            plt.imshow(data, cmap='gray')
            plt.title('GeoTIFF Raster Data')
            plt.colorbar()
            plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
