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

class GeofenceCardWidget(ctk.CTkFrame):
    def __init__(self, root, geofence, geofence_selected_callback, drone_colors,
                 width: int = 274,
                 height: int = 204,
                 fg_color: str = "black"):
        super().__init__(master=root)
        self.root = root
        self.width = width
        self.height = height
        self.fg_color = fg_color
        self.geofence = geofence
        self.configure(fg_color=self.fg_color, width=self.width, height=self.height)
        self.grid_propagate(False)

        drone_colors = hex_to_rgba(drone_colors)
        self.map_image, center_position = gml.create_map_image(geofence_vector=self.geofence.Coordinates, colors=drone_colors)
        self.map_image_CTk = CTkImage(light_image=self.map_image, dark_image=self.map_image, size=(200, 180))
        self.button = ctk.CTkButton(self,
                                    fg_color="#baaea6",
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

    def hide(self):
        self.grid_remove()


    def highlight(self):
        self.button.configure(fg_color="#b7b888")

    def unhighlight(self):
        self.button.configure(fg_color="#baaea6")

    def set_fg_button_color(self, color):
        self.button.configure(fg_color=color)

    def set_fg_count_color(self, color):
        self.count.configure(fg_color=color)
