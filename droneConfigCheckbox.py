import customtkinter as ctk
from DroneInfoClass import DroneInfo
import json


class DroneConfigCheckbox(ctk.CTkFrame):
    def __init__(self, root,
                 drone,
                 drone_data_attribute,
                 text,
                 position,
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
        self.text_color = text_color
        self.font = font
        self.padx = padx
        self.pady = pady
        self.width = width
        self.height = height

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
        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=self.text, font=self.font, text_color=self.text_color)
        self.label.grid(row=0, column=0, pady=10, padx=5)

        self.current_value_label = ctk.CTkLabel(self,
                                                text="Current value : " + str(self.drone_data_attribute_value),
                                                font=("Helvetica", 11, "bold"), height=3, text_color=self.text_color)
        self.current_value_label.place(x=10, y=self.height * 0.66)

        self.checkbox = ctk.CTkCheckBox(self,
                                        onvalue="Enabled",
                                        offvalue="Disabled",
                                        text="",
                                        fg_color=self.set_four,
                                        hover_color=self.set_three,
                                        checkmark_color="black",
                                        command= self.checkbox_event)
        self.checkbox.place(x=self.width*0.74, y=self.height * 0.22)

        self.checkbox_label = ctk.CTkLabel(self,
                                          text="Disabled",
                                          font=("Helvetica", 11, "bold"), height=3, text_color=self.text_color)
        self.checkbox_label.place(x=self.width*0.7, y=self.height * 0.66)
    def checkbox_event(self):
        if self.checkbox.get() == "Enabled":
            setattr(self.drone, self.drone_data_attribute, 1)
            self.checkbox_label.configure(text="Enabled")
        else:  # Unchecked
            setattr(self.drone, self.drone_data_attribute, 0)
            self.checkbox_label.configure(text="Disabled")


    def update_value(self, value):
        if bool(value):
            setattr(self.drone, self.drone_data_attribute, 1)
            self.current_value_label.configure(
                text="Current value : " + str(getattr(self.drone, self.drone_data_attribute)))
            self.checkbox.select()
            self.checkbox_label.configure(text="Enabled")
        if not bool(value):
            setattr(self.drone, self.drone_data_attribute, 0)
            self.current_value_label.configure(
                text="Current value : " + str(getattr(self.drone, self.drone_data_attribute)))
            self.checkbox.deselect()
            self.checkbox_label.configure(text="Disabled")