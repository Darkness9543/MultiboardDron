from tkintermapview import TkinterMapView
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import math


def hex_to_rgba(hex_color, alpha=0.6):
    # Convert hex color to RGBA
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color. It should be a 6-character string.")
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    rgba = tuple(val / 255 for val in rgb) + (alpha,)
    return rgba


class EditorMap:
    def __init__(self, parent, root, drone_colors, height, width, max_drones):
        self.parent = parent
        self.map_widget = TkinterMapView(root, height=height, width=width)
        self.map_widget.grid(row=0, column=0)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", max_zoom=22)
        self.drone_colors = []
        self.max_drones = max_drones
        self.markers = [[] for _ in range(max_drones)]
        self.coords_list = [[] for _ in range(max_drones)]
        self.coords = [[] for _ in range(max_drones)]
        self.paths = [[] for _ in range(max_drones)]
        self.path = [None] * max_drones
        self.polygons = [[] for _ in range(max_drones)]
        self.polygon_count = [0] * max_drones
        self.first_point = [None] * max_drones

        self.drone_colors = drone_colors
        self.map_widget.add_left_click_map_command(lambda coords: self.print_point(coords))
        self.map_widget.add_right_click_menu_command("Delete last waypoint",self.right_click_command_delete)
        self.map_widget.add_right_click_menu_command("Finish geofence",self.right_click_command_finish)
        self.map_widget.add_right_click_menu_command("Delete marker at 0", lambda: self.delete_marker_at_position(0))
        self.map_widget.add_right_click_menu_command("Delete polygon at 2", lambda: self.delete_polygon_at_position(0))
        self.map_widget.add_right_click_menu_command("Clear",self.reset)

        self.option_delete_all = True
        self.selected_drone_index = 0

        self.map_widget.set_position(41.276448, 1.9888564)
        self.map_widget.set_zoom(20)
    def load_scenario(self, scenario):
        geofence_list = scenario.Coordinates
        for polygon in self.polygons:
            for polygon_sub in polygon:
                self.map_widget.delete(polygon_sub)
        self.polygons = [[] for _ in range(self.max_drones)]
        for i, drone_list in enumerate(geofence_list):
            self.polygon_count[i] = 0
            for shape in drone_list:
                if shape["type"] == "polygon":
                    point_list = []
                    points = shape["waypoints"]
                    for point in points:
                        point_list.append([point["lat"], point["lon"]])
                    if self.polygon_count[i] < 1:
                        fill_color = self.drone_colors[i]
                    else:
                        fill_color = "black"
                    polygon = self.map_widget.set_polygon(point_list,
                                                               fill_color=fill_color, outline_color="black",
                                                               border_width=2)
                    self.polygon_count[i] += 1
                    self.polygons[i].append(polygon)
        self.parent.show_inclusion_geofence(self.polygons[self.selected_drone_index])
        self.parent.show_exclusion_points(self.coords[self.selected_drone_index],
                                          self.polygons[self.selected_drone_index])
    def right_click_command_finish(self):
        self.click_first_marker()
    def right_click_command_delete(self):
        if len(self.markers[self.selected_drone_index]) == 1:
            self.map_widget.delete(self.first_point[self.selected_drone_index])
            self.markers[self.selected_drone_index] = []
            self.coords[self.selected_drone_index] = []
            self.first_point[self.selected_drone_index] = None
        if len(self.markers[self.selected_drone_index]) >= 2:
            marker = self.markers[self.selected_drone_index].pop()
            self.coords.pop()
            self.map_widget.delete(marker)
            self.update_path()
    def set_current_drone(self, index):
        self.selected_drone_index = index
        self.parent.show_inclusion_geofence(self.polygons[self.selected_drone_index])
        self.parent.show_exclusion_points(self.coords[self.selected_drone_index],
                                          self.polygons[self.selected_drone_index])
    def update_path(self):
        if self.path[self.selected_drone_index]:
            self.path[self.selected_drone_index].delete()

        if len(self.markers[self.selected_drone_index]) >= 2:
            path_coords = []
            for marker in self.markers[self.selected_drone_index]:
                print(marker)
                path_coords.append(marker.position)
            self.path[self.selected_drone_index] = self.map_widget.set_path(path_coords, color="blue", width=2)
    def parse_data(self):
        coordinates = []
        for entry in self.coords_list:
            if entry:
                entry_list = []
                for sub_entry in entry:
                    if sub_entry:
                        points = []
                        for point in sub_entry:
                            print(f"Point : {point}")
                            points.append({"lat": point[0], "lon": point[1]})
                        sub_list = {"type": "polygon",
                                    "waypoints": points}
                        entry_list.append(sub_list)
                coordinates.append(entry_list)
        return coordinates
    def click_first_marker(self):
        if len(self.markers[self.selected_drone_index]) >= 3:
            print("First marker clicked!")
            # Delete the existing path
            if self.path[self.selected_drone_index]:
                self.map_widget.delete(self.path[self.selected_drone_index])
                self.path[self.selected_drone_index] = None
            # Draw a polygon with the points
            if self.polygon_count[self.selected_drone_index] < 1:
                fill_color = self.drone_colors[self.selected_drone_index]
            else:
                fill_color = "black"
            self.polygon = self.map_widget.set_polygon(self.coords[self.selected_drone_index], fill_color=fill_color, outline_color="black", border_width=2)
            self.polygons[self.selected_drone_index].append(self.polygon)
            if self.polygon_count[self.selected_drone_index] == 0:
                self.parent.show_inclusion_geofence(self.polygons[self.selected_drone_index])

            self.polygon_count[self.selected_drone_index] += 1
            # Remove markers from map
            for marker in self.markers[self.selected_drone_index]:
                self.map_widget.delete(marker)
            self.markers[self.selected_drone_index] = []
            # Reset coords and first_point to start new polygon
            self.coords_list[self.selected_drone_index].append(self.coords[self.selected_drone_index])
            self.coords[self.selected_drone_index] = []
            self.first_point[self.selected_drone_index] = None

            if self.polygon_count[self.selected_drone_index] > 1:
                self.parent.show_exclusion_points(self.coords[self.selected_drone_index],
                                                  self.polygons[self.selected_drone_index])
        else:
            print("Not enough points to finish")

    def print_point(self, coords):
        lat, lon = coords
        if not self.check_marker_click(coords):
            # Add a red circle marker at the clicked location
            print(f"Selected drone index = {self.selected_drone_index}")
            print(f"Markers: {self.markers}")
            marker = self.map_widget.set_marker(lat, lon, text=str(len(self.markers[self.selected_drone_index])+1), text_color="#ff0000", font=("Helvetica",13, "bold"), icon=self.create_circle_icon())
            self.markers[self.selected_drone_index].append(marker)
            self.coords[self.selected_drone_index].append(coords)  # Add the coordinate to the list
            print(self.coords[self.selected_drone_index])
            if self.polygon_count[self.selected_drone_index] == 0:
                self.parent.show_inclusion_points(self.coords[self.selected_drone_index])
            else:
                self.parent.show_exclusion_points(self.coords[self.selected_drone_index], self.polygons[self.selected_drone_index])
            if self.first_point[self.selected_drone_index] is None:
                self.first_point[self.selected_drone_index] = marker
                marker.change_icon(self.create_circle_icon("green"))
            # Draw or update the path
            if len(self.coords[self.selected_drone_index]) > 1:
                if self.path[self.selected_drone_index]:
                    # If path exists, delete it first
                    self.map_widget.delete(self.path[self.selected_drone_index])
                self.path[self.selected_drone_index] = self.map_widget.set_path(self.coords[self.selected_drone_index], color="blue", width=2)
            else:
                # If there's only one point, ensure no path is drawn
                if self.path[self.selected_drone_index]:
                    self.map_widget.delete(self.path[self.selected_drone_index])
                    self.path[self.selected_drone_index] = None
    def delete_polygon_at_position(self, position):
        if self.option_delete_all is True:
            if position == 0:
                print("Deleting all polygons")
                for i in range(len(self.polygons[self.selected_drone_index])):
                    self.map_widget.delete(self.polygons[self.selected_drone_index][0])
                    del self.polygons[self.selected_drone_index][0]
                    self.polygon_count[self.selected_drone_index] -= 1
            else:
                self.map_widget.delete(self.polygons[self.selected_drone_index][position])
                del self.polygons[self.selected_drone_index][position]
                self.polygon_count[self.selected_drone_index] -= 1
        else:
            self.map_widget.delete(self.polygons[self.selected_drone_index][position])
            del self.polygons[self.selected_drone_index][position]
            self.polygon_count[self.selected_drone_index] -= 1

        self.parent.show_inclusion_geofence(self.polygons[self.selected_drone_index])
        self.parent.show_exclusion_points(self.coords[self.selected_drone_index],
                                          self.polygons[self.selected_drone_index])
    def delete_marker_at_position(self, position):
        if position == 0:
            self.map_widget.delete(self.markers[self.selected_drone_index][position])
            del self.markers[self.selected_drone_index][position]
            del self.coords[self.selected_drone_index][position]
            for i, marker in enumerate(self.markers[self.selected_drone_index]):
                marker.set_text(str(i+1))
            self.first_point[self.selected_drone_index] = self.markers[self.selected_drone_index][0]
            self.first_point[self.selected_drone_index].change_icon(self.create_circle_icon("green"))
            self.update_path()
        else:
            self.map_widget.delete(self.markers[self.selected_drone_index][position])
            del self.markers[self.selected_drone_index][position]
            del self.coords[self.selected_drone_index][position]
            for i, marker in enumerate(self.markers[self.selected_drone_index]):
                marker.set_text(str(i+1))
            self.update_path()
        self.parent.show_inclusion_points(self.coords[self.selected_drone_index])
        self.parent.show_exclusion_points(self.coords[self.selected_drone_index], self.polygons[self.selected_drone_index])

    def check_marker_click(self, coords):
        if self.first_point[self.selected_drone_index]:
            first_marker_coords = (self.first_point[self.selected_drone_index].position[0], self.first_point[self.selected_drone_index].position[1])
            click_distance = self.calculate_distance(coords, first_marker_coords)
            if click_distance < 1:  # Threshold in meters
                self.click_first_marker()
                return True
        return False

    def calculate_distance(self, coords1, coords2):
        # Haversine formula to calculate distance between two lat/lon points in meters
        lat1, lon1 = coords1
        lat2, lon2 = coords2
        R = 6371000  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2) ** 2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c  # Output distance in meters
        return distance

    def create_circle_icon(self, color="red"):
        # Create a red circle icon using PIL
        image = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([2, 2, 18, 18], fill=color, outline=None)
        # Convert PIL image to PhotoImage
        return ImageTk.PhotoImage(image)

    def reset(self):
        # Optional method to reset the map after drawing the polygon
        # Delete markers
        for marker in self.markers:
            self.map_widget.delete(marker)
        self.markers = []
        # Delete path
        if self.path:
            self.map_widget.delete(self.path)
            self.path = None
        # Reset coords and first_point
        self.coords[self.selected_drone_index] = []
        self.first_point[self.selected_drone_index] = None

        self.parent.show_inclusion_points(self.coords[self.selected_drone_index])
        self.parent.show_exclusion_points(self.coords[self.selected_drone_index],  self.polygons[self.selected_drone_index])

    # Other methods remain unchanged



# You can instantiate and use the EditorMap class as needed