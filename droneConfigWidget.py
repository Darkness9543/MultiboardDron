import time

import customtkinter as ctk
from droneControlWidget import DroneControlWidget as DroneControl
from PIL import ImageTk, Image

from droneConfigCard import DroneConfigCard


def brighten_color(hex_color, percent):
    """
    Brighten a color by a given percentage.

    :param hex_color: A string representing the color in hex format (e.g., '#FF8000')
    :param percent: The percentage to brighten the color (0-100)
    :return: A string representing the brightened color in hex format
    """
    # Remove the '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert hex to RGB
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # Calculate the brightness factor
    factor = 1 + (percent / 100)

    # Brighten each channel
    r = min(round(r * factor), 255)
    g = min(round(g * factor), 255)
    b = min(round(b * factor), 255)

    # Convert back to hex
    return f'#{r:02x}{g:02x}{b:02x}'


class DroneConfigWidget(ctk.CTkFrame):
    def __init__(self, parent, root, color_palette, connection_ports, client, selected_geofence, defaults,
                 width: int = 900,
                 height: int = 900):
        super().__init__(master=root)
        self.color_palette = color_palette
        if color_palette is None:
            self.color_palette = ["#1E201E",
                                  "#3C3D37",
                                  "#697565",
                                  "#ECDFCC"]

        self.set_one = self.color_palette[0]
        self.set_two = self.color_palette[1]
        self.set_three = self.color_palette[2]
        self.set_four = self.color_palette[3]

        self.connection_ports = connection_ports
        self.client = client
        self.parent = parent
        self.root = root
        self.width = width
        self.height = height
        self.drone_card_list = {}
        self.drone_control_created = False
        self.selected_geofence = selected_geofence
        self.drone_colors = defaults[2]

        self.top_frame_height = 50
        self.card_height = 850
        self.top_buttons_height = 25

        self.create_main_frame()
        self.create_top_frame()
        self.create_drone_config_instances()
        self.create_return_button()
        self.create_proceed_button()
        self.create_set_parameters_all_button()
        self.create_get_parameters_all_button()

    # Style to make the scroll bar transparent
    def receive_message(self, message):
        topic_parts = message.topic.split('/')
        service_part = topic_parts[0]
        MessageDroneId = int(service_part.replace('autopilotService', ''))
        # Check if the drone ID exists in the mapping
        try:
            if self.drone_control_created:
                self.drone_control.receive_messaage(message)
            if MessageDroneId - 1 in self.drone_card_list:
                drone_card = self.drone_card_list[MessageDroneId - 1]
                drone_card.handle_message(message)

            else:
                print(f"Received message for unknown Drone ID: {MessageDroneId}")
        except:
            time.sleep(1)
            if self.drone_control_created:
                self.drone_control.receive_messaage(message)
            if MessageDroneId - 1 in self.drone_card_list:
                drone_card = self.drone_card_list[MessageDroneId - 1]
                drone_card.handle_message(message)
            else:
                print(f"Received message for unknown Drone ID: {MessageDroneId}")
    def hide_scrollbar(self, scrollable_frame):
        scrollbar = scrollable_frame._scrollbar
        scrollbar.configure(width=0, height=0, corner_radius=0)
        scrollbar.grid_forget()  # Remove from grid layout

    def create_main_frame(self):
        self.configure(height=self.height,
                       width=self.width,
                       fg_color=self.set_one)
        # Place the frame
        self.grid(
            row=0,
            column=0,
            sticky='nw',  # Stretch in all directions within the cell
        )
        self.grid_propagate(False)
        percent_padding = 0.05
        self.main_frame_scrolleable = ctk.CTkScrollableFrame(self,
                                                             orientation="horizontal",
                                                             height=int(self.card_height +
                                                                        (self.height - self.top_frame_height) *
                                                                        percent_padding / 2)+ 50,
                                                             scrollbar_button_color=self.set_four,
                                                             width=int(self.width * (1 - percent_padding)),
                                                             fg_color=self.set_three,
                                                             corner_radius=3)
        self.main_frame_scrolleable.grid(row=0,
                                         column=0,
                                         padx=int(self.width * percent_padding / 2),
                                         pady=int(self.top_frame_height + (
                                                 self.height - self.top_frame_height) * percent_padding / 2))

    def create_top_frame(self):
        self.top_frame = ctk.CTkFrame(self,
                                      fg_color=brighten_color(self.set_two, 80),
                                      height=int(self.top_frame_height),
                                      width=int(self.width * 1.1),
                                      corner_radius=0)
        self.top_frame.place(x=-1, y=0)
        self.grid_propagate(False)
        self.top_frame_divider = ctk.CTkFrame(self.top_frame,
                                              fg_color="black",
                                              height=int(self.height * 0.0025),
                                              width=int(self.width * 1.1),
                                              corner_radius=0)
        self.top_frame.grid_rowconfigure(10, weight=1)
        self.top_frame.grid_propagate(False)
        # self.top_frame_divider.grid(row=10, column=0, sticky="S")

    def create_drone_config_instances(self):
        if len(self.connection_ports) < 4:
            self.hide_scrollbar(self.main_frame_scrolleable)
        for droneId in range(0, len(self.connection_ports)):
            print("Creating card config..." + str(droneId))
            drone_config_card = DroneConfigCard(self,
                                                self.main_frame_scrolleable,
                                                self.client,
                                                droneId, self.selected_geofence,self.drone_colors[droneId],
                                                droneId, self.connection_ports[droneId],
                                                height=self.card_height)
            self.drone_card_list[droneId] = drone_config_card

    def create_return_button(self):
        image = ImageTk.PhotoImage(Image.open("assets/BackIcon.png").resize((20, int(self.top_buttons_height * 0.5))))
        self.return_button = ctk.CTkButton(self.top_frame,
                                           text="",
                                           image=image,
                                           width=50,
                                           height=self.top_buttons_height,
                                           fg_color=self.set_four,
                                           command=self.return_to_drone_selection)

        self.return_button.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="W")

    def create_proceed_button(self):
        self.proceed_button = ctk.CTkButton(self.top_frame,
                                            text="Proceed",
                                            text_color="black",
                                            width=80,
                                            height=self.top_buttons_height,
                                            fg_color=self.set_four,
                                            command=self.proceed)
        self.proceed_button.grid(row=0, column=1, padx=(5, 100), pady=10, sticky="W")

    def create_set_parameters_all_button(self):
        self.set_paramaeters_all_button = ctk.CTkButton(self.top_frame,
                                                        text="Set parameters for all",
                                                        text_color="black",
                                                        width=150,
                                                        height=self.top_buttons_height,
                                                        fg_color=self.set_four,
                                                        command=self.set_parameters_for_all)
        self.set_paramaeters_all_button.grid(row=0, column=2, padx=(5, 5), pady=10, sticky="W")

    def create_get_parameters_all_button(self):
        self.get_paramaeters_all_button = ctk.CTkButton(self.top_frame,
                                                        text="Get parameters for all",
                                                        text_color="black",
                                                        width=150,
                                                        height=self.top_buttons_height,
                                                        fg_color=self.set_four,
                                                        command=self.get_parameters_for_all)
        self.get_paramaeters_all_button.grid(row=0, column=3, padx=(5, 5), pady=10, sticky="W")

    def return_to_drone_selection(self):
        print("Im in")
        self.parent.restore_main_view()
        self.grid_remove()
        self.destroy()

    def share_config(self, drone):
        for i in range(0, len(self.drone_card_list)):
            self.drone_card_list[i].update_values(drone.Fence_Altitude_Max,
                                                  drone.Fence_Enabled,
                                                  drone.Geofence_Margin,
                                                  drone.Geofence_Action,
                                                  drone.RTL_Altitude,
                                                  drone.Pilot_Speed_Up,
                                                  drone.FLTMode6)

    def proceed(self):
        self.set_parameters_for_all()
        self.grid_forget()

        drones = []
        for drone_card in range(0, len(self.drone_card_list)):
            drones.append(self.drone_card_list[drone_card].drone)
        self.drone_control = DroneControl(self,
                                          self.root,
                                          drone_colors=self.drone_colors,
                                          height= self.height,
                                          width= self.width,
                                          color_palette=self.color_palette,
                                          drones=drones,
                                          client=self.client)
        self.drone_control_created = True

    def get_parameters_for_all(self):
        for drone_card in range(0, len(self.drone_card_list)):
            self.drone_card_list[drone_card].get_parameters()

    def set_parameters_for_all(self):
        for drone_card in range(0, len(self.drone_card_list)):
            if self.drone_card_list[drone_card].drone.Status == "connected":
                self.drone_card_list[drone_card].set_parameters()
            else:
                print(f"Current drone {self.drone_card_list[drone_card].drone.DroneId} is disconnected")
