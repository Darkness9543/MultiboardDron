import math
import requests
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO
import tkinter as tk
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

def deg2num_frac(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = (lon_deg + 180.0) / 360.0 * n
    y = (1.0 - math.log(
        math.tan(lat_rad) + 1 / math.cos(lat_rad)
    ) / math.pi) / 2.0 * n
    return x, y


def fetch_tile(x, y, z, tile_server_url):
    url = tile_server_url.format(z=z, x=x, y=y)
    response = requests.get(url)
    if response.status_code == 200:
        tile_image = Image.open(BytesIO(response.content)).convert('RGB')
        return tile_image
    else:
        print(f"Failed to fetch tile {x}, {y}")
        return None


def latlon_to_pixel_xy(lat, lon, zoom, x_origin_tile, y_origin_tile, tile_size):
    x_tile, y_tile = deg2num_frac(lat, lon, zoom)
    x_pixel = (x_tile - x_origin_tile) * tile_size
    y_pixel = (y_tile - y_origin_tile) * tile_size
    return x_pixel, y_pixel


def meters_to_pixels(meters, lat, zoom, tile_size):
    # Earth's radius in meters
    earth_radius = 6378137
    lat_rad = math.radians(lat)
    # Calculate ground resolution (meters per pixel) at given latitude
    resolution = (2 * math.pi * earth_radius * math.cos(lat_rad)) / (tile_size * 2 ** zoom)
    pixels = meters / resolution
    return pixels


def draw_polygons_with_exclusions_on_map(map_image, geofence_vector, zoom, x_origin_tile, y_origin_tile, tile_size,
                                         colors):
    print("Draw polygons")

    # Ensure map_image is in RGBA mode to handle transparency
    if map_image.mode != 'RGBA':
        map_image = map_image.convert('RGBA')

    for idx, shape_group in enumerate(geofence_vector):
        main_shape_data = shape_group[0]  # First element is the main shape
        exclusion_zones_data = shape_group[1:]  # Remaining elements are exclusion zones

        # Build main shape
        main_shape = None

        if main_shape_data['type'] == 'polygon':
            # Process polygon
            waypoints = main_shape_data['waypoints']
            main_shape_coords = []
            for point in waypoints:
                lat = point['lat']
                lon = point['lon']
                x_pixel, y_pixel = latlon_to_pixel_xy(lat, lon, zoom, x_origin_tile, y_origin_tile, tile_size)
                x_pixel = int(round(x_pixel))
                y_pixel = int(round(y_pixel))
                main_shape_coords.append((x_pixel, y_pixel))
            if len(main_shape_coords) >= 3:
                main_shape = Polygon(main_shape_coords)
            else:
                continue
        elif main_shape_data['type'] == 'circle':
            # Process circle
            center_lat = main_shape_data['lat']
            center_lon = main_shape_data['lon']
            radius_meters = main_shape_data['radius']
            center_x, center_y = latlon_to_pixel_xy(center_lat, center_lon, zoom, x_origin_tile, y_origin_tile,
                                                    tile_size)
            center_x = int(round(center_x))
            center_y = int(round(center_y))
            radius_pixels = meters_to_pixels(radius_meters, center_lat, zoom, tile_size)
            main_shape = Point(center_x, center_y).buffer(radius_pixels)
        else:
            raise ValueError(f"Unknown shape type: {main_shape_data['type']}")

        # Build exclusion zones
        exclusion_shapes = []
        for exclusion in exclusion_zones_data:
            exclusion_shape = None
            if exclusion['type'] == 'polygon':
                waypoints = exclusion['waypoints']
                exclusion_coords = []
                for point in waypoints:
                    lat = point['lat']
                    lon = point['lon']
                    x_pixel, y_pixel = latlon_to_pixel_xy(lat, lon, zoom, x_origin_tile, y_origin_tile, tile_size)
                    x_pixel = int(round(x_pixel))
                    y_pixel = int(round(y_pixel))
                    exclusion_coords.append((x_pixel, y_pixel))
                if len(exclusion_coords) >= 3:
                    exclusion_shape = Polygon(exclusion_coords)
                else:
                    continue
            elif exclusion['type'] == 'circle':
                center_lat = exclusion['lat']
                center_lon = exclusion['lon']
                radius_meters = exclusion['radius']
                center_x, center_y = latlon_to_pixel_xy(center_lat, center_lon, zoom, x_origin_tile, y_origin_tile,
                                                        tile_size)
                center_x = int(round(center_x))
                center_y = int(round(center_y))
                radius_pixels = meters_to_pixels(radius_meters, center_lat, zoom, tile_size)
                exclusion_shape = Point(center_x, center_y).buffer(radius_pixels)
            else:
                raise ValueError(f"Unknown shape type: {exclusion['type']}")
            if exclusion_shape:
                exclusion_shapes.append(exclusion_shape)

        # Subtract exclusion zones from main shape
        for exclusion_shape in exclusion_shapes:
            main_shape = main_shape.difference(exclusion_shape)

        if main_shape.is_empty:
            continue

        # Create a mask image for the shape, including holes
        mask = Image.new('L', map_image.size, 0)  # 'L' mode for grayscale
        draw_mask = ImageDraw.Draw(mask)

        # Handle both Polygon and MultiPolygon
        if main_shape.type == 'Polygon':
            polygons = [main_shape]
        elif main_shape.type == 'MultiPolygon':
            polygons = list(main_shape)
        else:
            continue

        for polygon in polygons:
            # Exterior coordinates
            exterior_coords = [(int(round(x)), int(round(y))) for x, y in polygon.exterior.coords]
            if len(exterior_coords) >= 3:
                draw_mask.polygon(exterior_coords, fill=255)
            # Interior coordinates (holes)
            for interior in polygon.interiors:
                interior_coords = [(int(round(x)), int(round(y))) for x, y in interior.coords]
                if len(interior_coords) >= 3:
                    draw_mask.polygon(interior_coords, fill=0)

        # Create an overlay image with the shape color and alpha
        overlay = Image.new('RGBA', map_image.size, (0, 0, 0, 0))
        print(f"Map colors: {colors}")
        color = colors[idx % len(colors)]  # Color should include alpha, e.g., (R, G, B, A)
        print(f"Map color: {color}")
        color_image = Image.new('RGBA', map_image.size, color)
        # Paste the color image onto the overlay using the mask
        overlay.paste(color_image, (0, 0), mask)

        # Composite the overlay onto the map image
        map_image = Image.alpha_composite(map_image, overlay)
        return map_image
def create_map_image(lat_deg=41.276408, lon_deg=1.9886864, zoom=20, tile_size=256, desired_width=888,
                     desired_height=550,
                     tile_server_url="https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", geofence_vector=None,
                     colors=None):
    if colors is None:
        colors = [
            (255, 0, 0, 100),  # Red with transparency
            (0, 0, 255, 100),  # Blue with transparency
            (0, 255, 0, 100),  # Green with transparency
            (255, 255, 0, 100),  # Yellow with transparency
            (255, 0, 255, 100),  # Magenta with transparency
            (0, 255, 255, 100),  # Cyan with transparency
        ]
    x, y = deg2num_frac(lat_deg, lon_deg, zoom)
    xtile, ytile = int(x), int(y)

    # Create an image to hold the map tiles
    map_image = Image.new('RGB', (tile_size * 3, tile_size * 3))

    # Fetch and assemble the tiles
    for i in range(-1, 2):
        for j in range(-1, 2):
            tile = fetch_tile(xtile + i, ytile + j, zoom, tile_server_url)
            if tile:
                map_image.paste(tile, ((i + 1) * tile_size, (j + 1) * tile_size))
            else:
                print(f"Missing tile at {xtile + i}, {ytile + j}")

    # Compute the pixel coordinates of the center location in the assembled image
    pixel_x = (x - (xtile - 1)) * tile_size
    pixel_y = (y - (ytile - 1)) * tile_size

    # Compute x_origin_tile and y_origin_tile
    x_origin_tile = xtile - 1
    y_origin_tile = ytile - 1

    # Draw polygons if any
    if geofence_vector is not None:
        map_image = draw_polygons_with_exclusions_on_map(map_image, geofence_vector, zoom, x_origin_tile, y_origin_tile, tile_size, colors)

    # Crop the image to the desired size centered at the center location
    half_width = desired_width // 2
    half_height = desired_height // 2

    left = pixel_x - half_width
    upper = pixel_y - half_height
    right = pixel_x + half_width
    lower = pixel_y + half_height

    # Ensure the crop rectangle is within the image boundaries
    left = max(0, left)
    upper = max(0, upper)
    right = min(map_image.width, right)
    lower = min(map_image.height, lower)

    cropped_image = map_image.crop((left, upper, right, lower))

    # Compute the position of the center location in the cropped image
    center_position = (pixel_x - left, pixel_y - upper)

    return cropped_image, center_position


def add_marker_to_map_image(map_image, marker_image_path, position):
    # Load and resize the marker image
    marker_image = Image.open(marker_image_path).convert("RGBA")
    marker_size = 30
    marker_image = marker_image.resize((marker_size, marker_size), Image.LANCZOS)

    # Compute the position to paste the marker image
    marker_width, marker_height = marker_image.size
    marker_x = position[0] - marker_width // 2
    marker_y = position[1] - marker_height // 2

    # Paste the marker onto the map image
    map_image.paste(marker_image, (int(marker_x), int(marker_y)), marker_image)


def display_map_image(image, root):
    photo = ImageTk.PhotoImage(image)

    label = tk.Label(root, image=photo)
    label.grid(row=0 , column=0)

def display_map_image_test(image):
    root = tk.Tk()
    root.title("Drone Map")

    photo = ImageTk.PhotoImage(image)

    label = tk.Label(root, image=photo)
    label.pack()

    root.mainloop()

if __name__ == "__main__":
    # Set initial position and zoom level
    lat = 41.276428
    lon = 1.9886864
    zoom = 20

    # Sample geofence_vector with polygons nearby
    geofence_vector = [
        [
            {
                'type': 'polygon',
                'waypoints': [
                    {'lat': 41.2764398, 'lon': 1.9882585},
                    {'lat': 41.2761999, 'lon': 1.9883537},
                    {'lat': 41.2763854, 'lon': 1.9890994},
                    {'lat': 41.2766273, 'lon': 1.9889948}
                ]
            },
            {
                'type': 'polygon',
                'waypoints': [
                    {'lat': 41.2764801, 'lon': 1.9886541},
                    {'lat': 41.2764519, 'lon': 1.9889626},
                    {'lat': 41.2763995, 'lon': 1.9887963},
                ]
            },
            {
                'type': 'polygon',
                'waypoints': [
                    {'lat': 41.2764035, 'lon': 1.9883262},
                    {'lat': 41.2762160, 'lon': 1.9883537},
                    {'lat': 41.2762281, 'lon': 1.9884771}
                ]
            },
            {
                'type': 'circle',
                'radius': 2,
                'lat': 41.2763430,
                'lon': 1.9883953
            }
        ]
    ]
    # Create the map image with polygons
    map_image, center_position = create_map_image(lat, lon, zoom, geofence_vector=geofence_vector)

    # Display the map image in a Tkinter window
    display_map_image_test(map_image)
