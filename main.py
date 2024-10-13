import queue
import threading

import customtkinter as ctk
import GeofenceClass as Geofence
import json
import math
import time
import paho.mqtt.client as mqtt
import DroneInfoClass
import DroneMap

from tkinter import *
from PIL import Image, ImageTk, ImageDraw
from typing import List
from tkintermapview import TkinterMapView

import geofenceWidget as geoWid
import droneSelectionWidget as droSelWid
from droneConfigWidget import DroneConfigWidget
import geofenceEditorWidget as geoEdit
import atexit
from AutopilotServiceClass import AutopilotService


def get_defaults(json_file_path="data/defaults.json"):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        connection_strings = data.get('connection_strings', [])
        ports = data.get('ports', [])
        drone_colors = data.get('drone_colors', [])
        max_drones = data.get('max_drones')

        return connection_strings, ports, drone_colors, max_drones
    except FileNotFoundError:
        print(f"Error: The file {json_file_path} was not found.")
        return [], [], []
    except json.JSONDecodeError:
        print(f"Error: The file {json_file_path} contains invalid JSON.")
        return [], [], []
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return [], [], []


class App(ctk.CTk):
    def on_message(self, client, userdata, message):
        if self.drone_config_widget_created:
            print(f"Message arrived: {message}")
            self.message_queue.put(message)

    def __init__(self):
        super().__init__()
        # Color palette

        self.color_palette = ["#1E201E",  # set_one
                              "#3C3D37",  # set_two
                              "#697565",  # set_three
                              "#ECDFCC"]  # set_four

        self.background_color = self.color_palette[0]  # set_one
        self.hover_color = "#323232"  # Adjust hover color with desired transparency
        self.drone_config_widget_created = False
        self.window_height = 950
        self.window_width = 1400
        self.sidebar_width = 60
        self.title('Drones TestView')
        self.geometry(f'{self.window_width}x{self.window_height}')
        self.configure(fg_color=self.background_color)

        self.message_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self.process_messages)
        self.processing_thread.daemon = True
        self.processing_thread.start()

        # Parameters for padding and spacing
        self.button_padx = 5  # Padding in x for buttons
        self.button_pady = 10  # Padding in y (spacing between buttons)

        # Variables:

        self.ThreadList = []
        self.Autopilots = []
        self.selected_geofence = None

        # Load defaults

        connection_strings, ports, drone_colors, max_drones = get_defaults()
        self.defaults = [connection_strings, ports, drone_colors, max_drones]
        # Initialize the main window components
        self.connect_MQTT()
        self.initialize_main_window()
        self.geofence_widget = geoWid.geofenceViewWidget(self, self.tabs[0], self.defaults)
        self.drone_widget = droSelWid.droneSelectionWidget(self, self.tabs[0], self.defaults)
        self.geofence_editor = geoEdit.geofenceEditorWidget(self, self.tabs[1], self.defaults, None,
                                                            width=self.tabs[0].winfo_width(),
                                                            height=self.tabs[0].winfo_height())
        self.create_proceed_to_drone_config_button()
        self.create_switch_prod_sim()

    def process_messages(self):
        while True:
            message = self.message_queue.get()
            print(f"Message get from queue {message}")
            self.drone_config_widget.receive_message(message)
            self.message_queue.task_done()

    def initialize_main_window(self):
        # Main frame
        self.main_frame = ctk.CTkFrame(self, fg_color=self.background_color)
        self.main_frame.pack(fill='both', expand=True)

        # Sidebar frame for tabs
        self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=self.sidebar_width, fg_color=self.color_palette[1])
        self.sidebar_frame.pack(side='left', fill='y')

        # Content frame for displaying tabs' contents
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=self.background_color)
        self.content_frame.pack(side='right', fill='both', expand=True)

        # Load images for buttons
        self.images = []
        for path in ["assets/drone_icon.png", "assets/geofence_icon.png",
                     "assets/settings_icon.png"]:  # Replace with your image paths
            img = Image.open(path)
            img = img.resize((45, 45))  # Adjust size as needed
            self.images.append(ImageTk.PhotoImage(img))

        # Create tab buttons
        self.tab_buttons = []
        for i in range(3):
            button = ctk.CTkButton(
                master=self.sidebar_frame,
                image=self.images[i],
                text='',
                width=60,
                height=60,
                fg_color="transparent",
                hover_color=self.hover_color,
                command=lambda i=i: self.show_tab(i)
            )
            button.pack(pady=self.button_pady, padx=self.button_padx)
            self.tab_buttons.append(button)

        # Create tab content frames
        self.tabs = []
        for i in range(3):
            tab_frame = ctk.CTkFrame(self.content_frame, fg_color=self.background_color)
            self.tabs.append(tab_frame)

        # Show the first tab by default
        self.show_tab(0)

    def show_tab(self, index):
        # Hide all tabs
        for tab in self.tabs:
            tab.pack_forget()

        # Show the selected tab
        self.tabs[index].pack(fill='both', expand=True)

    def connect_MQTT(self):
        self.client = mqtt.Client("Main", transport="websockets")
        self.client.on_message = self.on_message
        host = "broker.hivemq.com"
        port = 8000
        self.client.connect(host, port)
        print('Connecting to ' + str(host) + ':' + str(port))
        self.client.loop_start()

    def create_proceed_to_drone_config_button(self):
        self.proceed_to_drone_config_button = ctk.CTkButton(self.tabs[0],
                                                            text="Proceed",
                                                            fg_color=self.color_palette[3],
                                                            command=self.proceed_to_drone_config,
                                                            text_color="black",
                                                            width=100,
                                                            height=30)
        self.proceed_to_drone_config_button.grid(row=0, column=0, sticky="nw", padx=10, pady=682)

    def on_switch_toggle_prod_sim(self):
        print("on switch")
        self.drone_widget.switch_port_sim()

    def proceed_to_drone_config(self):
        connection_ports = self.drone_widget.get_connection_ports()
        print(self.selected_geofence)
        if self.selected_geofence is None:
            print("Error")
        else:
            i = 0
            for port in connection_ports:
                print("Creating autopilot")
                autopilot = AutopilotService(port, i + 1)
                thread = threading.Thread(target=autopilot.run, name=f"AutopilotThread-{i}")
                thread.start()
                self.Autopilots.append(autopilot)
                self.ThreadList.append(thread)
                i += 1
            pass
            self.geofence_widget.grid_remove()
            self.drone_widget.grid_remove()
            self.proceed_to_drone_config_button.grid_remove()
            self.switch_prod_sim_frame.grid_remove()

            self.drone_config_widget = DroneConfigWidget(self,
                                                         self.tabs[0],
                                                         self.color_palette,
                                                         connection_ports,
                                                         self.client,
                                                         self.selected_geofence,
                                                         self.defaults,
                                                         width=self.window_width - self.sidebar_width,
                                                         height=self.window_height)
            self.drone_config_widget_created = True

    def create_switch_prod_sim(self):
        def update_switch_label():
            if self.switch_prod_sim.get():
                switch_label.configure(text="Production")
                self.state_var.set("Production")
            else:
                switch_label.configure(text="Simulation")
                self.state_var.set("Simulation")

            self.on_switch_toggle_prod_sim()

        self.switch_prod_sim_frame = ctk.CTkFrame(self.tabs[0],
                                                  width=120, height=30, fg_color=self.color_palette[2])
        self.switch_prod_sim_frame.grid(row=0, column=0, padx=130, pady=682, sticky="nw")
        self.switch_prod_sim_frame.grid_propagate(False)

        # Switch
        self.state_var = ctk.StringVar(value="Simulation")
        self.switch_prod_sim = ctk.CTkSwitch(self.switch_prod_sim_frame,
                                             text="",
                                             command=self.on_switch_toggle_prod_sim,
                                             fg_color=self.color_palette[0],
                                             progress_color=self.color_palette[3])
        self.switch_prod_sim.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

        # Label beneath the switch
        switch_label = ctk.CTkLabel(self.switch_prod_sim_frame, text="Simulation", text_color="black",
                                    font=("Segoe UI", 13, "bold"))
        switch_label.grid(row=0, column=0, padx=(45, 5), pady=4, sticky="nw")

        self.switch_prod_sim.configure(command=update_switch_label)
        self.switch_prod_sim.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

    def on_geofence_selected(self, geofence):
        self.selected_geofence = geofence
        self.drone_widget.update_based_on_geofence(geofence)

    def restore_main_view(self):
        for autopilot in self.Autopilots:
            autopilot.stop()

        for thread in self.ThreadList:
            thread.join(timeout=5)  # Adjust timeout as necessary
            if thread.is_alive():
                print(f"Thread {thread.name} did not terminate within the timeout period.")
            else:
                print(f"Thread {thread.name} has been successfully terminated.")

            # Clear the lists after stopping
        self.Autopilots.clear()
        self.ThreadList.clear()

        self.geofence_widget.grid(
            row=0,
            column=1,
            sticky='nw',
            padx=5,
            pady=10
        )
        self.drone_widget.grid(
            row=0,
            column=0,
            sticky='nw',
            padx=(10, 5),
            pady=(10, 200)
        )
        self.proceed_to_drone_config_button.grid(row=0, column=0, sticky="nw", padx=10, pady=682)
        self.switch_prod_sim_frame.grid(row=0, column=0, padx=130, pady=682, sticky="nw")

    def update_root(self):
        self.update()
        self.update_idletasks()


root = App()
root.mainloop()
