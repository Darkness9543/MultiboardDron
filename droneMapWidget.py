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
        self.drone_colors = drone_colors

        # Set initial position and zoom level
        self.map_widget.set_position(41.276448, 1.9888564)
        self.map_widget.set_zoom(20)

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

    def draw_geofence(self, coordinates_set, drone_id, color):
        """
        Draws a polygon on the map with the given coordinates, closing the figure by connecting the last and first points.
        The color of the polygon outline and fill matches the input color, with some transparency.
        Stores the polygon in a list, as with the markers.
        """
        # Transform coordinates_set into a list of tuples (lat, lon)
        coordinates = [(coord["lat"], coord["lon"]) for coord in coordinates_set]
        # Ensure the polygon is closed by adding the first point at the end if needed
        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])

        # Convert color name to hex with alpha transparency
        fill_color = self.drone_colors[drone_id]  # 128 is 50% transparency
        outline_color = "black"  # Use the solid color for outline

        # Create the polygon on the map
        polygon = self.map_widget.set_polygon(coordinates, outline_color=outline_color, fill_color=fill_color,
                                              border_width=1)
        # Store the polygon in a list or dictionary
        if drone_id not in self.polygons:
            self.polygons[drone_id] = []
        self.polygons[drone_id].append(polygon)

    def hide_geofences(self):
        """
        Removes all polygons from the map.
        """
        for drone_id in self.polygons:
            for polygon in self.polygons[drone_id]:
                polygon.delete()
        self.polygons.clear()

