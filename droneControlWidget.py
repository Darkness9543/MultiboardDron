import customtkinter as ctk
from PIL import ImageTk, Image
from telemetryInfoCard import TelemetryInfoCard as TelemetryInfo
from droneMapWidget import DroneMap
from repeatingButton import RepeatingButton
import keyboard
import threading
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


class DroneControlWidget(ctk.CTkFrame):
    def __init__(self, parent, root, color_palette, drones, client,
                 drone_colors,
                 width: int = 900,
                 height: int = 900):
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
        self.hover_color = "#FFDAB9"

        self.drone_colors = drone_colors
        self.drones = drones

        self.client = client
        self.parent = parent
        self.root = root
        self.width = width
        self.height = height
        self.drone_card_list = {}

        self.top_frame_height = 50
        self.card_height = 700
        self.top_buttons_height = 25

        self.control_frame_width = 0.35
        self.control_frame_height = 0.7
        self.control_sidebar_width = 120
        self.control_sidebar_padx = 5
        self.padding_x = 0.02
        self.padding_y = 0.02

        self.grid_propagate(False)

        for drone in drones:
            print("Starting telemetry")
            print("miMain/autopilotService" + str(drone.DroneId + 1) + "/startTelemetry\n")
            self.client.publish("miMain/autopilotService" + str(drone.DroneId + 1) + "/startTelemetry")
        self.telemetry_info_list = []
        self._setup_key_bindings()
        self.create_main_frame()
        self.create_top_frame()
        self.create_map_frame()
        self.create_control_frame()
        self.initialize_control_frame()

    def create_main_frame(self):
        self.configure(height=self.height,
                       width=self.width,
                       fg_color=self.set_one)
        # Place the frame
        self.grid(
            row=0,
            column=0,
            sticky='nwse',  # Stretch in all directions within the cell
        )
        self.grid_propagate(False)
        percent_padding = 0.05
        self.main_frame = ctk.CTkFrame(self,
                                       height=int(self.card_height +
                                                  (self.height - self.top_frame_height) *
                                                  percent_padding / 2),

                                       width=int((self.width * (1 - percent_padding)) * 0.5),
                                       fg_color=self.set_three,
                                       corner_radius=3)

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

        image = ImageTk.PhotoImage(Image.open("assets/BackIcon.png").resize((20, int(self.top_buttons_height * 0.5))))
        self.return_button = ctk.CTkButton(self.top_frame,
                                           text="",
                                           image=image,
                                           width=50,
                                           height=self.top_buttons_height,
                                           fg_color=self.set_four,
                                           command=self.return_to_drone_config)

        self.return_button.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="W")

    def create_control_frame(self):
        self.control_frame = ctk.CTkFrame(self,
                                          fg_color=brighten_color(self.set_two, 80),
                                          height=int(self.control_frame_height * self.height),
                                          width=int(self.control_frame_width * self.width),
                                          corner_radius=10)
        self.control_frame.grid(row=0, column=0, padx=self.padding_x * self.width,
                                pady=self.padding_y * self.width + self.top_frame_height)
        self.control_frame.grid_propagate(False)
        self.control_frame.pack_propagate(False)

    def create_map_frame(self):
        height = int(self.height * (1 - self.padding_y * 2) - self.top_frame_height)
        width = int((1 - self.control_frame_width - 3 * self.padding_x) * self.width)
        self.map_frame = ctk.CTkFrame(self,
                                      fg_color=brighten_color(self.set_two, 80),
                                      height=height,
                                      width=width,
                                      corner_radius=10)
        self.map_frame.grid(row=0, column=1, padx=(0, 10),
                            pady=(self.padding_y * self.height + self.top_frame_height, self.padding_y * self.height))
        self.map_frame.grid_propagate(False)

        self.drone_map_widget = DroneMap(self.map_frame, self.client, self.drones, self.drone_colors, 720, 1080)

        self.show_geofences_button = ctk.CTkButton(self.map_frame,
                                                   height=40,
                                                   width=100,
                                                   fg_color=self.set_four,
                                                   text="Show geofences",
                                                   text_color="black",
                                                   command=self.show_geofences)
        self.show_geofences_button.place(x=width - 100 - 20, y=height - 40 - 20)

    def hide_scrollbar(self, scrollable_frame):
        scrollbar = scrollable_frame._scrollbar
        scrollbar.configure(width=0, height=0, corner_radius=0)
        scrollbar.grid_forget()  # Remove from grid layout

    def initialize_control_frame(self):
        self.sidebar_frame = ctk.CTkScrollableFrame(self.control_frame,
                                                    orientation="vertical",
                                                    width=self.control_sidebar_width,
                                                    fg_color=self.set_one,
                                                    scrollbar_button_color=self.set_four)
        self.sidebar_frame.pack(side='right', fill='y', padx=5, pady=10)

        if len(self.drones) <= 5:
            self.hide_scrollbar(self.sidebar_frame)
        self.content_frame = ctk.CTkFrame(self.control_frame,
                                          fg_color=self.set_three)
        self.content_frame.pack(side='left', fill='both', expand=True, padx=5, pady=10)
        self.tab_buttons = []
        for i, drone in enumerate(self.drones):
            if drone.Status == "connected":
                button = ctk.CTkButton(
                    master=self.sidebar_frame,
                    text=f'Drone {drone.DroneId + 1}',
                    text_color="black",
                    width=110,
                    height=70,
                    fg_color=self.set_four,
                    command=lambda d=drone: self.select_drone(d)
                )
                button.pack(pady=5, padx=5)
                self.tab_buttons.append(button)
        self.select_drone(self.drones[0])
        self.initialize_control_frame_content()

    def create_nwse_frame(self):
        self.NWSE_buttons_frame = ctk.CTkFrame(self.button_frame,
                                               fg_color=self.set_three,
                                               width=150,
                                               height=150)
        self.NWSE_buttons_frame.grid(row=0, column=0, padx=5, pady=5, columnspan=3, rowspan=3)
        buttons_NWSE = []
        positions = ["NW", "N", "NE", "W", "E", "SW", "S", "SE"]
        for row in range(3):
            for col in range(3):
                if row == 1 and col == 1:
                    continue  # Skip the center position
                position = positions.pop(0)
                button = ctk.CTkButton(self.NWSE_buttons_frame,
                                       text=position,
                                       text_color="black",
                                       fg_color=self.set_four,
                                       width=40,
                                       height=40,
                                       command=lambda pos=position, drone=self.current_drone: self.on_moving_press(pos,
                                                                                                                   drone))
                button.grid(row=row, column=col, padx=5, pady=5, sticky="w")
                buttons_NWSE.append(button)
                button.bind(
                    "<ButtonPress-1>",
                    lambda event, pos=position, drone=self.current_drone: self.on_moving_press(pos, drone)
                )
                button.bind(
                    "<ButtonRelease-1>",
                    lambda event: self.on_moving_release()
                )
        position = "Stop"
        button = ctk.CTkButton(self.NWSE_buttons_frame,
                               text=position,
                               text_color="black",
                               fg_color=self.set_four,
                               width=40,
                               height=40,
                               command=lambda pos=position, drone=self.current_drone: self.on_moving_release())
        button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def create_directional_control_frame(self):
        self.directional_buttons_frame = ctk.CTkFrame(self.button_frame,
                                                      fg_color=self.set_three,
                                                      width=150,
                                                      height=150)
        self.directional_buttons_frame.grid_propagate(False)
        buttons_directional = []
        positions = ["Fwd", "Left", "Right", "Back"]
        for row in range(3):
            for col in range(3):
                if (row, col) in {(1, 1), (0, 0), (0, 2), (2, 0), (2, 2)}:
                    continue  # Skip the center position
                position = positions.pop(0)
                button = ctk.CTkButton(self.directional_buttons_frame,
                                       text=position,
                                       text_color="black",
                                       fg_color=self.set_four,
                                       width=40,
                                       height=40,
                                       command=lambda pos=position, drone=self.current_drone: self.on_moving_press(pos,
                                                                                                                   drone))
                button.grid(row=row, column=col, padx=5, pady=5, sticky="w")
                buttons_directional.append(button)
                button.bind(
                    "<ButtonPress-1>",
                    lambda event, pos=position, drone=self.current_drone: self.on_moving_press(pos, drone)
                )
                button.bind(
                    "<ButtonRelease-1>",
                    lambda event: self.on_moving_release()
                )

        position = "Stop"
        button = ctk.CTkButton(self.directional_buttons_frame,
                               text=position,
                               text_color="black",
                               fg_color=self.set_four,
                               width=40,
                               height=40,
                               command=lambda pos=position, drone=self.current_drone: self.on_moving_release())
        button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def create_commands_frame(self):
        button_texts = ["Arm", "Takeoff", "RTL", "Land","Set guided"]
        for i, text in enumerate(button_texts):
            button = ctk.CTkButton(self.content_frame,
                                   text=text,
                                   text_color="black",
                                   fg_color=self.set_four,
                                   height=40,
                                   width=70,
                                   command=lambda t=text:
                                   self.drone_operate(t))
            button.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            button.grid_propagate(False)

    def create_telememtry_info_display(self, button_frame_height, button_frame_pady):

        info_display_padx = self.control_sidebar_padx * 4 - 5
        info_display_width = int((int(self.control_frame_width * self.width)
                                  - self.control_sidebar_width
                                  - self.control_sidebar_padx
                                  - info_display_padx * 3))
        info_display_height = int(int(self.control_frame_height * self.height)
                                  - button_frame_height
                                  - button_frame_pady * 16)
        self.info_display = ctk.CTkScrollableFrame(self.content_frame,
                                                   fg_color=self.set_one,
                                                   width=int(info_display_width/2),
                                                   height=info_display_height - 50,
                                                   orientation="vertical")
        self.info_display.grid(columnspan=2,
                               row=6,
                               column=0,
                               sticky="nwse",
                               padx=info_display_padx - 5,
                               pady=button_frame_pady + 5)
        self.initialize_telemetry_info_display(info_display_width)
    def create_fix_heading_switch(self):
        def fix_heading():
            print("Fixing heading")
            self.client.publish("miMain/autopilotService" + str(self.selected_drone.DroneId + 1) + "/fixHeading")
        def unfix_heading():
            print("Unfixing heading")
            self.client.publish("miMain/autopilotService" + str(self.selected_drone.DroneId + 1) + "/unfixHeading")
        self.fix_heading_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.fix_heading_frame.grid(row=4, column=0, padx=5, pady=5)
        self.fix_heading = ctk.CTkButton(self.fix_heading_frame, text="Fix heading", fg_color=self.set_four,
                                         command=fix_heading, width=80, height=30, text_color="black")
        self.fix_heading.grid(row=0, column=0, padx=2, pady=5)
        self.unfix_heading = ctk.CTkButton(self.fix_heading_frame, text="Unfix heading", fg_color=self.set_four,
                                         command=unfix_heading, width=80, height=30, text_color="black")
        self.unfix_heading.grid(row=0, column=1, padx=2, pady=5)

    def return_to_drone_config(self):
        self.parent.grid(row=0, column=0, sticky="nw")
        for drone in self.drones:
            print("Starting telemetry")
            print("miMain/autopilotService" + str(drone.DroneId + 1) + "/stopTelemetry\n")
            self.client.publish("miMain/autopilotService" + str(drone.DroneId + 1) + "/stopTelemetry")
        self.grid_forget()
    def create_control_type_switch(self):
        def on_nswe_click():
            self.NWSE_buttons_frame.grid(row=0, column=0, padx=5, pady=5, columnspan=3, rowspan=3)
            self.directional_buttons_frame.grid_forget()

            self.directional_button.configure(fg_color=inactive_color, hover_color=hover_color)
            self.nswe_button.configure(fg_color=active_color, hover_color=active_color)

        def on_directional_click():
            self.directional_buttons_frame.grid(row=0, column=0, padx=5, pady=5, columnspan=3, rowspan=3)
            self.NWSE_buttons_frame.grid_forget()

            self.nswe_button.configure(fg_color=inactive_color, hover_color=hover_color)
            self.directional_button.configure(fg_color=active_color, hover_color=active_color)

        active_color = self.set_four
        inactive_color = "grey"
        hover_color = "cyan"

        self.control_switch_frame = ctk.CTkFrame(self.button_frame,
                                                 fg_color=brighten_color(self.set_three, 30),
                                                 width=100,
                                                 height=50)
        self.control_switch_frame.grid(row=3, column=0, padx=10, pady=5, columnspan=3)

        self.nswe_button = ctk.CTkButton(self.control_switch_frame,
                                         fg_color=active_color,
                                         hover_color=active_color,
                                         text="NSWE",
                                         text_color="black",
                                         width=45,
                                         height=25,
                                         command=on_nswe_click)
        self.nswe_button.grid(row=0, column=0, padx=(5, 2), pady=5, sticky="W")

        self.directional_button = ctk.CTkButton(self.control_switch_frame,
                                                fg_color=inactive_color,
                                                hover_color=hover_color,
                                                text="Directional",
                                                text_color="black",
                                                width=45,
                                                height=25,
                                                command=on_directional_click)
        self.directional_button.grid(row=0, column=1, padx=(3, 5), pady=5, sticky="E")

    def create_altitude_buttons(self):

        self.altitude_frame = ctk.CTkFrame(self.button_frame,
                                           fg_color=brighten_color(self.set_three, 30),
                                           width=30)
        self.altitude_frame.grid(row=0, column=3, padx=0, pady=5, rowspan=3)

        self.up_button = ctk.CTkButton(self.altitude_frame,
                                       fg_color=self.set_four,
                                       text="↑",
                                       text_color="black",
                                       width=20,
                                       height=40,
                                       command=lambda: self.on_moving_press("Up"))
        self.up_button.grid(row=0, column=3, padx=5, pady=5, sticky="NW")
        self.up_button.bind(
            "<ButtonPress-1>",
            lambda event: self.on_moving_press("Up")
        )
        self.up_button.bind(
            "<ButtonRelease-1>",
            lambda event: self.on_moving_release()
        )

        self.down_button = ctk.CTkButton(self.altitude_frame,
                                         fg_color=self.set_four,
                                         text="↓",
                                         text_color="black",
                                         width=20,
                                         height=40)
        self.down_button.grid(row=2, column=3, padx=5, pady=5, sticky="NW")
        self.down_button.bind(
            "<ButtonPress-1>",
            lambda event: self.on_moving_press("Down")
        )
        self.down_button.bind(
            "<ButtonRelease-1>",
            lambda event: self.on_moving_release()
        )

    def initialize_control_frame_content(self):
        button_frame_height = 200
        button_frame_pady = 5
        self.button_frame = ctk.CTkFrame(self.content_frame,
                                         fg_color=self.set_three,
                                         width=230,
                                         height=button_frame_height + 60)
        self.button_frame.grid_propagate(False)
        self.button_frame.grid(row=0, column=0, padx=(5, 0), pady=button_frame_pady, rowspan=4)

        # Setting up North West South East buttons

        self.create_nwse_frame()

        # Setting up directional buttons (forward, back, left, right)

        self.create_directional_control_frame()

        # Create a switch to alternate between nswe and directional movement

        self.create_control_type_switch()

        self.create_fix_heading_switch()

        # Create the altitude controls

        self.create_altitude_buttons()

        # Creating the drone commands frame

        self.create_commands_frame()

        # Creating telemetry info display

        self.create_telememtry_info_display(button_frame_height, button_frame_pady)

    def on_moving_release(self):
        self.client.publish("miMain/autopilotService" + str(self.selected_drone.DroneId + 1) + "/move", "Stop")

    def on_moving_press(self, position, drone=None):
        position_to_direction = {
            "N": "North",
            "S": "South",
            "E": "East",
            "W": "West",
            "NW": "NorthWest",
            "NE": "NorthEast",
            "SW": "SouthWest",
            "SE": "SouthEast",
            "Fwd": "Forward",
            "Back": "Back",
            "Left": "Left",
            "Right": "Right",
            "Up": "Up",
            "Down": "Down",
            "Stop": "Stop"
        }
        payload = position_to_direction.get(position)
        print("Payload move: " + str(payload))
        self.client.publish("miMain/autopilotService" + str(self.selected_drone.DroneId + 1) + "/move", payload)

    def repeat_command(self, position):
        if self.is_repeating:
            self.on_moving_press(position, self.current_drone)
            self.repeat_id = self.button.after(200, self.repeat_command, position)

    def initialize_telemetry_info_display(self, info_display_width):

        ground_speed = TelemetryInfo(self,
                                     self.info_display,
                                     self.client,
                                     [0, 0],
                                     "Ground speed",
                                     "groundSpeed",
                                     self.current_drone,
                                     len(self.drones), width=info_display_width-10)
        self.telemetry_info_list.append(ground_speed)

        alt = TelemetryInfo(self,
                            self.info_display,
                            self.client,
                            [1, 0],
                            "Altitude",
                            "alt",
                            self.current_drone,
                            len(self.drones), width=info_display_width-10)
        self.telemetry_info_list.append(alt)

        state = TelemetryInfo(self,
                              self.info_display,
                              self.client,
                              [2, 0],
                              "State",
                              "state",
                              self.current_drone,
                              len(self.drones), width=info_display_width-10)
        self.telemetry_info_list.append(state)

        lat = TelemetryInfo(self,
                            self.info_display,
                            self.client,
                            [3, 0],
                            "Latitude",
                            "lat",
                            self.current_drone,
                            len(self.drones), width=info_display_width-10)
        self.telemetry_info_list.append(lat)

        lon = TelemetryInfo(self,
                            self.info_display,
                            self.client,
                            [4, 0],
                            "Longitude",
                            "lon",
                            self.current_drone,
                            len(self.drones), width=info_display_width-10)
        self.telemetry_info_list.append(lon)

        heading = TelemetryInfo(self,
                                self.info_display,
                                self.client,
                                [5, 0],
                                "Heading",
                                "heading",
                                self.current_drone,
                                len(self.drones), width=info_display_width-10)
        self.telemetry_info_list.append(heading)

    def receive_messaage(self, message):
        for telemetry_info in self.telemetry_info_list:
            telemetry_info.handle_message(message)
        self.drone_map_widget.handle_message(message)

    def drone_operate(self, button_text):
        # Add your desired functionality here
        drone_num = self.current_drone.DroneId
        if button_text == "Arm":
            self.client.publish("miMain/autopilotService" + str(drone_num + 1) + "/arm")
        if button_text == "Takeoff":
            self.client.publish("miMain/autopilotService" + str(drone_num + 1) + "/takeOff")
        if button_text == "RTL":
            self.client.publish("miMain/autopilotService" + str(drone_num + 1) + "/RTL")
        if button_text == "Land":
            self.client.publish("miMain/autopilotService" + str(drone_num + 1) + "/Land")
        if button_text == "Set guided":
            self.client.publish("miMain/autopilotService" + str(drone_num + 1) + "/setGuided")


        print(f" autopilotService'{drone_num + 1}' has been  instucted to '{button_text}'")

    def show_geofences(self):
        self.drone_map_widget.draw_geofences(self.drones[0].geofence.Coordinates)
        self.show_geofences_button.configure(command=self.hide_geofences, text="Hide geofences")

    def hide_geofences(self):
        self.drone_map_widget.hide_geofences()
        self.show_geofences_button.configure(command=self.show_geofences, text="Show geofences")

    def select_drone(self, drone):
        self.selected_drone = drone
        for i, button in enumerate(self.tab_buttons):
            if self.drones[i] == drone:
                button.configure(fg_color="grey", hover_color="grey")
            else:
                button.configure(fg_color=self.set_four, hover_color=self.hover_color)

        self.current_drone = drone
        for telemetry_info in self.telemetry_info_list:
            telemetry_info.set_current_drone(self.current_drone)

    def _setup_key_bindings(self):
        """
        Sets up key bindings for arrow keys to control drone movement.
        Runs the keyboard listener in a separate daemon thread.
        """
        # Define key-event to direction mapping
        key_direction_map = {
            'up': 'Fwd',  # Forward
            'down': 'Back',  # Backward
            'left': 'Left',
            'right': 'Right'
        }

        # Define handlers for each key
        for key, direction in key_direction_map.items():
            keyboard.on_press_key(key, lambda e, dir=direction: self.on_moving_press(dir))

        # Optional: Handle key release to stop the drone
        for key in key_direction_map.keys():
            keyboard.on_release_key(key, lambda e: self.on_moving_press("Stop"))

        # Start a separate thread to keep the main thread free
        listener_thread = threading.Thread(target=keyboard.wait, daemon=True)
        listener_thread.start()
