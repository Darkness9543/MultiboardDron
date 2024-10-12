import time

import customtkinter as ctk
import json
from DroneInfoClass import DroneInfo
from PIL import Image, ImageTk
class TelemetryInfoCard(ctk.CTkFrame):
    def handle_message(self, message):
        MessageDroneId = int(str(message.topic).split("/")[0].split("autopilotService")[1])
        ReceivedInfoType = str(message.topic).split("/")[2]
        if ReceivedInfoType == "telemetryInfo":
            if self.drone.DroneId + 1 == MessageDroneId:
                payload = json.loads(message.payload)
                self.drone.setTelemetryInfo(payload[self.telemetry_data], self.telemetry_data)
                self.update_value_label(payload[self.telemetry_data])

    def __init__(self, parent, root, client, position,
                 text,
                 telemetry_data,
                 drone,
                 drone_total,
                 width: int = 100,
                 height: int = 60,
                 color_palette: None = None):
        super().__init__(master=root)

        if color_palette is None:
            color_palette = ["#1E201E",
                             "#3C3D37",
                             "#697565",
                             "#ECDFCC"]

        self.set_one = color_palette[0]
        self.set_two = color_palette[1]
        self.set_three = color_palette[2]
        self.set_four = color_palette[3]
        self.drone_total = drone_total
        self.drone = drone
        self.parent = parent
        self.root = root
        self.client = client
        self.position = position
        self.width = width
        self.height = height
        self.text = text
        self.telemetry_data = telemetry_data
        self.grid_propagate(False)



        self.configure(width= self.width, height=self.height, fg_color="transparent")
        self.grid(row=position[0], column=position[1], padx=5, pady=5)
        self.grid_propagate(False)


        self.label = ctk.CTkLabel(self,
                                  text=self.text,
                                  text_color="white")
        self.label.grid(row=0, column=0, padx=5, pady=5)

        self.value_label = ctk.CTkLabel(self,
                                  text="",
                                  text_color="white")
        self.value_label.grid(row=1, column=0, padx=5, pady=0, sticky="EW")

        for i in range(self.drone_total):
            self.client.subscribe(f"autopilotService{i+1}/miMain/telemetryInfo")

    def update_value_label(self, value):
        if self.telemetry_data == "lat" or self.telemetry_data == "lon":
            self.value_label.configure(text=str(round(value,6)))
        elif self.telemetry_data == "state":
            self.value_label.configure(text=value)
        else:
            self.value_label.configure(text=str(round(value, 2)))
    def set_current_drone(self, drone):
        self.drone = drone
        self.value_label.configure(text="")
