from tkintermapview import TkinterMapView
from PIL import Image, ImageTk, ImageDraw
import math
class DroneMap:
    def __init__(self, parent, height, width):
        self.map_widget = TkinterMapView(parent, height=height, width=width)
        self.map_widget.grid(row=0, column=0)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", max_zoom=22)

        # Set initial position and zoom level
        self.map_widget.set_position(41.276448, 1.9888564)
        self.map_widget.set_zoom(20)

        # Dictionary to store markers
        self.markers = {}

        # Load the arrow image
        self.marker_image = Image.open("assets/dronaArrow.png")
        original_width, original_height = self.marker_image.size
        new_size = (original_width // 15, original_height // 15)
        self.marker_image = self.marker_image.resize(new_size, Image.LANCZOS)

        # Load the arrow image and create the combined image
        self.marker0_image = self.create_combined_marker_image("assets/dronaArrow.png", "red")
        self.marker1_image = self.create_combined_marker_image("assets/dronaArrow.png", "blue")
        self.marker2_image = self.create_combined_marker_image("assets/dronaArrow.png", "green")
        self.marker3_image = self.create_combined_marker_image("assets/dronaArrow.png", "yellow")
        self.marker_images = [self.marker0_image, self.marker1_image, self.marker2_image, self.marker3_image]
        self.marker_color = ["red", "blue", "green", "yellow"]

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

