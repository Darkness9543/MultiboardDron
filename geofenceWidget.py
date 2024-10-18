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
from geofenceCardWidget import GeofenceCardWidget


class geofenceViewWidget(ctk.CTkFrame):
    def __init__(self, parent, root, defaults,
                 number_of_drones: int = 4,
                 color_palette=None):
        super().__init__(master=root)
        # Color palette
        self.parent = parent
        if color_palette is None:
            color_palette = ["#1E201E",
                             "#3C3D37",
                             "#697565",
                             "#ECDFCC"]

        set_one = color_palette[0]
        set_two = color_palette[1]
        set_three = color_palette[2]
        set_four = color_palette[3]

        self.drone_colors = defaults[2]

        self.geofence_frame_color = set_two
        self.search_widget_color = set_one
        self.geofence_viewport_widget_color = set_one

        self.number_filter_buttons_color = set_four
        self.fav_filter_button_color = set_four
        self.drone_count_color = set_one

        self.scrollable_widget_color = set_one
        self.geofence_card_primary_color = set_three  # White

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
        self.create_search_widget()
        self.create_geofence_viewport()
        self.set_color_palette()
    def update_geofences(self):
        self.load_geofence_list()
        for geofence_card in self.geofence_card_list:
            geofence_card.destroy()
        self.geofence_card_list = []
        self.create_geofence_cards()


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
            self.fav_button = ctk.CTkButton(self.search_widget,
                                            height=30,
                                            width=20,
                                            text="",
                                            image=fav_off_image,
                                            fg_color="#d4cdcb")
            self.fav_button.image_off = fav_off_image
            self.fav_button.image_on = fav_on_image
            self.fav_button.configure(command=lambda: fav_button_clicked(self.fav_button, fav_off_image, fav_on_image))
            self.fav_button.grid(row=0, column=0, sticky="w", padx=(10, 10), pady=(5, 0))

        def filter_by_number(number):
            self.number_filter = number
            index = 0
            for i in self.number_drones_selection_button_list:
                i.configure(state="normal", fg_color="#feffd4",
                            text_color="black", hover_color="#c9c1a3",
                            hover=True, font=("Helvetica", 16, "bold"))
                if index == number:
                    i.configure(state="disabled", fg_color="#d1a019", text_color_disabled="black")
                index += 1

            filter_geofence_list()

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
                            card.grid(row=0, column=index, padx=3, pady=5)
                            index += 1

            else:
                for card in self.geofence_card_list:
                    card.hide()

        self.is_fav_selected = False
        self.number_filter = 0

        # Creating the main widget

        self.search_widget = ctk.CTkFrame(self,
                                          width=928 + 0,
                                          height=310)
        self.search_widget.grid_propagate(False)
        self.search_widget.grid(row=1, column=0, pady=(5, 0), padx=(10, 10))

        # Search box

        search_box = ctk.CTkTextbox(self.search_widget, height=20, width=200)
        search_box.grid(row=0, column=0, padx=(50, 0), pady=(5, 0), sticky="w")

        # Creating buttons...
        # - Reset filters
        self.reset_filter_button = ctk.CTkButton(self.search_widget, height=30, width=30, text="*", fg_color="#feffd4",
                                                 text_color="black", hover_color="#c9c1a3", hover=True,
                                                 font=("Helvetica", 16, "bold"),
                                                 command=lambda: filter_by_number(0))
        self.reset_filter_button.grid(row=0, column=0, pady=5, padx=280, sticky="w")
        self.number_drones_selection_button_list.append(self.reset_filter_button)

        # - Favourite

        create_favourite_button()

        # - Number of drones filter

        for i in range(1, self.number_of_drones + 1):
            self.number_drones_selection_button_list.append(
                ctk.CTkButton(self.search_widget,
                              height=30, width=30,
                              text=str(i), fg_color="#feffd4",
                              text_color="black", hover_color="#c9c1a3",
                              hover=True, font=("Helvetica", 16, "bold"),
                              command=lambda i=i: filter_by_number(i)))
            self.number_drones_selection_button_list[i].grid(row=0, column=0, pady=5, padx=280 + 35 * i, sticky="w")

        # Scrollable widget

        self.scrollable_widget = ctk.CTkScrollableFrame(self.search_widget,
                                                        width=880 + 0,
                                                        height=220,
                                                        orientation="horizontal",
                                                        fg_color="#d4cdcb",
                                                        scrollbar_button_color="#2e2e2e")

        self.scrollable_widget.grid(row=2, column=0, padx=(5, 5), pady=10, sticky="W")

        # Loading geofence data

        self.create_geofence_cards()
        filter_geofence_list()

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
        index = 0
        for geofence in self.geofence_list:
            card = GeofenceCardWidget(self.scrollable_widget, geofence, self.geofence_selected, self.drone_colors)
            card.grid(row=0, column=index, padx=5, pady=5)
            self.geofence_card_list.append(card)
            index+=1

    def create_main_frame(self):
        self.configure(height=900,
                       width=950 + 0,
                       fg_color="#bac1c5")
        self.grid(
            row=0,
            column=1,
            sticky='nw',
            padx=5,
            pady=10
        )
        self.grid_propagate(False)

    def create_geofence_viewport(self,
                                 width=928,
                                 height=550,
                                 fg_color="White"):
        self.geofence_viewport_widget = ctk.CTkFrame(self,
                                                     width=width,
                                                     height=height)
        self.geofence_viewport_widget.grid_propagate(False)
        self.geofence_viewport_widget.grid(row=0, column=0, pady=(5, 0), padx=10, sticky="W")
        self.geofence_viewport_widget.grid_rowconfigure(0, weight=1)
        self.geofence_viewport_widget.grid_columnconfigure(0, weight=1)

        self.geofence_image = ctk.CTkLabel(self.geofence_viewport_widget,
                                           text="",
                                           width=int(width * 0.95),
                                           height=int(height * 0.95),
                                           fg_color="transparent",
                                           anchor="center")
        self.geofence_image.grid(row=0, column=0)

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
        # Assign default colors if parameters are not provided
        geofence_frame_color = geofence_frame_color or self.geofence_frame_color
        geofence_viewport_widget_color = geofence_viewport_widget_color or self.geofence_viewport_widget_color
        search_widget_color = search_widget_color or self.search_widget_color
        reset_filter_button_color = number_filter_buttons_color or self.number_filter_buttons_color
        number_filter_buttons_color = number_filter_buttons_color or self.number_filter_buttons_color
        fav_filter_button_color = fav_filter_button_color or self.fav_filter_button_color
        scrollable_widget_color = scrollable_widget_color or self.scrollable_widget_color
        geofence_card_primary_color = geofence_card_primary_color or self.geofence_card_primary_color
        drone_count_color = drone_count_color or self.drone_count_color

        # Configure Geofence Frame
        self.configure(fg_color=geofence_frame_color)

        # Configure Geofence Viewport Widget
        self.geofence_viewport_widget.configure(fg_color=geofence_viewport_widget_color)

        # Configure Search Widget
        self.search_widget.configure(fg_color=search_widget_color)

        # Configure Reset Filter Button
        self.reset_filter_button.configure(fg_color=reset_filter_button_color)

        # Configure Number Filter Buttons
        for button in self.number_drones_selection_button_list:
            button.configure(fg_color=number_filter_buttons_color)

        # Configure Favorite Filter Button
        self.fav_button.configure(fg_color=fav_filter_button_color)

        # Configure Scrollable Widget
        self.scrollable_widget.configure(fg_color=scrollable_widget_color)

        # Configure Geofence Viewport Image (if needed)
        self.geofence_image.configure(
            fg_color=geofence_viewport_widget_color)  # Assuming you want no separate background

        # Configure Geofence Cards
        for card in self.geofence_card_list:
            card.set_fg_button_color(geofence_card_primary_color)
            card.set_fg_count_color(drone_count_color)
