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

import geofenceEditorView
from geofenceCardWidget import GeofenceCardWidget
from geofencePicker import geofencePicker as geoPick


class geofenceEditorWidget(ctk.CTkFrame):
    def __init__(self, parent, root, defaults, selected_geofence,
                 width: int = 800,
                 height: int = 500,
                 number_of_drones: int = 2,
                 color_palette=None):
        super().__init__(master=root)
        # Color palette
        self.parent = parent
        if color_palette is None:
            color_palette = ["#1E201E",
                             "#3C3D37",
                             "#697565",
                             "#ECDFCC"]

        self.set_one = color_palette[0]
        self.set_two = color_palette[1]
        self.set_three = color_palette[2]
        self.set_four = color_palette[3]
        self.defaults = defaults
        self.drone_colors = defaults[2]
        self.width = width
        self.height = height
        self.geofence_frame_color = self.set_two
        self.search_widget_color = self.set_one
        self.geofence_viewport_widget_color = self.set_one

        self.number_filter_buttons_color = self.set_four
        self.fav_filter_button_color = self.set_four
        self.drone_count_color = self.set_one

        self.scrollable_widget_color = self.set_one
        self.geofence_card_primary_color = self.set_three  # Whit

        # Initialization

        self.geofence_list = []
        self.number_of_drones = number_of_drones
        self.number_drones_selection_button_list: List[ctk.CTkButton] = []
        self.root = root

        # Search widget variables

        self.search_box = None
        self.search_widget = None
        self.is_fav_selected = False
        self.number_filter = 0
        self.geofence_card_list = []
        self.scrollable_widget = None

        # Geofence viewport variables

        self.geofence_image = None
        self.geofence_viewport_widget = None

        # Creating the main view
        self.load_geofence_list()
        self.create_main_frame()
        self.create_left_side_content()
        self.create_geofence_editor_viewport()
        self.set_color_palette()

    def geofence_selected(self, geofence):
        for card in self.geofence_card_list:
            if card.geofence.Name == geofence.Name:
                card.highlight()
                self.draw_geofence(card)
            else:
                card.unhighlight()
        self.parent.on_geofence_selected(geofence)
    def create_left_side_content(self):
        self.side_frame = ctk.CTkFrame(self, fg_color=self.set_two)
        self.side_frame.pack(pady=(10, 10), padx=5, fill="y", expand=True, side="left")



        self.fence_picker = geoPick(self, self.side_frame, self.defaults)
        self.fence_picker.grid(pady=(0, 10), padx=5, column=0, row=1, columnspan=10)
        self.fence_picker.grid_propagate(False)


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

    def create_geofence_cards(self):
        for geofence in self.geofence_list:
            card = GeofenceCardWidget(self.scrollable_widget, geofence, self.geofence_selected, self.drone_colors)
            self.geofence_card_list.append(card)

    def create_main_frame(self):
        self.configure(height=self.height,
                       width=self.width,
                       fg_color="green")
        self.pack(pady=(10, 10), padx=10, fill="both", expand=True)
        self.grid_propagate(False)

    def create_geofence_editor_viewport(self,
                                        width=928,
                                        height=550,
                                        fg_color="red"):
        self.geofence_viewport_widget = ctk.CTkFrame(self,
                                                     width=width,
                                                     height=height,
                                                     fg_color=fg_color)
        self.geofence_viewport_widget.pack(pady=(10, 10), padx=(0,10), fill="both", expand=True, side="right")
        self.geofence_viewport_widget.grid_propagate(False)
        self.geofence_viewport_widget.update()
        self.geofence_viewport_widget.update_idletasks()
        self.parent.update_root()
        self.update()
        self.update_idletasks()
        self.geofence_editor = geofenceEditorView.GeofenceEditor(self, self.geofence_viewport_widget,
                                                                 self.defaults,
                                                                 None,
                                                                 width=928,
                                                                 height=870)
        self.new_button = ctk.CTkButton(self.geofence_viewport_widget,
                                        height=20,
                                        width=60,
                                        fg_color=self.set_four,
                                        text="New",
                                        text_color="black")
        self.new_button.place(x=10, y=10)

        self.save_button = ctk.CTkButton(self.geofence_viewport_widget,
                                         height=20,
                                         width=60,
                                         fg_color=self.set_four,
                                         text="Save",
                                         text_color="black")
        self.save_button.place(x=75, y=10)

        self.delete_button = ctk.CTkButton(self.geofence_viewport_widget,
                                           height=20,
                                           width=60,
                                           fg_color=self.set_four,
                                           text="Delete",
                                           text_color="black")
        self.delete_button.place(x=140, y=10)


    def draw_geofence(self, card,
                      width=int(928 * 0.95),
                      height=int(550 * 0.95)):
        image = ctk.CTkImage(light_image=card.map_image, dark_image=card.map_image, size=(width, height))
        self.geofence_image.configure(image=image, compound="center")

    def set_color_palette(
            self,
            geofence_frame_color=None,
            geofence_viewport_widget_color=None,
            search_widget_color=None,
            number_filter_buttons_color=None,
            fav_filter_button_color=None,
            scrollable_widget_color=None,
            geofence_card_primary_color=None,
            drone_count_color=None
    ):
        pass
