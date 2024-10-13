import customtkinter as ctk
import GeofenceClass as Geofence
import json
import math
import time
import paho.mqtt.client as mqtt
import DroneInfoClass
import DroneMap
from geographiclib.geodesic import Geodesic
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
from typing import List, Any
from tkintermapview import TkinterMapView
import atexit

import editorMapWidget
from geofenceCardWidget import GeofenceCardWidget
from geofencePicker import geofencePicker as geoPick

class PointInstance(ctk.CTkFrame):
    def __init__(self, master, index, coord, command_callback, width: int = 200, height: int = 40,
                 fg_color: str = "", color_palette: [] = None, **kwargs):
        super().__init__(master = master)
        self.index = index
        self.coord = coord

        if color_palette is None:
            self.color_palette = ["#1E201E",
                             "#3C3D37",
                             "#697565",
                             "#ECDFCC"]
        if fg_color == "":
            fg_color = self.color_palette[2]
        self.configure(width= width, height=height, fg_color=fg_color)
        self.grid_propagate(False)

        self.label = ctk.CTkLabel(self, text_color= "white", text=f"Point {index+1}:   lat: {round(self.coord[0],7)}\n                lon: {round(self.coord[1],7)}")
        self.label.grid(row=0, column=0, pady=5, padx=10)
        self.delete_button = ctk.CTkButton(self, text_color="white", text="x", width=10, height=10, command=lambda: command_callback(self.index))
        self.delete_button.grid(row=0, column=1, pady=5, padx=5)
        self.grid(row=index, column=0, padx=10, pady=5)
class DroneInstance:
    def __init__(self,
                 index: int = 0):
        self.index = index
        self.inclusion = []
        self.exclusion = []
        self.button = None


