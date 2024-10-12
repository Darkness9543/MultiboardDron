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
from typing import List
from tkintermapview import TkinterMapView
import atexit

import colorCircle
from geofenceCardWidget import GeofenceCardWidget
import droneFrame


def get_connection_data(json_file_path="data/defaults.json"):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        connection_strings = data.get('connection_strings', [])
        ports = data.get('ports', [])

        return connection_strings, ports
    except FileNotFoundError:
        print(f"Error: The file {json_file_path} was not found.")
        return [], []
    except json.JSONDecodeError:
        print(f"Error: The file {json_file_path} contains invalid JSON.")
        return [], []
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return [], []


class droneSelectionWidget(ctk.CTkFrame):
    def __init__(self, parent, root, defaults,
                 color_palette=None):
        super().__init__(master=root)
        self.parent = parent
        self.root = root
        # Color palette
        self.color_palette = []
        if color_palette is None:
            self.color_palette = ["#1E201E",
                                  "#3C3D37",
                                  "#697565",
                                  "#ECDFCC"]

        self.set_one = self.color_palette[0]
        self.set_two = self.color_palette[1]
        self.set_three = self.color_palette[2]
        self.set_four = self.color_palette[3]

        # Common variables

        self.default_connection_data = defaults[0]
        self.default_port_data = defaults[1]
        print(defaults[2])
        self.drone_colors = defaults[2]

        self.is_sim = True
        self.drone_selection_frame_color = self.set_two
        self.MAX_DRONES = 10
        self.drone_frames = []

        # Drone number selector

        self.drone_number_label = None

        # Initializing

        self.create_main_frame()
        self.set_color_palette()
        self.create_drone_number_selector()
        self.create_drone_configuration_list()
        self.update_ui(1)

    def update_based_on_geofence(self, geofence):
        self.update_ui(geofence.DroneCount)
        pass

    def create_drone_number_selector(self):
        # Create and place the label
        self.drone_number_label = ctk.CTkLabel(self, text="Number of drones: 1")
        self.drone_number_label.pack(pady=10)

        # Create and configure the slider
        self.drone_number_slider = ctk.CTkSlider(
            self,
            from_=1,
            to=self.MAX_DRONES,
            number_of_steps=self.MAX_DRONES - 1,  # Ensures step increments of 1
            command=self.on_slider_move  # Callback when slider is moved
        )
        self.drone_number_slider.set(1)  # Initialize slider to 1
        self.drone_number_slider.pack(pady=10)

        # Create and place the textbox
        self.drone_number_textbox = ctk.CTkEntry(
            self,
            placeholder_text="Enter number of drones"
        )
        self.drone_number_textbox.pack(pady=10)
        self.drone_number_textbox.bind("<Return>", self.on_textbox_enter)  # Bind Enter key to validation



    def create_drone_configuration_list(self):
        # Create and pack the scrollable frame below the selector
        self.drone_config_scrollable = ctk.CTkScrollableFrame(
            self,
            fg_color=self.set_one,
            width=320,
            height=500  # Adjust height as needed
        )
        self.drone_config_scrollable.pack(pady=10, padx=10, fill="both", expand=True)

    def on_textbox_enter(self, event):
        user_input = self.drone_number_textbox.get().strip()
        if self.validate_input(user_input):
            number = int(user_input)
            if number > self.MAX_DRONES:
                number = self.MAX_DRONES
            elif number < 1:
                number = 1  # Enforce a minimum value of 1
            self.update_ui(number)
        else:
            # Optionally, you can provide feedback to the user about invalid input
            self.drone_number_textbox.delete(0, ctk.END)
            self.drone_number_textbox.insert(0, "1")  # Reset to default
            self.update_ui(1)

    def on_slider_move(self, value):
        number = int(round(value))
        self.update_ui(number)

    def validate_input(self, input_str):
        try:
            number = int(input_str)
            if 1 <= number <= self.MAX_DRONES:
                return True
            else:
                return False
        except ValueError:
            return False

    def update_ui(self, number):
        # Update label
        self.drone_number_label.configure(text=f"Number of drones: {number}")

        # Update slider without triggering the callback
        self.drone_number_slider.set(number)

        # Update textbox without triggering any events
        self.drone_number_textbox.delete(0, ctk.END)
        self.drone_number_textbox.insert(0, str(number))

        # Update drone configuration frames
        self.update_drone_configurations(number)

    def update_drone_configurations(self, number):
        current_count = len(self.drone_frames)
        if number > current_count:
            # Add new drone frames
            for i in range(current_count + 1, number + 1):
                frame = droneFrame.droneFrame(self.drone_config_scrollable,
                                              i,
                                              self.color_palette,
                                              self.on_switch_toggle,
                                              self.is_sim,
                                              self.drone_colors[i-1])

                frame.switch_port_sim(self.default_port_data[i - 1], self.default_connection_data[i - 1], self.is_sim)
                self.drone_frames.append(frame)
        elif number < current_count:
            # Remove excess drone frames
            for _ in range(current_count - number):
                print(_)
                frame = self.drone_frames.pop()
                frame.destroy()


    def on_switch_toggle(self):
        """
        Optional: Handle switch toggle events if additional actions are needed.

        Parameters:
            var (StringVar): The variable associated with the switch.
            switch (CTkSwitch): The switch widget.
        """
        # This function can be expanded based on specific requirements
        pass

    def create_main_frame(self):

        self.configure(height=900,
                       width=350 + 0,
                       fg_color=self.set_three)

        # Place the frame
        self.grid(
            row=0,
            column=0,
            sticky='nw',
            padx=(10, 5),
            pady=(10, 200)
        )
        self.grid_propagate(False)

    def set_color_palette(
            self,
            drone_selection_frame_color=None
    ):
        # Assign default colors if parameters are not provided
        drone_selection_frame_color = drone_selection_frame_color or self.drone_selection_frame_color

        # Configure Geofence Frame
        self.configure(fg_color=drone_selection_frame_color)

    def blend_colors(self, color1, color2, opacity):
        """
        Blends two hex colors based on the given opacity.

        Parameters:
            color1 (str): The hex color code of the foreground color (e.g., "#RRGGBB").
            color2 (str): The hex color code of the background color (e.g., "#RRGGBB").
            opacity (float): The opacity percentage for color1 (0.0 to 1.0).

        Returns:
            str: The blended hex color code.
        """
        # Remove the '#' character if present
        color1 = color1.lstrip('#')
        color2 = color2.lstrip('#')

        # Convert hex to RGB
        r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
        r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)

        # Calculate blended RGB
        r = int(r1 * opacity + r2 * (1 - opacity))
        g = int(g1 * opacity + g2 * (1 - opacity))
        b = int(b1 * opacity + b2 * (1 - opacity))

        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'

    def switch_port_sim(self):
        if self.is_sim:
            self.is_sim = False
        else:
            self.is_sim = True
        self.update_port_label(self.is_sim)

    def update_port_label(self, simBool):
        index = 0
        for drone_frame in self.drone_frames:
            drone_frame.switch_port_sim(self.default_port_data[index], self.default_connection_data[index], simBool)
            index += 1

    def get_connection_ports(self):
        connection_ports = []
        for drone_frame in self.drone_frames:
            connection_ports.append(drone_frame.port_textbox.get())
        return connection_ports
