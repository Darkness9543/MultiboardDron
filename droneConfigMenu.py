import customtkinter as ctk
from DroneInfoClass import DroneInfo
import json


class DroneConfigMenu(ctk.CTkFrame):
    def __init__(self, root,
                 drone,
                 drone_data_attribute,
                 text,
                 position,
                 options,
                 text_color: str = "white",
                 font: tuple = ("Helvetica", 15, "bold"),
                 padx: int = 10,
                 pady: int = 5,
                 width: int = 280,
                 height: int = 65,
                 color_palette: None = None):
        super().__init__(master=root)

        self.root = root
        self.drone = drone
        self.drone_data_attribute = drone_data_attribute
        self.text = text
        self.position = position
        self.options = options
        self.text_color = text_color
        self.font = font
        self.padx = padx
        self.pady = pady
        self.width = width
        self.height = height

        self.drone_data_attribute_value = str(getattr(drone, drone_data_attribute))
        self.drone_data_attribute_option = self.optionMenu_number_to_attribute(self.drone_data_attribute_value,
                                                                               self.drone_data_attribute)

        if color_palette is None:
            self.color_palette = ["#1E201E",
                                  "#3C3D37",
                                  "#697565",
                                  "#ECDFCC"]

        self.set_one = self.color_palette[0]
        self.set_two = self.color_palette[1]
        self.set_three = self.color_palette[2]
        self.set_four = self.color_palette[3]

        self.configure(width=self.width, height=self.height, fg_color=self.set_two)
        self.grid(row=position, column=0, padx=self.padx, pady=self.pady)
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=self.text, font=self.font, text_color=self.text_color)
        self.label.grid(row=0, column=0, pady=10, padx=5)

        self.current_value_label = ctk.CTkLabel(self,
                                                text="Current value : " + str(self.drone_data_attribute_value),
                                                font=("Helvetica", 11, "bold"), height=3, text_color=self.text_color)
        self.current_value_label.place(x=10, y=self.height * 0.66)

        # Option menu

        self.optionMenu = ctk.CTkOptionMenu(self, values=self.options, height=25, width=125, fg_color=self.set_four,
                                            button_color=self.set_three, button_hover_color="#E2F1E7", text_color="black")
        self.optionMenu.configure(command= lambda value: self.update_drone_attribute(value))
        self.optionMenu.grid(row=0, column=1, pady=10, padx=5, sticky="E")
        self.optionMenu.set(self.drone_data_attribute_option)

    def update_drone_attribute(self, value):
        value_map = {
            "Disabled": 0,
            "Enabled": 1,

            "Report only": 0,
            "RTL ": 1,
            "Land ": 2,
            "SmartRTL": 5,

            "Stabilize": 0,
            "Acro": 1,
            "AltHold": 2,
            "Auto": 3,
            "Guided": 4,
            "Loiter": 5,
            "RTL": 6,
            "Circle": 7,
            "Land": 8,
            "Drift": 9,
            "Sport": 10,
            "Flip": 11,
            "AutoTune": 12,
            "PosHold": 13,
            "Brake": 14,
            "Throw": 15,
            "Avoid_ADSB": 16,
            "Guided_NoGPS": 17,
            "Smart_RTL": 18,
            "FlowHold": 19,
            "Follow": 20,
            "ZigZag": 21,
            "SystemID": 22,
            "Heli_Autorotate": 23,
            "Auto RTL": 24
        }
        value_int = int(value_map[value])
        setattr(self.drone, self.drone_data_attribute, value_int)

    def optionMenu_number_to_attribute(self, droneDataAttributeValue, droneDataAttribute):
        global currentAttributeValue
        droneDataAttributeValue = int(droneDataAttributeValue)
        if droneDataAttribute == "Fence_Enabled":
            if droneDataAttributeValue == 0:
                currentAttributeValue = "Disabled"
            if droneDataAttributeValue == 1:
                currentAttributeValue = "Enabled"
        if droneDataAttribute == "Geofence_Action":
            if droneDataAttributeValue == 0:
                currentAttributeValue = "Report only"
            elif droneDataAttributeValue == 1:
                currentAttributeValue = "RTL"
            elif droneDataAttributeValue == 2:
                currentAttributeValue = "Land"
            elif droneDataAttributeValue == 3:
                currentAttributeValue = "SmartRTL or RTL or Land"
            elif droneDataAttributeValue == 4:
                currentAttributeValue = "Brake or Land"
            elif droneDataAttributeValue == 5:
                currentAttributeValue = "SmartRTL"

        elif droneDataAttribute == "FLTMode6":
            if droneDataAttributeValue == 0:
                currentAttributeValue = "Stabilize"
            elif droneDataAttributeValue == 1:
                currentAttributeValue = "Acro"
            elif droneDataAttributeValue == 2:
                currentAttributeValue = "AltHold"
            elif droneDataAttributeValue == 3:
                currentAttributeValue = "Auto"
            elif droneDataAttributeValue == 4:
                currentAttributeValue = "Guided"
            elif droneDataAttributeValue == 5:
                currentAttributeValue = "Loiter"
            elif droneDataAttributeValue == 6:
                currentAttributeValue = "RTL"
            elif droneDataAttributeValue == 7:
                currentAttributeValue = "Circle"
            elif droneDataAttributeValue == 8:
                currentAttributeValue = "Land"
            elif droneDataAttributeValue == 9:
                currentAttributeValue = "Drift"
            elif droneDataAttributeValue == 10:
                currentAttributeValue = "Sport"
            elif droneDataAttributeValue == 11:
                currentAttributeValue = "Flip"
            elif droneDataAttributeValue == 12:
                currentAttributeValue = "AutoTune"
            elif droneDataAttributeValue == 13:
                currentAttributeValue = "PosHold"
            elif droneDataAttributeValue == 14:
                currentAttributeValue = "Brake"
            elif droneDataAttributeValue == 15:
                currentAttributeValue = "Throw"
            elif droneDataAttributeValue == 16:
                currentAttributeValue = "Avoid_ADSB"
            elif droneDataAttributeValue == 17:
                currentAttributeValue = "Guided_NoGPS"
            elif droneDataAttributeValue == 18:
                currentAttributeValue = "Smart_RTL"
            elif droneDataAttributeValue == 19:
                currentAttributeValue = "FlowHold"
            elif droneDataAttributeValue == 20:
                currentAttributeValue = "Follow"
            elif droneDataAttributeValue == 21:
                currentAttributeValue = "ZigZag"
            elif droneDataAttributeValue == 22:
                currentAttributeValue = "SystemID"
            elif droneDataAttributeValue == 23:
                currentAttributeValue = "Heli_Autorotate"
            elif droneDataAttributeValue == 24:
                currentAttributeValue = "Auto RTL"
        else:
            currentAttributeValue = "Unknown"
        return_value = currentAttributeValue
        return return_value

    def update_value(self, value):
        setattr(self.drone, self.drone_data_attribute, value)
        self.current_value_label.configure(
            text="Current value : " + str(getattr(self.drone, self.drone_data_attribute)))
        self.optionMenu.set(self.optionMenu_number_to_attribute(value, self.drone_data_attribute))

