import customtkinter as ctk
from DroneInfoClass import DroneInfo
import json


class DroneConfigSlider(ctk.CTkFrame):
    def __init__(self, root,
                 drone,
                 drone_data_attribute,
                 text,
                 position,
                 min_value,
                 max_value,
                 steps,
                 text_color: str = "white",
                 font: tuple = ("Helvetica", 15, "bold"),
                 padx: int = 10,
                 pady: tuple[int, int] = (5, 5),
                 width: int = 280,
                 height: int = 65,
                 color_palette: None = None):
        super().__init__(master=root)

        self.root = root
        self.drone = drone
        self.drone_data_attribute = drone_data_attribute
        self.text = text
        self.position = position
        self.min_value = min_value
        self.max_value = max_value
        self.steps = steps
        self.text_color = text_color
        self.font = font
        self.padx = padx
        self.pady = pady
        self.width = width
        self.height = height
        self.set_units_multiplier = 1
        # Changing units from cm to m for some parameters

        if self.drone_data_attribute in ("RTL_Altitude","Pilot_Speed_Up"):
            self.min_value *= 0.01
            self.max_value *= 0.01

            self.set_units_multiplier = 0.01

        self.drone_data_attribute_value = str(getattr(drone, drone_data_attribute))

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

        self.label = ctk.CTkLabel(self, text=self.text, font=self.font, text_color=self.text_color)
        self.label.grid(row=0, column=0, pady=10, padx=5)

        self.current_value_label = ctk.CTkLabel(self,
                                                text="Current value : " + str(self.drone_data_attribute_value),
                                                font=("Helvetica", 11, "bold"), height=3, text_color=self.text_color)
        self.current_value_label.place(x=10, y=self.height * 0.66)

        self.grid_columnconfigure(1, weight=1)
        self.entry = ctk.CTkEntry(self, width=90, fg_color=self.set_four)
        self.entry.insert(0, self.drone_data_attribute_value)
        self.entry.grid(row=0, column=1, pady=10, padx=5, sticky= "E")

        # Slider

        self.slider = ctk.CTkSlider(self, from_=self.min_value, to=self.max_value, number_of_steps=self.steps,
                                    width=100)
        self.slider.configure(
            command=lambda value: self.update_entry_from_slider(value))
        self.slider.set(int(self.drone_data_attribute_value))
        self.slider.place(x=self.width * 0.63, y=self.height * 0.66)

        self.entry.bind("<Return>", lambda event: self.update_slider_from_entry())

        # Units label
        self.unit_text = ""
        if self.drone_data_attribute in ("Fence_Altitude_Max", "Geofence_Margin", "RTL_Altitude"):
            self.unit_text = "m"
        if self.drone_data_attribute in "Pilot_Speed_Up":
            self.unit_text = "m/s"
        self.units_label = ctk.CTkLabel(self.entry,
                                        width = 10,
                                        height = 10,
                                        text=self.unit_text,
                                        fg_color="transparent",
                                        text_color="black")
        self.units_label.grid(row=0, column=0, sticky="E", padx=5, pady=5)

    def update_entry_from_slider(self, value):
        self.entry.delete(0, ctk.END)
        self.entry.insert(0, str(round(value,2)))
        setattr(self.drone, self.drone_data_attribute, value/self.set_units_multiplier)

    def update_slider_from_entry(self):
        # Update the slider from the entry
        value = float(self.entry.get())
        self.slider.set(value)
        setattr(self.drone, self.drone_data_attribute, value/self.set_units_multiplier)

    def update_value(self, value):
        self.update_entry_from_slider(value*self.set_units_multiplier)
        self.update_slider_from_entry()

        self.current_value_label.configure(text=f"Current value : {str(value*self.set_units_multiplier)} {self.unit_text}")

    def get_value(self):
        return float(self.entry.get())