class GeofenceEditor(ctk.CTkFrame):
    def __init__(self, parent, root, defaults, selected_geofence,
                 width: int = 800,
                 height: int = 500,
                 number_of_drones: int = 2,
                 color_palette=None):
        super().__init__(master=root)
        # Color palette

        self.parent = parent
        self.configure(width=width, height=height, fg_color="yellow")
        self.grid_propagate(False)
        if color_palette is None:
            color_palette = ["#1E201E",
                             "#3C3D37",
                             "#697565",
                             "#ECDFCC"]

        self.set_one = color_palette[0]
        self.set_two = color_palette[1]
        self.set_three = color_palette[2]
        self.set_four = color_palette[3]

        self.button_color = self.set_four

        self.defaults = defaults
        self.drone_colors = defaults[2]
        self.max_drones = defaults[3]
        self.width = width
        self.height = height
        self.grid(row=0, column=0, pady=(40, 0))
        self.point_instances = []
        self.input_frame_percent_height = 0.1
        self.percent_map_width = 0.7
        self.percent_drone_selection_height = 0.3
        self.create_input_frame()
        self.create_drone_selection_frame()
        self.create_points_register_frame()
        self.create_map_frame()
        self.drone_instances = []
        self.initialize_drone_selection()
        self.selected_drone = None

    def create_input_frame(self):
        self.input_frame = ctk.CTkFrame(self, width=self.width,
                                        height=int(self.height * self.input_frame_percent_height),
                                        fg_color="cyan")
        self.input_frame.grid(row=0, column=0, columnspan=2)
        self.input_frame.grid_propagate(False)
        self.initialize_input_options()

    def create_drone_selection_frame(self):
        self.drone_selection_frame = ctk.CTkFrame(self, fg_color="blue",
                                                  width=int(self.width * (1 - self.percent_map_width)),
                                                  height=int(self.height * self.percent_drone_selection_height))
        self.drone_selection_frame.grid(row=1, column=1)
        self.drone_selection_frame.grid_propagate(False)

        drone_selection_frame = ctk.CTkScrollableFrame(self.drone_selection_frame, fg_color="blue",
                                                       width=int(self.width * (1 - self.percent_map_width)),
                                                       height=int(self.height * self.percent_drone_selection_height))
        drone_selection_frame.grid(row=0, column=0)
        self.drone_selection_frame_scrolleable = drone_selection_frame

    def create_points_register_frame(self):
        width = int(self.width * (1 - self.percent_map_width))
        height = int(self.height * (1 - self.percent_drone_selection_height - self.input_frame_percent_height))
        self.point_register_frame = ctk.CTkFrame(self, fg_color="orange",
                                                 width= width,
                                                 height=height)
        self.point_register_frame.grid(row=2, column=1)
        self.point_register_frame.grid_propagate(False)

        self.create_points_register(width, height)



    def create_map_frame(self):
        width = int(self.width * self.percent_map_width)
        height = int(self.height * (1 - self.input_frame_percent_height))
        self.map_frame = ctk.CTkFrame(self,
                                      width=width,
                                      height=height)
        self.map_frame.grid(row=1, column=0, rowspan=2)
        self.map_frame.grid_propagate(False)

        self.editor_map = editorMapWidget.EditorMap(self, self.map_frame, self.drone_colors, height, width, self.max_drones)

    # Input options

    def initialize_input_options(self):
        # Name option
        self.name_frame = ctk.CTkFrame(self.input_frame, width=200, height=50, fg_color=self.set_three)
        self.name_label = ctk.CTkLabel(self.name_frame, text="Name", text_color="black", fg_color="transparent")
        self.name_textbox = ctk.CTkEntry(self.name_frame, width=150, height=20)
        self.name_label.grid(row=0, column=0, padx=5, pady=5)
        self.name_textbox.grid(row=0, column=1, padx=5, pady=5)

        # Is favourite option

        self.favourite_frame = ctk.CTkFrame(self.input_frame, width=200, height=50, fg_color=self.set_three)
        self.favourite_label = ctk.CTkLabel(self.favourite_frame, text="Is favourite?", text_color="black")
        self.favourite_checkbox = ctk.CTkCheckBox(self.favourite_frame, width=150, height=40, text="")
        self.favourite_label.grid(row=0, column=0, padx=5, pady=5)
        self.favourite_checkbox.grid(row=0, column=1, padx=5, pady=5)

        # Number of drones option

        self.number_drones_frame = ctk.CTkFrame(self.input_frame, width=200, height=50, fg_color=self.set_three)
        self.number_drones_label = ctk.CTkLabel(self.number_drones_frame, text="Number drones", text_color="black")
        self.number_drones_slider = ctk.CTkSlider(self.number_drones_frame, from_=1, to=self.defaults[3],
                                                  number_of_steps=self.defaults[3] - 1,
                                                  width=100)
        self.number_drones_label.grid(row=0, column=0, padx=5, pady=5)
        self.number_drones_slider.grid(row=0, column=1, padx=5, pady=5)
        self.number_display_label = ctk.CTkLabel(self.number_drones_frame, text="1", text_color="black")

        self.number_drones_slider.configure(
            command=lambda value: self.update_value_slider(value))
        self.number_drones_slider.set(1)
        self.name_frame.grid(row=0, column=0, padx=10, pady=10)
        self.favourite_frame.grid(row=0, column=1, padx=10, pady=10)
        self.number_display_label.grid(row=0, column=2, padx=4, pady=10)
        self.number_drones_frame.grid(row=0, column=2, padx=10, pady=10)

    # Drone selection

    def initialize_drone_selection(self):
        for i in range(self.defaults[3]):
            self.drone_instances.append(DroneInstance(index=i))
            drone_button = ctk.CTkButton(self.drone_selection_frame_scrolleable, width=200, height=40,
                                         text=f"Drone {i + 1}", fg_color=self.button_color, text_color="black",
                                         command=lambda i=i: self.drone_button_selected(i))
            drone_button.grid(row=i, column=0, padx=20, pady=10)
            self.drone_instances[i].button = drone_button
        self.update_drone_selection(int(self.number_drones_slider.get()))

    def drone_button_selected(self, index):
        self.update_drone_selection(int(self.number_drones_slider.get()))
        self.highlight_button(index)
        self.selected_drone = self.drone_instances[index]
        self.editor_map.set_current_drone(index)

    def highlight_button(self, index):
        for drone in self.drone_instances:
            if drone.index is index:
                drone.button.configure(fg_color="grey")
            else:
                drone.button.configure(fg_color=self.button_color)

    def update_drone_selection(self, num_drones):
        for i, drone in enumerate(self.drone_instances):
            print(f"i= {i}    drone= {drone.index}")
            if drone.index < num_drones:
                drone.button.grid(row=i, column=0, padx=10, pady=10)
            else:
                drone.button.grid_forget()
        pass

    def update_value_slider(self, value):
        self.number_display_label.configure(text=str(int(value)))
        self.update_drone_selection(value)

    # Point register

    def create_points_register(self, parent_width, parent_height):
        proportion = 0.4
        padx, pady = 10, 10
        self.inclusion_scrolleable_frame = ctk.CTkScrollableFrame(self.point_register_frame,
                                                                  width=int(parent_width- 4*padx),
                                                                  height = int(proportion*(parent_height- 7*pady)))
        self.exclusion_scrolleable_frame = ctk.CTkScrollableFrame(self.point_register_frame,
                                                                  width=int(parent_width - 4 * padx),
                                                                  height=int((1-proportion) * (parent_height - 7 * pady)))
        self.inclusion_scrolleable_frame.grid(row=0, column=0, padx=padx, pady=pady)
        self.exclusion_scrolleable_frame.grid(row=1, column=0, padx=padx, pady=(0, pady))
    def print_callback(self, index):
        print(f"Callback {index}")
        pass
    def show_inclusion_points(self, coords):
        print(f"Show inclusion points: {coords}")
        for point in self.point_instances:
            point.destroy()
        self.point_instances = []
        for i, coord in enumerate(coords):
            point_instance = PointInstance(self.inclusion_scrolleable_frame, i,coord, self.print_callback)
            self.point_instances.append(point_instance)
        pass

