import customtkinter as ctk
from customtkinter import CTkImage

import geofenceMapLib as gml
import json
import math
import time
import paho.mqtt.client as mqtt
import DroneInfoClass
import DroneMap
from geographiclib.geodesic import Geodesic
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
from typing import List
from tkintermapview import TkinterMapView
from GeofenceClass import Geofence
import atexit
from confirmationPopUp import ConfirmationPopup


def transform_coordinates(input_data):
    geofence_vector = []

    for polygon in input_data:
        transformed_polygon = []
        for point in polygon:
            transformed_polygon.append([point['lat'], point['lon']])
        geofence_vector.append(transformed_polygon)

    return geofence_vector


def hex_to_rgba(hex_colors, alpha=128):
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    rgba_colors = []
    for hex_color in hex_colors:
        rgb = hex_to_rgb(hex_color)
        rgba_colors.append((*rgb, alpha))

    return rgba_colors


def brighten_color(hex_color, percent):
    """
    Brighten a color by a given percentage.

    :param hex_color: A string representing the color in hex format (e.g., '#FF8000')
    :param percent: The percentage to brighten the color (0-100)
    :return: A string representing the brightened color in hex format
    """
    # Remove the '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert hex to RGB
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # Calculate the brightness factor
    factor = 1 + (percent / 100)

    # Brighten each channel
    r = min(round(r * factor), 255)
    g = min(round(g * factor), 255)
    b = min(round(b * factor), 255)

    # Convert back to hex
    return f'#{r:02x}{g:02x}{b:02x}'


class GeofenceCardWidget(ctk.CTkFrame):
    def __init__(self, root, parent, geofence, geofence_selected_callback, drone_colors,
                 width: int = 274,
                 height: int = 204,
                 fg_color: str = "black",
                 color_palette: list[str] = None):
        super().__init__(master=root)
        if color_palette is None:
            color_palette = ["#1E201E",
                             "#3C3D37",
                             "#697565",
                             "#ECDFCC"]
        self.parent = parent
        self.set_one = color_palette[0]
        self.set_two = color_palette[1]
        self.set_three = color_palette[2]
        self.set_four = color_palette[3]
        self.root = root
        self.width = width
        self.height = height
        self.fg_color = fg_color
        self.geofence = geofence
        self.drone_colors = drone_colors

        self.normal_color = brighten_color(self.set_four, -25)
        self.bright_color = brighten_color(self.set_four, 50)
        self.delete_button = None
        self.configure(fg_color=self.fg_color, width=self.width, height=self.height)
        self.grid_propagate(False)
        drone_colors = hex_to_rgba(drone_colors)
        self.map_image, center_position = gml.create_map_image(geofence_vector=self.geofence.Coordinates,
                                                               colors=drone_colors)
        self.map_image_CTk = CTkImage(light_image=self.map_image, dark_image=self.map_image, size=(200, 180))
        self.button = ctk.CTkButton(self,
                                    fg_color=self.normal_color,
                                    text_color="black",
                                    hover_color="#e1edd8",
                                    text=geofence.Name,
                                    width=270,
                                    height=200,
                                    image=self.map_image_CTk,
                                    compound="bottom")
        self.button.configure(command=lambda: geofence_selected_callback(self.geofence))
        self.button.grid_propagate(False)
        self.button.grid(row=0, column=0, padx=2, pady=2)
        self.button.image = self.map_image_CTk

        self.count = ctk.CTkButton(self,
                                   fg_color="#2e1200",
                                   bg_color="#baaea6",
                                   text_color="white",
                                   width=20,
                                   text=str(geofence.DroneCount),
                                   hover=False, state="disabled")
        self.count.grid(row=0, column=0, sticky="ne", padx=5, pady=5)
        self.add_delete_option()

    def update_image(self, geofence_coordinates):
        map_image, center_position = gml.create_map_image(geofence_vector=geofence_coordinates,
                                                          colors=self.drone_colors)
        map_image_CTk = CTkImage(light_image=map_image, dark_image=map_image, size=(200, 180))
        self.button.configure(image=map_image_CTk)

    def hide(self):
        self.grid_remove()

    def highlight(self):
        self.button.configure(fg_color=self.bright_color)
        if self.delete_button is not None:
            self.delete_button.configure(fg_color=self.bright_color, bg_color=self.bright_color)

    def unhighlight(self):
        self.button.configure(fg_color=self.normal_color)
        if self.delete_button is not None:
            self.delete_button.configure(fg_color=self.normal_color, bg_color=self.normal_color)

    def set_fg_button_color(self, color):
        self.button.configure(fg_color=color)

    def set_fg_count_color(self, color):
        self.count.configure(fg_color=color)

    def add_delete_option(self):
        delete_image = ImageTk.PhotoImage(Image.open("assets/delete_image.png").resize((25, 25)))
        self.delete_button = ctk.CTkButton(self.button, width=30, height=30, fg_color="transparent", image=delete_image,
                                           text="", command=self.confirmation_test)
        self.delete_button.grid_propagate(False)
        self.delete_button.place(x=2, y=2)

    def confirmation_test(self):
        self.button.grid_forget()
        self.count.grid_forget()
        self.confirm_panel = ctk.CTkFrame(self,
                                          width=self.width,
                                          height=self.height,
                                          fg_color=self.set_two, corner_radius=0)
        self.confirm_label = ctk.CTkLabel(self.confirm_panel,
                                          fg_color="transparent",
                                          text="Are you sure you want to delete this scenario?",
                                          text_color="white",
                                          font=("Helvetica", 11, "bold"))
        self.yes_button = ctk.CTkButton(self.confirm_panel,
                                        width=100, height=40,
                                        text="Yes", fg_color=self.set_four, text_color="black",
                                        command=self.delete_scenario)
        self.no_button = ctk.CTkButton(self.confirm_panel,
                                       width=100, height=40,
                                       text="No", fg_color=self.set_four, text_color="black",
                                       command=self.cancel_delete)
        self.confirm_panel.grid_propagate(False)
        self.confirm_panel.grid(row=0, column=0)
        self.confirm_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(50,10))
        self.yes_button.grid(row=1, column=0)
        self.no_button.grid(row=1, column=1)
    def cancel_delete(self):
        self.button.grid(row=0, column=0, padx=2, pady=2)
        self.count.grid(row=0, column=0, sticky="ne", padx=5, pady=5)
        self.confirm_panel.destroy()
    def delete_scenario(self):
        geofence_name = self.geofence.Name
        try:
            with open("data/GeofenceData.json", 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print("File Not Found", "GeofenceData.json does not exist.")
            return
        except json.JSONDecodeError:
            print("JSON Error", "Failed to decode GeofenceData.json. Please check the file format.")
            return

        geofence_list = data.get("GeofenceList", [])

        geofence_to_delete = None
        for geofence in geofence_list:
            if geofence.get("name") == geofence_name:
                geofence_to_delete = geofence
                break

        if not geofence_to_delete:
            print("Not Found", f"No scenario named '{geofence_name}' was found.")
            return

        geofence_list.remove(geofence_to_delete)
        data["GeofenceList"] = geofence_list  # Update the data dictionary

        try:
            with open('data/GeofenceData.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("Success", f"Scenario '{geofence_name}' has been deleted successfully.")
        except IOError as e:
            print("File Error", f"An error occurred while deleting the scenario: {e}")
        self.parent.update_geofences_root()
