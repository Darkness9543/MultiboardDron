from tkintermapview import TkinterMapView
from PIL import Image, ImageTk, ImageDraw
import json
import math

class DroneMap:

    def handle_message(self, message):
        MessageDroneId = int(str(message.topic).split("/")[0].split("autopilotService")[1])
        ReceivedInfoType = str(message.topic).split("/")[2]
        if ReceivedInfoType == "telemetryInfo":
            payload = json.loads(message.payload)
            for drone in self.drones:
                if drone.DroneId + 1 == MessageDroneId:
                    drone.setTelemetryInfo(payload["groundSpeed"], "groundSpeed")
                    drone.setTelemetryInfo(payload["alt"], "alt")
                    drone.setTelemetryInfo(payload["state"], "state")
                    drone.setTelemetryInfo(payload["lat"], "lat")
                    drone.setTelemetryInfo(payload["lon"], "lon")
                    drone.setTelemetryInfo(payload["heading"], "heading")

                    self.move_marker(drone.DroneId, drone.lat, drone.lon, drone.heading)

    def __init__(self, parent, client, drones, drone_colors, height, width):

        self.drones = drones
        for i in range(len(self.drones)):
            client.subscribe(f"autopilotService{i + 1}/miMain/telemetryInfo")

        self.map_widget = TkinterMapView(parent, height=height, width=width)
        self.map_widget.grid(row=0, column=0)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", max_zoom=22)
        self.drone_colors =  [(255, 0, 0, 100), (0, 255, 0, 100)]

        # Set initial position and zoom level
        self.map_widget.set_position(41.276448, 1.9888564)
        self.map_widget.set_zoom(20)
        self.geofence_polygons = []
        # Dictionary to store markers
        self.markers = {}
        self.polygons = {}
        # Load the arrow image
        self.marker_image = Image.open("assets/dronaArrow.png")
        original_width, original_height = self.marker_image.size
        new_size = (original_width // 15, original_height // 15)
        self.marker_image = self.marker_image.resize(new_size, Image.LANCZOS)
        self.marker_images = []
        # Load the arrow image and create the combined image
        for drone in drones:
            marker_image = self.create_combined_marker_image("assets/dronaArrow.png", self.drone_colors[drone.DroneId])
            self.marker_images.append(marker_image)
        self.marker_color = self.drone_colors

    def create_combined_marker_image(self, arrow_path, fill_color):
        # Load the arrow image
        self.marker_image = Image.open(arrow_path)
        original_width, original_height = self.marker_image.size
        new_size = (original_width // 15, original_height // 15)
        self.marker_image = self.marker_image.resize(new_size, Image.LANCZOS)

        # Create a new image with an alpha channel
        combined_image = Image.new('RGBA', self.marker_image.size, (0, 0, 0, 0))

        # Create a draw object
        draw = ImageDraw.Draw(combined_image)

        # Draw a filled circle
        circle_diameter = min(new_size) - 34  # Leave a small border
        circle_radius = circle_diameter // 2
        circle_position = ((new_size[0] - circle_diameter) // 2 -0.1, (new_size[1] - circle_diameter) // 2)
        draw.ellipse([circle_position, (circle_position[0] + circle_diameter, circle_position[1] + circle_diameter)],
                     fill=fill_color)

        # Paste the original image onto the new image
        combined_image.paste(self.marker_image, (0, 0), self.marker_image)

        self.marker_image = combined_image
        return combined_image

    def move_marker(self, marker_id, lat, lon, heading):
        """
        Moves the marker with the given ID to a new location specified by lat and lon,
        and updates its arrow to point in the direction of the heading.
        """
        # If there is an existing marker, delete it
        if marker_id in self.markers:
            self.markers[marker_id].delete()

        # Rotate the base arrow image to match the heading
        rotated_image = self.marker_images[marker_id].rotate(-heading, resample=Image.BICUBIC, expand=True)
        # Convert to a PhotoImage
        marker_image = ImageTk.PhotoImage(rotated_image)
        # Create a new marker at the new location
        new_marker = self.map_widget.set_marker(lat, lon, icon=marker_image)
        self.markers[marker_id] = new_marker

    def draw_geofences(self, coordinates_set):
        """
        Draws geofences on the map. Inclusion zones are drawn in the drone's color with simulated transparency.
        Exclusion zones are drawn in black.

        :param coordinates_set: List of geofence data.
        """
        # First, hide any existing geofences
        self.hide_geofences()

        # Iterate over the geofence data
        for idx, shape_group in enumerate(coordinates_set):
            main_shape_data = shape_group[0]  # First element is the main shape
            exclusion_shapes_data = shape_group[1:]  # Remaining elements are exclusion shapes

            # Get the color for the inclusion zone
            color = self.drone_colors[idx % len(self.drone_colors)]
            # Adjust the color to simulate transparency (since true transparency isn't supported)
            adjusted_color = self.adjust_color_for_transparency(color)

            # Process the main shape (inclusion zone)
            if main_shape_data['type'] == 'polygon':
                waypoints = main_shape_data['waypoints']
                positions = [(wp['lat'], wp['lon']) for wp in waypoints]

                # Draw the inclusion polygon
                polygon = self.map_widget.set_polygon(positions, fill_color=adjusted_color, outline_color=adjusted_color)
                # Store the polygon for later removal
                self.geofence_polygons.append(polygon)
            else:
                # If you have other shape types like 'circle', handle them here
                pass  # For this example, only polygons are handled

            # Process exclusion zones
            for exclusion_shape in exclusion_shapes_data:
                if exclusion_shape['type'] == 'polygon':
                    waypoints = exclusion_shape['waypoints']
                    positions = [(wp['lat'], wp['lon']) for wp in waypoints]

                    # Draw the exclusion polygon in black
                    polygon = self.map_widget.set_polygon(positions, fill_color='black', outline_color='black')
                    self.geofence_polygons.append(polygon)
                else:
                    # Handle other shape types like 'circle' if needed
                    pass

    def hide_geofences(self):
        """
        Removes all geofences from the map.
        """
        for polygon in self.geofence_polygons:
            polygon.delete()
        self.geofence_polygons.clear()

    def adjust_color_for_transparency(self, color, alpha=100):
        if isinstance(color, str):
            # If color is a string (hex), convert it to RGB
            color = hex_to_rgb(color)
        """
        Adjusts the given color to simulate transparency by blending it with white.

        :param color: Tuple (R, G, B, A)
        :param alpha: Alpha value (0-255)
        :return: Hex color string
        """
        r, g, b, _ = color  # Ignore the original alpha
        alpha_fraction = alpha / 255.0
        # Blend the color with white to simulate transparency
        r_new = int(r * alpha_fraction + 255 * (1 - alpha_fraction))
        g_new = int(g * alpha_fraction + 255 * (1 - alpha_fraction))
        b_new = int(b * alpha_fraction + 255 * (1 - alpha_fraction))
        return '#{:02x}{:02x}{:02x}'.format(r_new, g_new, b_new)

def hex_to_rgb(hex_color):
    # Remove the '#' if it's there
    hex_color = hex_color.lstrip('#')
    # Convert hex to RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))