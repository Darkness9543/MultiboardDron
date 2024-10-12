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


class geofencePicker(ctk.CTkFrame):
    def __init__(self, parent, root, defaults,
                 width: int=350,
                 height: int=600,
                 number_of_drones: int = 2,
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
        self.width = width
        self.height = height

        self.default_connection_data = defaults[0]
        self.default_port_data = defaults[1]
        print(defaults[2])
        self.drone_colors = defaults[2]

        self.is_sim = True
        self.drone_selection_frame_color = self.set_two
        self.MAX_DRONES = 10
        self.drone_frames = []
        self.grid_propagate(False)
        self.geofence_card_list = []

        # Drone number selector

        self.drone_number_label = None

        # geofence selection

        self.number_of_drones = number_of_drones

        self.geofence_list = []
        self.is_fav_selected = False
        self.scrollable_widget = None
        self.geofence_card_primary_color = self.set_three
        self.drone_count_color = self.set_one
        self.number_filter = 1


        # Initializing

        self.create_main_frame()
        self.set_color_palette()
        self.load_geofence_list()
        self.create_geofence_picker_list()
        self.create_search_widget()





    def create_geofence_picker_list(self):
        # Create and pack the scrollable frame below the selector

        # Create the scrollable frame
        self.scrollable_widget = ctk.CTkScrollableFrame(
            self,
            fg_color=self.set_one,
            width=310,
            height=820  # Initial height
        )

        self.scrollable_widget.grid(row=1, column=0, sticky="w", padx=(10, 10), pady=(10, 5))


    def validate_input(self, input_str):
        try:
            number = int(input_str)
            if 1 <= number <= self.MAX_DRONES:
                return True
            else:
                return False
        except ValueError:
            return False


    def on_switch_toggle(self):
        """
        Optional: Handle switch toggle events if additional actions are needed.

        Parameters:
            var (StringVar): The variable associated with the switch.
            switch (CTkSwitch): The switch widget.
        """
        # This function can be expanded based on specific requirements
        pass

    def create_geofence_cards(self):
        for geofence in self.geofence_list:
            card = GeofenceCardWidget(self.scrollable_widget, geofence, self.geofence_selected, self.drone_colors)
            self.geofence_card_list.append(card)

    def geofence_selected(self, geofence):
        for card in self.geofence_card_list:
            if card.geofence.Name == geofence.Name:
                card.highlight()
                self.draw_geofence(card)
            else:
                card.unhighlight()
        self.parent.on_geofence_selected(geofence)

    def create_search_widget(self):
        def fav_button_clicked(fav_button, fav_off_image, fav_on_image):
            if not self.is_fav_selected:
                fav_button.configure(image=fav_on_image)
                self.is_fav_selected = True
            else:
                fav_button.configure(image=fav_off_image)
                self.is_fav_selected = False

            filter_geofence_list()

        def create_favourite_button():
            fav_off_image = ImageTk.PhotoImage(Image.open("assets/FavIconOff.png").resize((20, 20)))
            fav_on_image = ImageTk.PhotoImage(Image.open("assets/FavIconOn.png").resize((20, 20)))
            self.fav_button = ctk.CTkButton(self,
                                            height=30,
                                            width=20,
                                            text="",
                                            image=fav_off_image,
                                            fg_color="#d4cdcb")
            self.fav_button.image_off = fav_off_image
            self.fav_button.image_on = fav_on_image
            self.fav_button.configure(command=lambda: fav_button_clicked(self.fav_button, fav_off_image, fav_on_image))
            self.fav_button.grid(row=0, column=0, sticky="w", padx=(20, 10), pady=(20, 5))

        def filter_geofence_list():
            geofence_list = []
            for geofence in self.geofence_list:
                if self.number_filter == 0:
                    if self.is_fav_selected:
                        if geofence.IsGeofenceFav == self.is_fav_selected:
                            geofence_list.append(geofence)
                    else:
                        geofence_list.append(geofence)
                elif geofence.DroneCount == self.number_filter:
                    if self.is_fav_selected:
                        if geofence.IsGeofenceFav == self.is_fav_selected:
                            geofence_list.append(geofence)
                    else:
                        geofence_list.append(geofence)
            display_geofence_list(geofence_list)

        def display_geofence_list(geofence_list):
            if len(geofence_list) > 0:
                index = 0
                for card in self.geofence_card_list:
                    card.hide()
                for geofence in geofence_list:
                    for card in self.geofence_card_list:
                        if geofence.Name == card.geofence.Name:
                            card.grid(row=index, column=0, padx=5, pady=3)
                            index+=1

            else:
                for card in self.geofence_card_list:
                    card.hide()

        self.is_fav_selected = False
        self.number_filter = 0


        # Search box

        search_box = ctk.CTkTextbox(self, height=20, width=200)
        search_box.grid(row=0, column=0, padx=(70, 0), pady=(20, 5), sticky="w")

        # Creating buttons...
        # - Reset filters
        # - Favourite

        create_favourite_button()

        # Loading geofence data

        self.create_geofence_cards()
        display_geofence_list(self.geofence_list)
    def load_geofence_list(self):
        file = open('data/GeofenceData.json')
        data = json.load(file)
        geofence_list = []
        for i in data['GeofenceList']:
            Values = i.values()
            drone_count = list(Values)[0]
            name = list(Values)[1]
            is_fav = list(Values)[2]
            coordinates = list(Values)[3]
            geofence = Geofence.Geofence(
                drone_count,
                name,
                is_fav,
                coordinates)
            geofence_list.append(geofence)
        self.geofence_list = geofence_list
        print ("N geofences", len(geofence_list))

    def create_main_frame(self):

        self.configure(height=900,
                       width=350 + 0,
                       fg_color=self.set_three)

        # Place the frame


    def set_color_palette(
            self,
            drone_selection_frame_color=None,
            geofence_card_primary_color=None,
            drone_count_color=None
    ):
        # Assign default colors if parameters are not provided
        drone_selection_frame_color = drone_selection_frame_color or self.drone_selection_frame_color
        geofence_card_primary_color = geofence_card_primary_color or self.geofence_card_primary_color
        drone_count_color = drone_count_color or self.drone_count_color

        # Configure Geofence Frame
        self.configure(fg_color=drone_selection_frame_color)

        for card in self.geofence_card_list:
            card.set_fg_button_color(geofence_card_primary_color)
            card.set_fg_count_color(drone_count_color)

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
