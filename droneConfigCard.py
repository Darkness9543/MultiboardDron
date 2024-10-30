import queue
import time

import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import GeofenceClass
from DroneInfoClass import DroneInfo
from droneConfigSlider import DroneConfigSlider as DroneSlider
from droneConfigMenu import DroneConfigMenu as DroneMenu
from droneConfigCheckbox import DroneConfigCheckbox as DroneCheckbox
from droneConfigIndicator import DroneStatusIndicator as DroneIndicator
import json


class DroneConfigCard(ctk.CTkFrame):

    def _handle_message_ui(self, message):

        MessageDroneId = int(str(message.topic).split("/")[0].split("autopilotService")[1])
        ReceivedInfoType = str(message.topic).split("/")[2]
        if ReceivedInfoType == "parameters":
            payload = json.loads(message.payload)
            if self.drone.DroneId + 1 == MessageDroneId:
                self.drone.setDroneInfoParameters(
                    payload[0]['FENCE_ALT_MAX'],
                    payload[1]['FENCE_ENABLE'],
                    payload[2]['FENCE_MARGIN'],
                    payload[3]['FENCE_ACTION'],
                    payload[4]['RTL_ALT'],
                    payload[5]['PILOT_SPEED_UP'],
                    payload[6]['FLTMODE6'],
                    payload[7]['WP_YAW_BEHAVIOR']
                )
                print("Fence Alt Max: " + str(payload[0]['FENCE_ALT_MAX']))
                print("Fence Enable: " + str(payload[1]['FENCE_ENABLE']))
                print("Fence Margin: " + str(payload[2]['FENCE_MARGIN']))
                print("Fence Action: " + str(payload[3]['FENCE_ACTION']))
                print("RTL_ALT: " + str(payload[4]['RTL_ALT']))
                print("Pilot speed up: " + str(payload[5]['PILOT_SPEED_UP']))
                print("FLTmode6: " + str(payload[6]['FLTMODE6']))

                self.update_values(payload[0]['FENCE_ALT_MAX'],
                                   payload[1]['FENCE_ENABLE'],
                                   payload[2]['FENCE_MARGIN'],
                                   payload[3]['FENCE_ACTION'],
                                   payload[4]['RTL_ALT'],
                                   payload[5]['PILOT_SPEED_UP'],
                                   payload[6]['FLTMODE6'],
                                   payload[7]['WP_YAW_BEHAVIOR'])
                self.indicator.set_state("Connected")

        if ReceivedInfoType == "connected":
            print("Dron " + str(MessageDroneId) + " conectado")

            self.drone.Status = "connected"
            payload = json.dumps(self.geofence.Coordinates[self.drone.DroneId])
            self.client.publish(f"miMain/autopilotService{self.id + 1}/setGeofence", payload)
            self.indicator.set_state("Setting geofence")
        if ReceivedInfoType == "geofenceSet":

            self.client.publish("miMain/autopilotService" + str(MessageDroneId) + "/getParameters", self.parameters)
        if ReceivedInfoType == "disconnected":
            self.drone.Status = "disconnected"

    def __init__(self, parent, root, client, position, geofences, drone_color,
                 id, port,
                 width: int = 320,
                 height: int = 750,
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
        self.port = port
        self.parameters = json.dumps(['FENCE_ALT_MAX', 'FENCE_ENABLE', 'FENCE_MARGIN', 'FENCE_ACTION',
                                     "RTL_ALT", "PILOT_SPEED_UP", 'FLTMODE6', 'WP_YAW_BEHAVIOR'])
        self.id = id
        self.parent = parent
        self.root = root
        self.client = client
        self.position = position

        self.geofence = geofences
        self.drone = DroneInfo(geofence=geofences, DroneId=self.id)

        # Handling connection to client
        self.client.subscribe(f"autopilotService{self.id+1}/miMain/parameters")
        self.client.subscribe(f"autopilotService{self.id+1}/miMain/connected")
        self.client.subscribe(f"autopilotService{self.id+1}/miMain/disconnected")
        self.client.subscribe(f"autopilotService{self.id+1}/miMain/geofenceSet")



        print("self.id+1")
        print(self.id+1)

        self.configure(fg_color="red")
        self.grid_propagate(False)

        # Setting up the interface

        self.rowconfigure(8, weight=1)
        self.rowconfigure(9, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.configure(width=width, height=height, fg_color=self.set_one)
        if self.position == 0:
            self.grid(row=0, column=self.position, padx=(10, 5), pady=5)
        else:
            self.grid(row=0, column=self.position, padx=5, pady=10)
        self.grid_propagate(False)



        # Title label

        self.label = ctk.CTkLabel(self,
                                  text="Drone " + str(self.id + 1),
                                  font=("Helvetica", 16, "bold"),
                                  text_color="white")
        self.label.grid(row=0, column=0, pady=(5, 0), padx=10)

        # Set the color indicator
        size = 60
        self.color_indicator = self.circle = ctk.CTkLabel(self, width=size, height=int(size * 0.07),
                                                          text="", corner_radius=int(5), fg_color=drone_color)
        self.color_indicator.grid(row=0, column=0, pady=(50, 0), padx=10)
        self.color_indicator.grid_propagate(False)

        # Set port label

        self.port_label = ctk.CTkLabel(self,
                                  text=self.port,
                                  font=("Helvetica", 12, "bold"),
                                  text_color="white")
        self.port_label.grid(row=0, column=0, pady=(80, 0), padx=10)

        # Connection indicator

        self.indicator = DroneIndicator(self, position=[width - 40, 10])

        # Data frame

        self.data_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", width= 300, height= 620)
        self.data_frame.grid(row=1, column=0,padx=0, pady=0, rowspan=7)

        # Fence altitude max

        self.drone_slider_test = DroneSlider(self.data_frame,
                                             self.drone,
                                             "Fence_Altitude_Max",
                                             "Geofence max altitude", 1,
                                             5,
                                             100,
                                             95,
                                             pady=(10, 5))

        # Fence enabled

        self.drone_fence_enabled = DroneCheckbox(self.data_frame,
                                                 self.drone,
                                                 "Fence_Enabled",
                                                 "Fence status", 2)

        # Geofence margin

        self.drone_geofence_margin = DroneSlider(self.data_frame,
                                                 self.drone,
                                                 "Geofence_Margin",
                                                 "Geofence margin", 3,
                                                 1,
                                                 20,
                                                 19)
        # Geofence action

        self.drone_geofence_action = DroneMenu(self.data_frame,
                                               self.drone,
                                               "Geofence_Action",
                                               "Geofence action", 4,
                                               ["Report only", "Brake ",
                                                "RTL ", "Land ",
                                                "SmartRTL"]
                                               )
        # RTL altitude

        self.drone_rtl_altitude = DroneSlider(self.data_frame,
                                              self.drone,
                                              "RTL_Altitude",
                                              "RTL Altitude", 5,
                                              400,
                                              3200,
                                              28)

        # Pilot_speed_up

        self.drone_pilot_speed_up = DroneSlider(self.data_frame,
                                                self.drone,
                                                "Pilot_Speed_Up",
                                                "Pilot speed up", 6,
                                                10,
                                                500,
                                                49)

        # FLTMode6

        self.drone_FLTMode6 = DroneMenu(self.data_frame,
                                        self.drone,
                                        "FLTMode6",
                                        "FLTMode 6", 7,
                                        ["RTL", "Land"])

        # WP_YAW_BEHAVIOR

        self.drone_WP_YAW_BEHAVIOR = DroneCheckbox(self.data_frame,
                                                 self.drone,
                                                 "WP_YAW_BEHAVIOR",
                                                 "Change yaw on movement", 8)

        # Setting up configuration buttons

        self.get_parameters_button = ctk.CTkButton(self,
                                                   text="Get parameters",
                                                   text_color="black",
                                                   font=("Helvetica", 13, "bold"),
                                                   width=135,
                                                   height=30,
                                                   fg_color=self.set_four,
                                                   command=lambda: self.get_parameters())
        self.get_parameters_button.grid(row=9, column=0, padx=10, pady=(10,5), sticky="W")
        self.get_parameters_button.grid_propagate(False)

        self.set_parameters_button = ctk.CTkButton(self,
                                                   text="Set parameters",
                                                   text_color="black",
                                                   font=("Helvetica", 13, "bold"),
                                                   width=135,
                                                   height=30,
                                                   fg_color=self.set_four,
                                                   command=lambda: self.set_parameters())
        self.set_parameters_button.grid(row=9, column=0, padx=10, pady=(10,5), sticky="E")
        self.set_parameters_button.grid_propagate(False)
        # Share config

        self.share_config_button = ctk.CTkButton(self,
                                                   text="Use config for all",
                                                   text_color="black",
                                                   font=("Helvetica", 13, "bold"),
                                                   width=135,
                                                   height=30,
                                                   fg_color=self.set_four,
                                                   command=lambda: self.share_config())
        self.share_config_button.grid(row=10, column=0, padx=20, pady=(5,25))
        self.share_config_button.grid_propagate(False)

        # Reconnect button

        image = ImageTk.PhotoImage(Image.open("assets/reconnect.png").resize((20, 20)))
        self.reconnect_button = ctk.CTkButton(self,
                                                   width=20,
                                                   text="",
                                                   height=20,
                                                   image=image,
                                                   fg_color=self.set_four,
                                                   command=lambda: self.reconnect())
        self.reconnect_button.place(x=10, y=10)


        print(self.geofence.Coordinates[self.drone.DroneId][0]['type'])

        # Queue for thread-safe GUI updates
        self.gui_queue = queue.Queue()

        # Start the background thread for handling messages
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.process_messages, daemon=True)
        self.thread.start()

        # Periodically check the queue for GUI updates
        self.after(100, self.process_gui_queue)

        self.after(100, self.connect)


    def process_gui_queue(self):
        self.after(40, self.process_gui_queue)

    def handle_message(self, message):
        """
        This method is called from the MQTT client's callback.
        It puts the message into a thread-safe queue for processing.
        """
        self.gui_queue.put(message)

    def process_messages(self):
        """
        Background thread that processes incoming messages.
        """
        while not self.stop_event.is_set():
            try:
                # Wait for a message from the queue
                message = self.gui_queue.get(timeout=3)
                self._handle_message_ui(message)
            except queue.Empty:
                continue  # No message received, continue waiting
    def destroy(self):
        self.stop_event.set()
        self.thread.join()
        super().destroy()
    def update_values(self,
                      FENCE_ALT_MAX,
                      FENCE_ENABLE,
                      FENCE_MARGIN,
                      FENCE_ACTION,
                      RTL_ALT,
                      PILOT_SPEED_UP,
                      FLTMODE6,
                      WP_YAW_BEHAVIOR
                      ):
        self.drone_slider_test.update_value(FENCE_ALT_MAX)
        self.drone_fence_enabled.update_value(FENCE_ENABLE)
        self.drone_geofence_margin.update_value(FENCE_MARGIN)
        self.drone_geofence_action.update_value(FENCE_ACTION)
        self.drone_rtl_altitude.update_value(RTL_ALT)
        self.drone_pilot_speed_up.update_value(PILOT_SPEED_UP)
        self.drone_FLTMode6.update_value(FLTMODE6)
        self.drone_WP_YAW_BEHAVIOR.update_value(WP_YAW_BEHAVIOR)

    def get_parameters(self):
        self.client.publish("miMain/autopilotService" + str(self.id + 1) + "/getParameters", self.parameters)

    def set_parameters(self):
        drone = self.drone
        print(f"Preparing parameters for Drone {drone.DroneId}:")
        params_to_set = [
            {"ID": "FENCE_ALT_MAX", "Value": drone.Fence_Altitude_Max},
            {"ID": "FENCE_ENABLE", "Value": drone.Fence_Enabled},
            {"ID": "FENCE_MARGIN", "Value": drone.Geofence_Margin},
            {"ID": "FENCE_ACTION", "Value": drone.Geofence_Action},
            {"ID": "RTL_ALT", "Value": drone.RTL_Altitude},
            {"ID": "PILOT_SPEED_UP", "Value": drone.Pilot_Speed_Up},
            {"ID": "FLTMODE6", "Value": drone.FLTMode6},
            {"ID": "WP_YAW_BEHAVIOR", "Value": drone.WP_YAW_BEHAVIOR}
        ]

        for param in params_to_set:
            print(f"  - Setting {param['ID']} to {param['Value']}")

            # Convert to JSON string
        payload = json.dumps(params_to_set)
        topic = f"miMain/autopilotService{drone.DroneId + 1}/setParameters"
        print(f"Publishing parameters to topic: {topic}")
        self.client.publish(topic, payload)
        print(f"Parameters published for Drone {drone.DroneId}")
        print("--------------------")

    def share_config(self):
        self.parent.share_config(self.drone)

    def connect(self):
        self.indicator.set_state("Disconnected")
        self.client.publish(f"miMain/autopilotService{self.id + 1}/disconnect")
        self.client.publish(f"miMain/autopilotService{self.id + 1}/connect")
    def reconnect(self):
        self.parent.parent.restart_autopilot(self.id)
        self.after(200, lambda: self.client.publish(f"miMain/autopilotService{self.id + 1}/connect"))

