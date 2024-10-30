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
from colorCircle import ColorCircle

class droneFrame(ctk.CTkFrame):
    def __init__(self, root, drone_number, color_palette, switch_callback, is_sim, drone_color):
        super().__init__(root)

        if color_palette is None:
            color_palette = ["#1E201E",
                             "#3C3D37",
                             "#697565",
                             "#ECDFCC"]

        self.set_one = color_palette[0]
        self.set_two = color_palette[1]
        self.set_three = color_palette[2]
        self.set_four = color_palette[3]
        self.configure(height=80, fg_color=self.set_three)
        self.grid(row=drone_number, column=0 ,pady=5, padx=5)
        self.configure(width=320)
        self.grid_propagate(False)
        self.is_sim = is_sim
        self.inserted_port = None
        self.inserted_connection_string = None

        # Drone Label
        self.drone_label = ctk.CTkLabel(self, text=f"Drone {drone_number}", font=("Helvetica", 14, "bold"))
        self.drone_label.grid(row=0, column=0, padx=5, pady=(25, 0), sticky="nw")

        # Port/Connection String Label
        self.port_label = ctk.CTkLabel(self, text="Connection string:")
        self.port_label.grid(row=0, column=1, padx=60, pady=5, sticky="nw")
        # Port/Connection String Textbox with blended background color
        self.port_textbox = ctk.CTkEntry(
            self,
            width=150,
            fg_color=self.set_four  # Set the blended color as the background
        )
        self.port_textbox.grid(row=0, column=1, padx=50, pady=(35, 10), sticky="E")
        self.port_textbox.grid_propagate(False)

        # Switch
        self.state_var = ctk.StringVar(value="Global")
        self.switch = ctk.CTkSwitch(self,
                                    text="",
                                    command=lambda var=self.state_var, sw=None: switch_callback,
                                    fg_color=self.set_one,
                                    progress_color=self.set_four)
        #self.switch.grid(row=0, column=2, padx=(10, 0), pady=(17), sticky="nw")

        # Label beneath the switch
        self.switch_label = ctk.CTkLabel(self, text="Global")
        #self.switch_label.grid(row=0, column=2, padx=8, pady=(40, 5), sticky="nw")

        # Update switch label on toggle
        self.switch.configure(command=self.update_switch_label)

        # Set the color indicator
        size = 50
        self.color_indicator = self.circle = ctk.CTkLabel(self, width=size, height=int(size*0.07),
                                                          text="", corner_radius=int(5), fg_color=drone_color)
        self.color_indicator.place(x=5, y=5)

    def update_switch_label(self):
        if self.switch.get():
            self.switch_label.configure(text="Direct")
            self.state_var.set("Direct")
        else:
            self.switch_label.configure(text="Global")
            self.state_var.set("Global")

    def switch_port_sim(self, default_port, default_connection_string, sim_bool):
        """
        Switches the textbox content between port and connection string based on the sim_bool flag.

        Args:
            default_port (str): The default port number as a string.
            default_connection_string (str): The default connection string.
            sim_bool (bool): Flag indicating simulation mode (True) or production mode (False).
        """

        # Set the simulation mode flag
        self.is_sim = sim_bool

        # Initialize inserted_connection_string and inserted_port if they are not already set
        if not hasattr(self, 'inserted_connection_string') or self.inserted_connection_string is None:
            self.inserted_connection_string = default_connection_string
            print(f"Initialized connection string to default: {default_connection_string}")

        if not hasattr(self, 'inserted_port') or self.inserted_port is None:
            self.inserted_port = default_port
            print(f"Initialized port to default: {default_port}")

        if sim_bool:
            # **Simulation Mode**: Display connection string and save the current port

            # Retrieve the current port from the textbox
            current_port = self.port_textbox.get().strip()
            if current_port:
                self.inserted_port = current_port
                print(f"Saved port from textbox: {self.inserted_port}")
            else:
                print("Warning: Port textbox is empty. Using existing stored port.")

            # Update the textbox to display the connection string
            self.port_textbox.delete(0, 'end')
            self.port_textbox.insert(0, self.inserted_connection_string)
            print(f"Displayed connection string in textbox: {self.inserted_connection_string}")

        elif not sim_bool:
            # **Production Mode**: Display port and save the current connection string

            # Retrieve the current connection string from the textbox
            current_connection_string = self.port_textbox.get().strip()
            if current_connection_string:
                self.inserted_connection_string = current_connection_string
                print(f"Saved connection string from textbox: {self.inserted_connection_string}")
            else:
                print("Warning: Connection string textbox is empty. Using existing stored connection string.")

            # Ensure that inserted_port has a valid value before displaying
            if self.inserted_port:
                # Update the textbox to display the port
                self.port_textbox.delete(0, 'end')
                self.port_textbox.insert(0, self.inserted_port)
                print(f"Displayed port in textbox: {self.inserted_port}")
            else:
                # Fallback to default_port if inserted_port is somehow empty
                self.inserted_port = default_port
                self.port_textbox.delete(0, 'end')
                self.port_textbox.insert(0, self.inserted_port)
                print(f"Displayed default port in textbox: {self.inserted_port}")


    def set_port_data(self, value):
        self.port_textbox.delete(0, 'end')
        self.port_textbox.insert(0, value)
    def hide(self):
        self.grid_remove()
    def show(self):
        self.grid()
