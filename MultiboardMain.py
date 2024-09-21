import tkinter

import customtkinter as ctk
import GeofenceClass as Geofence
import json
import math
import time
import paho.mqtt.client as mqtt
import DroneInfoClass
from geographiclib.geodesic import Geodesic
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
from typing import List
import atexit



class ComputeCoords:
    def __init__(self):

        self.geod = Geodesic.WGS84

        # two points (x,y) in the canvas and their corresponding positions (lat,lon)
        # self.refCoord = [60, 290]
        # self.refPosition = [41.27643361279337, 1.988196484744549]
        # self.refCoord2 = [790, 370]
        # self.refPosition2 = [41.27635096595008, 1.9891352578997614]

        self.refCoord = [84, 293]
        self.refPosition = [41.2764267, 1.9882317]
        self.refCoord2 = [768, 358]
        self.refPosition2 = [41.2763652, 1.98911288]
        distCoord = (
            math.sqrt(
                (self.refCoord[0] - self.refCoord2[0]) ** 2
                + (self.refCoord[1] - self.refCoord2[1]) ** 2
            ))
        g = self.geod.Inverse(
            self.refPosition[0],
            self.refPosition[1],
            self.refPosition2[0],
            self.refPosition2[1],
        )
        distPositions = float(g["s12"])
        self.mpp = distPositions / distCoord  # meters per pixel
        self.ppm = 1 / self.mpp  # pixels per meter

    def convertToCoords(self, position):
        g = self.geod.Inverse(
            self.refPosition[0],
            self.refPosition[1],
            float(position[0]),
            float(position[1]),
        )
        azimuth = float(g["azi2"])
        dist = float(g["s12"])

        x = self.refCoord[0] + math.trunc(
            dist * self.ppm * math.sin(math.radians(180 - azimuth))
        )
        y = self.refCoord[1] + math.trunc(
            dist * self.ppm * math.cos(math.radians(180 - azimuth))
        )
        return x, y

    def convertToPosition(self, coords):
        # compute distance with ref coords
        dist = (
                math.sqrt(
                    (coords[0] - self.refCoord[0]) ** 2
                    + (coords[1] - self.refCoord[1]) ** 2
                )
                * self.mpp
        )
        azimuth = math.degrees(
            math.atan2((self.refCoord[0] - coords[0]), (self.refCoord[1] - coords[1]))
        ) * (-1)
        if azimuth < 0:
            azimuth = azimuth + 360
        # compute lat,log of new wayp
        g = self.geod.Direct(
            float(self.refPosition[0]), float(self.refPosition[1]), azimuth, dist
        )
        lat = float(g["lat2"])
        lon = float(g["lon2"])
        return lat, lon


class App(ctk.CTk):

    def on_message(self, client, userdata, message):
        print("New message")
        MessageDroneId = int(str(message.topic).split("/")[0].split("autopilotService")[1])
        ReceivedInfoType = str(message.topic).split("/")[2]
        if ReceivedInfoType == "parameters":
            payload = json.loads(message.payload)
            for droneInfo in self.DroneDataList:
                if droneInfo.DroneId + 1 == MessageDroneId:
                    self.DroneDataList[droneInfo.DroneId].setDroneInfoParameters(
                        payload[0]['FENCE_ALT_MAX'],
                        payload[1]['FENCE_ENABLE'],
                        payload[2]['FENCE_MARGIN'],
                        payload[3]['FENCE_ACTION'],
                        payload[4]['RTL_ALT'],
                        payload[5]['PILOT_SPEED_UP'],
                        payload[6]['FLTMODE6'],
                    )
                    print("Fence Alt Max"+str(payload[0]['FENCE_ALT_MAX']))
                    print("Fence Enable"+str(payload[1]['FENCE_ENABLE']))
                    print("Fence Margin"+str(payload[2]['FENCE_MARGIN']))
                    print("Fence Action"+str(payload[3]['FENCE_ACTION']))
                    print("RTL_ALT"+str(payload[4]['RTL_ALT']))
                    print("Pilot speed up"+str(payload[5]['PILOT_SPEED_UP']))
                    print("FLTmode6"+str(payload[6]['FLTMODE6']))

                    self.update_config_frame(self.DroneDataList[droneInfo.DroneId])
        if ReceivedInfoType == "connected":
            print("Dron " + str(MessageDroneId) + " conectado")
            self.DroneDataList[MessageDroneId - 1].Status = "connected"
            self.client.publish("miMain/autopilotService" + str(MessageDroneId) + "/getParameters")

        if ReceivedInfoType == "telemetryInfo":
            print("Received telemtry info")
            payload = json.loads(message.payload)
            for droneInfo in self.DroneDataList:
                if droneInfo.DroneId + 1 == MessageDroneId:
                    print(payload)
                    droneInfo.setTelemetryInfo(
                        payload["groundSpeed"],
                        payload["alt"],
                        payload["state"],
                        payload["lat"],
                        payload["lon"],
                    )

    def __init__(self):
        super().__init__()

        self.selected_tab = 0

        self.DroneDataList = [DroneInfoClass.DroneInfo(),
                              DroneInfoClass.DroneInfo(),
                              DroneInfoClass.DroneInfo(),
                              DroneInfoClass.DroneInfo()]
        self.DroneDataList[0].DroneId = 0
        self.DroneDataList[1].DroneId = 1
        self.DroneDataList[2].DroneId = 2
        self.DroneDataList[3].DroneId = 3

        self.callbacks = []

        self.client = mqtt.Client("Main", transport="websockets")
        self.client.on_message = self.on_message
        self.client.connect("broker.hivemq.com", 8000)
        print('Connecting to broker.hivemq.com:8000')
        self.client.loop_start()
        for i in range(1, 4):
            self.client.subscribe("autopilotService" + str(i) + "/miMain/parameters")
            self.client.subscribe("autopilotService" + str(i) + "/miMain/telemetryInfo")
            self.client.subscribe("autopilotService" + str(i) + "/miMain/connected")

        self.title('Drones TestView')
        self.geometry('1700x956')
        self.BackgroundColor = "#262626"
        CustomFont = ctk.CTkFont("Times", 22, "bold")

        self.GeofenceWidthEdge = 150
        self.GeneralButtonColor = "#404a4d"
        self.configure(fg_color=self.BackgroundColor)
        self.Tab = ctk.CTkTabview(self, width=1480, height=730, fg_color=self.BackgroundColor,
                                  segmented_button_fg_color=self.BackgroundColor,
                                  segmented_button_unselected_color=self.BackgroundColor,
                                  segmented_button_unselected_hover_color="#323232")
        self.Tab.grid(row=1, column=0)
        self.MultiboardLogo = ImageTk.PhotoImage(Image.open("assets/MultiboardLogo.png").resize((70, 70)))
        self.LogoButton = ctk.CTkButton(self, text="", image=self.MultiboardLogo,
                                        fg_color=self.BackgroundColor,
                                        state="disabled").place(x=10, y=10)
        self.TabDrones = self.Tab.add("Drones")
        self.TabGeofence = self.Tab.add("Geofences")
        self.TabSettings = self.Tab.add("Settings")
        self.Tab._segmented_button.configure(font=CustomFont, width=600)
        self.Tab._segmented_button.grid(sticky="W", padx=150, pady=20)

        self.initialize_selection_panel()
        self.initialize_geofence_panel()

        self.IsDroneConfigInitialized = False

    def initialize_drone_config(self):
        self.GeofencePanel.grid_remove()
        self.SelectionPanel.grid_remove()

        self.ConfigPanelWidth = 1700
        self.ConfigPanelHeight = 860
        self.DroneConfigPanel = ctk.CTkFrame(self.TabDrones, height=self.ConfigPanelWidth, width=self.ConfigPanelHeight,
                                             fg_color="transparent")
        self.DroneConfigPanel.grid(row=0, column=0)
        ColorButtonConfig = "#bac1c5"
        self.ReturnImage = ImageTk.PhotoImage(Image.open("assets/BackIcon.png").resize((20, 20)))
        self.ReturnButton = ctk.CTkButton(self.DroneConfigPanel, text="", fg_color=ColorButtonConfig,
                                          image=self.ReturnImage
                                          , command=lambda i=0: self.restore_default_view())
        self.ReturnButton.place(x=30, y=10)
        self.DroneSettingsPanel_1 = ctk.CTkFrame(self.DroneConfigPanel, fg_color="#bac1c5",
                                                 width=int(self.ConfigPanelWidth / 4 - 30)
                                                 , height=int(self.ConfigPanelHeight * 0.8))
        self.DroneSettingsPanel_2 = ctk.CTkFrame(self.DroneConfigPanel, fg_color="#bac1c5",
                                                 width=int(self.ConfigPanelWidth / 4 - 30)
                                                 , height=int(self.ConfigPanelHeight * 0.8))
        self.DroneSettingsPanel_3 = ctk.CTkFrame(self.DroneConfigPanel, fg_color="#bac1c5",
                                                 width=int(self.ConfigPanelWidth / 4 - 30)
                                                 , height=int(self.ConfigPanelHeight * 0.8))
        self.DroneSettingsPanel_4 = ctk.CTkFrame(self.DroneConfigPanel, fg_color="#bac1c5",
                                                 width=int(self.ConfigPanelWidth / 4 - 30)
                                                 , height=int(self.ConfigPanelHeight * 0.8))
        self.DroneSettingsPanelList = [self.DroneSettingsPanel_1,
                                       self.DroneSettingsPanel_2,
                                       self.DroneSettingsPanel_3,
                                       self.DroneSettingsPanel_4]
        self.DroneSettingsValues = [[],[],[],[]]
        self.DroneSettingsFrames_1 = []

        self.show_drone_config_panels()

        # Proceed Button

        TestButton = ctk.CTkButton(self.DroneConfigPanel, command=lambda i=0: self.initialize_drone_control_panel(),
                                   fg_color=ColorButtonConfig,text="Proceed", text_color="black", font=("Helvetica", 14, "bold"))
        TestButton.place(x=180,y=10)


    def initialize_drone_control_panel(self):

        connection_status = []
        tabs = []

        for drone in self.DroneDataList:
            if drone.Status == "connected":
                connection_status.append(True)
                self.client.publish("miMain/autopilotService" + str(drone.DroneId+1) + "/startTelemetry")
            else:
                connection_status.append(False)


        time.sleep(2)
        self.DroneConfigPanel.grid_remove()
        self.ControlPanel = ctk.CTkFrame(self.TabDrones, height=850, width = 1660,
                                           fg_color="#bac1c5")
        self.ControlPanel.grid(row=0, column=0)
        self.ControlPanel.grid_propagate(False)

        # Creating panels
        self.DroneControlPanel = ctk.CTkFrame(self.ControlPanel, height=500, width=500, fg_color="#000000")
        self.DroneViewportPanel = ctk.CTkFrame(self.ControlPanel, height=830, width=1125, fg_color="#000000")

        self.DroneControlPanel.grid(row=0, column=0, padx= 10,pady=10, sticky="N")
        self.DroneControlPanel.grid_propagate(False)

        self.DroneViewportPanel.grid(row=0, column=1, padx=5, pady=10)
        self.DroneViewportPanel.grid_propagate(False)

        # Left section (70% width)
        self.DroneInfoPanel = ctk.CTkFrame(self.DroneControlPanel, height=500, width=350, fg_color="#faf5f5")
        self.DroneInfoPanel.grid(row=0, column=0, padx=0, pady=0, sticky="NSEW")
        self.DroneInfoPanel.grid_propagate(False)

        # Right section (30% width) for tabs
        self.TabSelectorPanel = ctk.CTkFrame(self.DroneControlPanel, height=500, width=150, fg_color="#aaaaaa")
        self.TabSelectorPanel.grid(row=0, column=1, padx=0, pady=0, sticky="NSEW")
        self.TabSelectorPanel.grid_propagate(False)


        self.create_tabs(tabs, self.selected_tab)
        self.create_main_panel_content(self.selected_tab)


        '''# Drone SELECTION panel
        self.DroneSelectionPanel = ctk.CTkFrame(self.DroneControlPanel, width=120, height=480, fg_color="#bac1c5")
        self.DroneSelectionPanel.grid(row=0, column=0,padx=10,pady=10, sticky="E")
        self.DroneSelectionPanel.grid_propagate(False) '''

        # Setting up the Canvas image
        self.DroneLabImage = ImageTk.PhotoImage(Image.open("assets/recintoDrone.png"))
        self.ViewportCanvas = ctk.CTkCanvas( self.DroneViewportPanel,height=830, width=1115)
        self.ViewportCanvas.grid(row=0, column=0)
        self.ViewportCanvas.create_image(552.5,415, image=self.DroneLabImage)

        #Drone selection buttons
        '''for i in range(0, self.SelectedNumberOfDrones):
            print("Check FS :" + str(i))
            ctk.CTkButton(self.DroneSelectionPanel, height=70, width=100, text="Drone "+str(i + 1), fg_color="#bac1c5",
                              text_color="white", font=("Helvetica", 16, "bold"),
                              command=lambda i=i: self.select_drone_control_option(i))'''
        #Drone drawing
        for i in self.DroneDataList:
            if i.Status == "connected":
                self.draw_drone(i)

    def create_tabs(self, tabs, selected_tab):

        for i in range(4):

            tab = ctk.CTkFrame(self.TabSelectorPanel, height=125, width=150,
                               fg_color="#faf5f5" if i == selected_tab else "#252629",)
            tab.grid(row=i * 2, column=0, padx=0, pady=0, sticky="EW")
            tab.grid_propagate(False)
            tab.grid_rowconfigure(0, weight=1)  # Allow row 0 to grow
            tab.grid_rowconfigure(1, weight=0)  # Set row 1 to minimum height

            tab_label = ctk.CTkLabel(tab, width= 100, text="Tab {}".format(i + 1) if self.DroneDataList[
                                                                             i].Status == "connected" else "DISCONNECTED",
                                     anchor=tkinter.CENTER, fg_color="#faf5f5" if i == selected_tab else "#252629", text_color="black"if self.DroneDataList[
                                                                             i].Status == "connected" else "white")

            tab_label.grid(row=0, column=0,columnspan=2, pady=10, sticky="NSWE")

            button1 = ctk.CTkButton(tab, text="RTL", width= 60, command=lambda i=i: self.drone_operate("RTL", i))
            button1.grid(row=1, column=0, padx=(10,5), pady=10, sticky="S")

            button2 = ctk.CTkButton(tab, text="land", width= 60, command=lambda i=i: self.drone_operate("Land", i))
            button2.grid(row=1, column=1, padx=(5,10), pady=10, sticky="S")

            tab.bind("<Button-1>", lambda e, i=i: self.select_tab( i, tabs))
            tabs.append(tab)

    def select_tab(self, index, tabs):
        if self.DroneDataList[index].Status == "connected":
            self.update_tabs(index, tabs)
            self.update_main_panel_content(index)

    def update_tabs(self, index, tabs):
        self.selected_tab = index
        for i, tab in enumerate(tabs):
            tab.configure(fg_color="#c3c6c9" if i == index else "#252629")
            for widget in tab.winfo_children():
                widget.configure(fg_color="#c3c6c9" if i == index else "#252629")

    def create_main_panel_content(self, index):
        # Create two side-by-side frames
        left_frame = ctk.CTkFrame(self.DroneInfoPanel, width=200, fg_color="#faf5f5")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="NSEW")

        # Define a function to be called when a button is clicked


        # Create buttons inside the left_frame
        buttons = []
        positions = ["NW", "N", "NE", "W", "E", "SW", "S", "SE"]
        for row in range(3):
            for col in range(3):
                if row == 1 and col == 1:
                    continue  # Skip the center position
                position = positions.pop(0)
                button = ctk.CTkButton(left_frame, text=position, width=60, height=60)
                button.grid(row=row, column=col, padx=5, pady=5)
                buttons.append(button)
                button.bind("<ButtonPress-1>", lambda event, tab=self.selected_tab: self.on_moving_press(position, tab))

        right_frame = ctk.CTkFrame(self.DroneInfoPanel, width=120, fg_color="#db7f7f")
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="NSEW")

        # Create buttons inside the right_frame
        button_texts = ["Arm", "Takeoff", "RTL", "Land"]
        for i, text in enumerate(button_texts):
            button = ctk.CTkButton(right_frame, text=text, fg_color="#808080", height=60,
                                   width = 100,command=lambda t=text: self.drone_operate(t,self.selected_tab))
            button.grid(row=i, column=0, padx=10, pady=10, sticky="NS")

        # Create the bottom frame that spans both side frames
        bottom_frame = ctk.CTkFrame(self.DroneInfoPanel, height=100, fg_color="#c3b4d1")
        bottom_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="NSEW")

        # Configure grid weights for proper resizing
        self.DroneInfoPanel.grid_rowconfigure(0, weight=1)
        self.DroneInfoPanel.grid_rowconfigure(1, weight=1)
        self.DroneInfoPanel.grid_columnconfigure(0, weight=1)
        self.DroneInfoPanel.grid_columnconfigure(1, weight=1)

    def update_main_panel_content(self, index):
        # Clear existing content
        for widget in self.DroneInfoPanel.winfo_children():
            widget.destroy()

        if self.DroneDataList[index].Status == "connected":
            # Add new content based on selected tab
            info_label = ctk.CTkLabel(self.DroneInfoPanel,
                                      text="Information for Tab {}".format(index + 1), fg_color="#c3c6c9",
                                      text_color="black")
            info_label.grid(row=0, column=0, padx=10, pady=10, sticky="W")
            # Add more widgets as needed for each tab

    def drone_move(self, position):
        print(f"Button {position} clicked")


    def drone_operate(self, button_text, drone_num):
        # Add your desired functionality here

        if button_text == "Arm":
            self.client.publish("miMain/autopilotService" + str(drone_num+1) + "/arm")
        if button_text == "Takeoff":
            self.client.publish("miMain/autopilotService" + str(drone_num+1) + "/takeOff")
        if button_text == "RTL":
            self.client.publish("miMain/autopilotService" + str(drone_num+1) + "/RTL")
        if button_text == "Land":
            self.client.publish("miMain/autopilotService" + str(drone_num+1) + "/Land")

        print(f" autopilotService'{drone_num}' has been  instucted to '{button_text}'")

    def on_moving_press(self, position, drone_num):
        print ("Nice click on 1 ")
        position_to_direction = {
            "N": "Forward",
            "W": "Left",
            "E": "Right",
            "S": "Back",
        }
        payload = position_to_direction.get(position)

        time.sleep(0.1)

        self.client.publish("miMain/autopilotService" + str(drone_num + 1) + "/move", payload)




    def draw_drone(self,drone):
        print("For drone : " + str(drone.DroneId))
        print("Printing Lat Lon etc:")
        print(drone.lat)
        print(drone.lon)
        x, y = ComputeCoords().convertToCoords([drone.lat, drone.lon])
        print("Printing conversion:")
        print(x)
        print(y)
        self.dronePoint = self.ViewportCanvas.create_oval(x-15, y-15, x+15, y+15, fill="red")

    def initialize_drone_controls(self):
        up_control = ctk.CTkButton(self.DroneControlPanel, text="UP", width= 50, height=50)
        up_control.place(x=50, y=50)
    def select_drone_control_option(self, droneIndex):

        pass
    def config_test_button(self):
        print("click")

    def share_config(self, DroneToBeCopied):
        for Drone in self.DroneDataList:
            if Drone.Status == "connected":
                print(Drone.DroneId)
                self.update_entry_from_slider(DroneToBeCopied.Fence_Altitude_Max, Drone, "Fence_Altitude_Max",
                                              self.DroneSettingsValues[Drone.DroneId][0])
                self.update_slider_from_entry(Drone, "Fence_Altitude_Max",self.DroneSettingsValues[Drone.DroneId][1],
                                              self.DroneSettingsValues[Drone.DroneId][0])

                self.DroneSettingsValues[Drone.DroneId][2].set(
                    self.optionMenu_number_to_attribute(DroneToBeCopied.Fence_Enabled))

                self.update_entry_from_slider(DroneToBeCopied.Geofence_Margin, Drone, "Geofence_Margin",
                                              self.DroneSettingsValues[Drone.DroneId][3])
                self.update_slider_from_entry(Drone, "Geofence_Margin", self.DroneSettingsValues[Drone.DroneId][4],
                                              self.DroneSettingsValues[Drone.DroneId][3])

                self.DroneSettingsValues[Drone.DroneId][5].set(
                    self.optionMenu_number_to_attribute(DroneToBeCopied.Geofence_Action))

                self.update_entry_from_slider(DroneToBeCopied.RTL_Altitude, Drone, "RTL_Altitude",
                                              self.DroneSettingsValues[Drone.DroneId][6])
                self.update_slider_from_entry(Drone, "RTL_Altitude", self.DroneSettingsValues[Drone.DroneId][7],
                                              self.DroneSettingsValues[Drone.DroneId][6])

                self.update_entry_from_slider(DroneToBeCopied.Pilot_Speed_Up, Drone, "Pilot_Speed_Up",
                                              self.DroneSettingsValues[Drone.DroneId][8])
                self.update_slider_from_entry(Drone, "Pilot_Speed_Up", self.DroneSettingsValues[Drone.DroneId][9],
                                              self.DroneSettingsValues[Drone.DroneId][8])

                self.DroneSettingsValues[Drone.DroneId][10].set(
                    self.optionMenu_number_to_attribute(DroneToBeCopied.FLTMode6))




    def initialize_config_options(self):
        DroneLabelFont = ctk.CTkFont("Helvetica", 23, "bold")
        for Drone in self.DroneDataList:
            DroneSettingsPanel = self.DroneSettingsPanelList[Drone.DroneId]
            DroneLabel = ctk.CTkLabel(DroneSettingsPanel, text=str("Drone " + str(Drone.DroneId + 1)),
                                      font=DroneLabelFont)
            DroneLabel.place(x=20, y=30)
            StatusLabel = ctk.CTkLabel(DroneSettingsPanel, text="Status:", font=("Helvetica", 17, "bold"))

            if Drone.Status == "connected":
                StatusLabelColor = ctk.CTkLabel(DroneSettingsPanel, text="Connected", font=("Helvetica", 17, "bold"),
                                                text_color="#299943")

                # Fence_Altitude_Max
                entry_fence_altitude, slider_fence_altitude = self.config_slider_frame(Drone, "Fence_Altitude_Max", "Geofence max altitude", 0,
                                         50, 300, 25)

                # Fence_Enabled
                optionMenu_fence_enabled = self.config_optionMenu_frame(Drone, "Fence_Enabled", "Fence status",
                                             1, ["Enabled", "Disabled"])


                # Geofence_Margin
                entry_geofence_margin, slider_geofence_margin = self.config_slider_frame(Drone, "Geofence_Margin", "Geofence margin", 2,
                                         1, 20, 19)

                # Geofence_Action
                optionMenu_geofence_action = self.config_optionMenu_frame(Drone, "Geofence_Action", "Geofence action",
                                             3, ["Enabled", "Disabled"])

                # RTL_Altitude
                entry_RTL_altitude, slider_RTL_altitude = self.config_slider_frame(Drone, "RTL_Altitude", "RTL Altitude", 4,
                                         400, 3200, 28)

                # Pilot_Speed_Up
                entry_pilot_speed, slider_pilot_speed = self.config_slider_frame(Drone, "Pilot_Speed_Up", "Pilot speed UP", 5,
                                         10, 500, 49)

                # FLTMode6
                optionMenu_FLT_mode = self.config_optionMenu_frame(Drone, "FLTMode6", "FLT Mode 6",
                                             6, ["RTL", "Land"])
                self.DroneSettingsValues[Drone.DroneId] = [entry_fence_altitude, slider_fence_altitude,
                                                 optionMenu_fence_enabled,
                                                 entry_geofence_margin, slider_geofence_margin,
                                                 optionMenu_geofence_action,
                                                 entry_RTL_altitude, slider_RTL_altitude,
                                                 entry_pilot_speed, slider_pilot_speed,
                                                 optionMenu_FLT_mode]

                copyConfigButton = ctk.CTkButton(self.DroneSettingsPanelList[Drone.DroneId],
                                                 text= "Copy config to other drones", height = 30, width= 200, fg_color= "#404659", hover_color="#2c2c3d",
                                                 command= lambda i=Drone: self.share_config(i))
                copyConfigButton.grid(row=7, column= 0, pady=40, padx=50)
            else:
                StatusLabelColor = ctk.CTkLabel(DroneSettingsPanel, text="Disconnected", font=("Helvetica", 17, "bold"),
                                                text_color="#992936")
            StatusLabel.place(x=20, y=55)
            StatusLabelColor.place(x=85, y=55)

    def config_optionMenu_frame(self, Drone, droneDataAttribute, primaryLabelText, row_position, options):
        # Configuration

        Padx_Frame = 5
        Pady_Frame = 5
        if row_position == 0:
            Pady_Frame = (100, 5)
        TextHeight = 8
        LabelPositionX = 20
        CurrentValuePositionX = 20
        TextBoxPositionX = 250
        FrameColor = "transparent"
        Width = self.ConfigPanelWidth / 4 - 30 - Padx_Frame * 2
        Height = 45

        # End Configuration

        droneDataAttributeValue = getattr(Drone, droneDataAttribute)

        if droneDataAttribute == "FLTMode6":
            print("Check1")
            print(int(droneDataAttributeValue))
            if int(droneDataAttributeValue) == 0 or int(droneDataAttributeValue) == 1:
                print("Check2")
                droneDataAttributeValue = 6
                setattr(Drone, droneDataAttribute, 6)

        currentAttributeValue = self.optionMenu_number_to_attribute(droneDataAttributeValue)

        DroneSettingsPanel = self.DroneSettingsPanelList[Drone.DroneId]

        Frame = ctk.CTkFrame(DroneSettingsPanel, width=Width, height=Height, fg_color=FrameColor)
        Label = ctk.CTkLabel(Frame, text=primaryLabelText, font=("Helvetica", 17, "bold"))
        Label.place(x=LabelPositionX, y=TextHeight)

        CurrentValue = ctk.CTkLabel(Frame, text="Current value : " + str(Drone.Fence_Enabled),
                                    font=("Helvetica", 11, "bold"), height=3)
        CurrentValue.place(x=CurrentValuePositionX, y=TextHeight + 23)

        optionMenu = ctk.CTkOptionMenu(Frame, values=options, height=25, width=125,fg_color= "#404659", button_color="#14241e", button_hover_color="#4a4246",
                                       command=lambda value: self.update_drone_attribute(Drone, droneDataAttribute,
                                                                                         value))
        optionMenu.place(x=TextBoxPositionX, y=TextHeight)
        optionMenu.set(currentAttributeValue)

        Frame.grid(row=row_position, column=0, padx=Padx_Frame, pady=Pady_Frame)
        Frame.grid_propagate(False)
        self.DroneSettingsFrames_1.append(Frame)

        return optionMenu
    def optionMenu_number_to_attribute(self,droneDataAttributeValue):
        currentAttributeValue = 0
        if droneDataAttributeValue == 0:
            currentAttributeValue = "Disabled"
        elif droneDataAttributeValue == 1:
            currentAttributeValue = "Enabled"
        elif droneDataAttributeValue == 6:
            currentAttributeValue = "RTL"
        elif droneDataAttributeValue == 9:
            currentAttributeValue = "Land"
        return currentAttributeValue
    def update_drone_attribute(self, Drone, droneDataAttribute, selected_option):
        # Map "Yes" and "No" to 1 and 0
        value_map = {"Enabled": 1, "Disabled": 0, "RTL": 6, "Land": 9}
        value = int(value_map[selected_option])
        setattr(Drone, droneDataAttribute, value)
        print(
            f"Updated {droneDataAttribute} to {value} based on option '{selected_option}' for drone {Drone.DroneId + 1}")

    def config_slider_frame(self, Drone, droneDataAttribute, primaryLabelText, row_position, minValue, maxValue, steps):
        Padx_Frame = 5
        Pady_Frame = 5
        if row_position == 0:
            Pady_Frame = (100, 5)
        TextHeight = 8
        LabelPositionX = 20
        CurrentValuePositionX = 20
        TextBoxPositionX = 250
        FrameColor = "transparent"
        Width = self.ConfigPanelWidth / 4 - 30 - Padx_Frame * 2
        Height = 45
        droneDataAttributeValue = getattr(Drone, droneDataAttribute)
        DroneSettingsPanel = self.DroneSettingsPanelList[Drone.DroneId]

        Frame = ctk.CTkFrame(DroneSettingsPanel, width=Width, height=Height, fg_color=FrameColor)
        Label = ctk.CTkLabel(Frame, text=primaryLabelText, font=("Helvetica", 17, "bold"))
        Label.place(x=LabelPositionX, y=TextHeight)

        CurrentValueLabel = ctk.CTkLabel(Frame, text="Current value : " + str(droneDataAttributeValue),
                                         font=("Helvetica", 11, "bold"), height=3)
        CurrentValueLabel.place(x=CurrentValuePositionX, y=TextHeight + 23)

        entry = ctk.CTkEntry(Frame, width=90, fg_color="#e4eaeb")
        entry.insert(0, droneDataAttributeValue)
        entry.place(x=TextBoxPositionX + 15, y=TextHeight - 10)

        slider = ctk.CTkSlider(Frame, from_=minValue, to=maxValue, number_of_steps=steps, width=125)
        slider.configure(
            command=lambda value: self.update_entry_from_slider(value, Drone, droneDataAttribute, entry))
        slider.set(droneDataAttributeValue)
        slider.place(x=TextBoxPositionX, y=TextHeight + 20)

        entry.bind("<Return>", lambda event: self.update_slider_from_entry(Drone, droneDataAttribute,
                                                                                          slider,
                                                                                          entry))
        Frame.grid(row=row_position, column=0, padx=Padx_Frame, pady=Pady_Frame)
        Frame.grid_propagate(False)

        self.DroneSettingsFrames_1.append(Frame)
        return entry, slider
    def update_config_frame(self, Drone):

        self.DroneSettingsValues[Drone.DroneId][0].delete(0, ctk.END)
        self.DroneSettingsValues[Drone.DroneId][0].insert(0, str(Drone.Fence_Altitude_Max))
        self.DroneSettingsValues[Drone.DroneId][1].set(float(Drone.Fence_Altitude_Max))

        ConvertedParam1 = "Enabled" if Drone.Fence_Enabled==1 else "Disabled"
        self.DroneSettingsValues[Drone.DroneId][2].set(ConvertedParam1)

        self.DroneSettingsValues[Drone.DroneId][3].delete(0, ctk.END)
        self.DroneSettingsValues[Drone.DroneId][3].insert(0, str(Drone.Geofence_Margin))
        self.DroneSettingsValues[Drone.DroneId][4].set(float(Drone.Geofence_Margin))

        ConvertedParam2 = "Enabled" if Drone.Geofence_Action == 1 else "Disabled"
        self.DroneSettingsValues[Drone.DroneId][5].set(ConvertedParam2)

        self.DroneSettingsValues[Drone.DroneId][6].delete(0, ctk.END)
        self.DroneSettingsValues[Drone.DroneId][6].insert(0, str(Drone.RTL_Altitude))
        self.DroneSettingsValues[Drone.DroneId][7].set(float(Drone.RTL_Altitude))

        self.DroneSettingsValues[Drone.DroneId][8].delete(0, ctk.END)
        self.DroneSettingsValues[Drone.DroneId][8].insert(0, str(Drone.Pilot_Speed_Up))
        self.DroneSettingsValues[Drone.DroneId][9].set(float(Drone.Pilot_Speed_Up))

        ConvertedParam3 = "RTL" if Drone.Geofence_Action == 1 else "Land"
        self.DroneSettingsValues[Drone.DroneId][10].set(ConvertedParam3)
    def update_entry_from_slider(self, value, Drone, droneDataAttribute, entry):
        entry.delete(0, ctk.END)
        entry.insert(0, str(value))
        setattr(Drone, droneDataAttribute, value)

    def update_slider_from_entry(self, Drone, droneDataAttribute, slider, entry):
        # Update the slider from the entry
        value = float(entry.get())
        slider.set(value)
        setattr(Drone, droneDataAttribute, value)

    def show_drone_config_panels(self):

        for i in range(1, 5):
            drone_settings_panel_name = f'DroneSettingsPanel_{i}'
            drone_panel = getattr(self, drone_settings_panel_name)
            drone_panel.grid_remove()

        for i in range(1, self.SelectedNumberOfDrones + 1):
            if i == 1:
                self.client.publish("miMain/autopilotService1/connect")
                print("Trying to connect to drone 1")
            elif i == 2:
                self.client.publish("miMain/autopilotService2/connect")
                print("Trying to connect to drone 2")
            elif i == 3:
                self.client.publish("miMain/autopilotService3/connect")
                print("Trying to connect to drone 3")
            elif i == 4:
                self.client.publish("miMain/autopilotService4/connect")
                print("Trying to connect to drone 4")
            drone_settings_panel_name = f'DroneSettingsPanel_{i}'
            drone_panel = getattr(self, drone_settings_panel_name)
            drone_panel.grid_propagate(False)
            if i == 1:
                drone_panel.grid(row=0, column=i, padx=(30, 10), pady=(50, 50))
            else:
                drone_panel.grid(row=0, column=i, padx=(10, 10), pady=(50, 50))
        time.sleep(4)
        self.initialize_config_options()

    def restore_drone_config_view(self):
        self.GeofencePanel.grid_remove()
        self.SelectionPanel.grid_remove()
        self.DroneConfigPanel.grid(row=0, column=0)
        self.show_drone_config_panels()

    def restore_default_view(self):
        self.DroneConfigPanel.grid_remove()
        self.GeofencePanel.grid(row=0, column=1, padx=(0, 0), pady=0)
        self.SelectionPanel.grid(row=0, column=0, padx=(0, 10), pady=0)

    def initialize_geofence_panel(self):
        self.GeofencePanel = ctk.CTkFrame(self.TabDrones, height=860, width=950 + self.GeofenceWidthEdge,
                                          fg_color="#bac1c5")
        self.GeofencePanel.grid(row=0, column=1, padx=(0, 0), pady=0)
        self.GeofencePanel.grid_propagate(False)

        # Search panel

        self.SearchPanel = ctk.CTkFrame(self.GeofencePanel, width=888 + self.GeofenceWidthEdge, height=310,
                                        fg_color=self.BackgroundColor)
        self.SearchPanel.grid_propagate(False)
        self.SearchPanel.grid(row=1, column=0, pady=(5, 0), padx=(30, 0))

        # Search bar

        self.SearchBox = ctk.CTkTextbox(self.SearchPanel, height=20, width=200)
        self.SearchBox.grid(row=0, column=0, padx=(50, 0), pady=(5, 0), sticky="w")

        # Number of drones filter selection

        self.NumberFilterButtonList: List[ctk.CTkButton] = []
        self.CachedSelection = 0
        self.SelectedCard = None
        TotalNumberOfDrones = 4

        self.NumberFilterButtonList.append(
            ctk.CTkButton(self.SearchPanel, height=30, width=30, text="*", fg_color="#feffd4", text_color="black",
                          hover_color="#c9c1a3", hover=True, font=("Helvetica", 16, "bold"),
                          command=lambda i=0: self.RestoreAllGeofenceList(
                          )))

        self.NumberFilterButtonList[0].grid(row=0, column=0, pady=5, padx=280 + 35 * 0, sticky="w")
        for i in range(0, TotalNumberOfDrones + 1):
            self.NumberFilterButtonList.append(
                ctk.CTkButton(self.SearchPanel, height=30, width=30, text=str(i + 1), fg_color="#feffd4",
                              text_color="black", hover_color="#c9c1a3", hover=True, font=("Helvetica", 16, "bold"),
                              command=lambda i=i: self.ButtonFilterNumberPressed(i)))
            self.NumberFilterButtonList[i].grid(row=0, column=0, pady=5, padx=280 + 35 * i, sticky="w")

        # Favourite button

        self.StateFavButton = False
        self.FavOffImage = ImageTk.PhotoImage(Image.open("assets/FavIconOff.png").resize((20, 20)))
        self.FavOnImage = ImageTk.PhotoImage(Image.open("assets/FavIconOn.png").resize((20, 20)))
        self.FavButton = ctk.CTkButton(self.SearchPanel, height=30, width=20, text="", image=self.FavOffImage,
                                       fg_color="#d4cdcb",
                                       command=self.FavButtonClicked)
        self.FavButton.grid(row=0, column=0, sticky="w", padx=(10, 10), pady=(5, 0))

        # Scrollable panel

        self.ScrollablePanel = ctk.CTkScrollableFrame(self.SearchPanel, width=850 + self.GeofenceWidthEdge, height=220,
                                                      orientation="horizontal",
                                                      fg_color="#d4cdcb", scrollbar_button_color="#2e2e2e")
        self.ScrollablePanel.grid(row=2, column=0, padx=(10, 10), pady=10)

        # Geofence canvas

        self.SelectedGeofenceName = ""
        self.DroneLabImage = ImageTk.PhotoImage(Image.open("assets/DroneLabImageLimited.png"))
        self.GeofenceCanvas = ctk.CTkCanvas(self.GeofencePanel, width=900, height=500)

        self.GeofenceCanvas.grid(row=0, column=0, pady=(25, 0), padx=(30, 0))
        self.GeofenceCanvas.create_image(450, 250, image=self.DroneLabImage)

        # Reading JSON data
        self.GeofenceList: List[Geofence.Geofence] = []
        self.InitializeList()

        # Reset JSON info button

        self.ResetIcon = ImageTk.PhotoImage(Image.open("assets/ResetIcon.png").resize((30, 30)))
        self.ResetButton = ctk.CTkButton(self.SearchPanel, height=40, width=40, text="", image=self.ResetIcon,
                                         command=self.RefreshGeofenceList, fg_color="#d4cdcb")
        self.ResetButton.grid(row=0, column=0, sticky="e", padx=(10, 37), pady=(5, 0))

        # Geofence list setup
        self.GeofenceCardList: List[List[ctk.CTkButton]] = []
        self.GeofenceButtonList: List[ctk.CTkButton] = []
        self.MapGeofenceToCard = None
        self.SetGeofenceButtonList(self.GeofenceList)
        self.Tab.configure(command=self.ResetGeofenceList)

        # Selected geofence

        self.SelectedGeofence = None

        # Testing Button

        # self.TestingButton = ctk.CTkButton(self.SelectionPanel, command=lambda i=i: self.TestingButtonClicked())
        # self.TestingButton.place(x=10, y=10)

    def initialize_selection_panel(self):
        # Selection Panel section : This panel will contain the interface for the drone selection

        self.SelectionPanel = ctk.CTkFrame(self.TabDrones, height=860, width=727 - self.GeofenceWidthEdge,
                                           fg_color="#bac1c5")
        self.SelectionPanel.grid(row=0, column=0, padx=(0, 10), pady=0)
        self.SelectionPanel.grid_propagate(False)

        # Selection text

        self.SelectionText = ctk.CTkLabel(self.SelectionPanel,
                                          text="Select the number of drones",
                                          font=("Helvetica", 24, "bold"))
        self.SelectionText.place(x=120, y=50)

        DroneSelectionButtonHeight = 200
        DroneSelectionButtonWidth = 105
        PadYVarUP = 140
        PadYVarDown = 10

        # Drone panels : Here we will contain the button, switches and text boxes for each  of the options

        self.SelectedNumberOfDrones = 0

        self.DronePanel_1 = ctk.CTkFrame(self.SelectionPanel, width=120, height=320, fg_color="transparent")
        self.DronePanel_1.grid_propagate(False)
        self.DronePanel_1.grid(row=0, column=0, padx=(30, 5), pady=(200, PadYVarDown))

        self.DronePanel_2 = ctk.CTkFrame(self.SelectionPanel, width=120, height=320, fg_color="transparent")
        self.DronePanel_2.grid_propagate(False)
        self.DronePanel_2.grid(row=0, column=1, padx=(5), pady=(200, PadYVarDown))

        self.DronePanel_3 = ctk.CTkFrame(self.SelectionPanel, width=120, height=320, fg_color="transparent")
        self.DronePanel_3.grid_propagate(False)
        self.DronePanel_3.grid(row=0, column=2, padx=(5), pady=(200, PadYVarDown))

        self.DronePanel_4 = ctk.CTkFrame(self.SelectionPanel, width=120, height=320, fg_color="transparent")
        self.DronePanel_4.grid_propagate(False)
        self.DronePanel_4.grid(row=0, column=3, padx=(5), pady=(200, PadYVarDown))

        # Drone buttons

        self.ImageNumberOne = ctk.CTkImage(light_image=Image.open('assets/NumberOne.png'),
                                           dark_image=Image.open('assets/NumberOne.png'),
                                           size=(50, 50))
        self.ImageNumberTwo = ctk.CTkImage(light_image=Image.open('assets/NumberTwo.png'),
                                           dark_image=Image.open('assets/NumberTwo.png'),
                                           size=(50, 50))
        self.ImageNumberThree = ctk.CTkImage(light_image=Image.open('assets/NumberThree.png'),
                                             dark_image=Image.open('assets/NumberThree.png'),
                                             size=(50, 50))
        self.ImageNumberFour = ctk.CTkImage(light_image=Image.open('assets/NumberFour.png'),
                                            dark_image=Image.open('assets/NumberFour.png'),
                                            size=(50, 50))

        BorderMargin = 2

        self.DroneSelectionButtonFrame_1 = ctk.CTkFrame(self.DronePanel_1,
                                                        width=DroneSelectionButtonWidth + 2 * BorderMargin,
                                                        height=DroneSelectionButtonHeight + 2 * BorderMargin,
                                                        fg_color="black")
        self.DroneSelectionButtonFrame_2 = ctk.CTkFrame(self.DronePanel_2,
                                                        width=DroneSelectionButtonWidth + 2 * BorderMargin,
                                                        height=DroneSelectionButtonHeight + 2 * BorderMargin,
                                                        fg_color="black")
        self.DroneSelectionButtonFrame_3 = ctk.CTkFrame(self.DronePanel_3,
                                                        width=DroneSelectionButtonWidth + 2 * BorderMargin,
                                                        height=DroneSelectionButtonHeight + 2 * BorderMargin,
                                                        fg_color="black")
        self.DroneSelectionButtonFrame_4 = ctk.CTkFrame(self.DronePanel_4,
                                                        width=DroneSelectionButtonWidth + 2 * BorderMargin,
                                                        height=DroneSelectionButtonHeight + 2 * BorderMargin,
                                                        fg_color="black")

        self.DroneSelectionButton_1 = ctk.CTkButton(self.DronePanel_1, width=DroneSelectionButtonWidth,
                                                    height=DroneSelectionButtonHeight, text="",
                                                    command=self.DroneButton1Clicked, image=self.ImageNumberOne,
                                                    fg_color="#9fc6f5")
        self.DroneSelectionButton_2 = ctk.CTkButton(self.DronePanel_2, width=DroneSelectionButtonWidth,
                                                    height=DroneSelectionButtonHeight, text="",
                                                    command=self.DroneButton2Clicked, image=self.ImageNumberTwo,
                                                    fg_color="#9fc6f5")
        self.DroneSelectionButton_3 = ctk.CTkButton(self.DronePanel_3, width=DroneSelectionButtonWidth,
                                                    height=DroneSelectionButtonHeight, text="",
                                                    command=self.DroneButton3Clicked, image=self.ImageNumberThree,
                                                    fg_color="#9fc6f5")
        self.DroneSelectionButton_4 = ctk.CTkButton(self.DronePanel_4, width=DroneSelectionButtonWidth,
                                                    height=DroneSelectionButtonHeight, text="",
                                                    command=self.DroneButton4Clicked, image=self.ImageNumberFour,
                                                    fg_color="#9fc6f5")

        self.DroneSelectionButton_1.grid(row=0, column=0, padx=(5, 0))
        self.DroneSelectionButtonFrame_1.grid(row=0, column=0, padx=(5, 0))
        self.DroneSelectionButton_2.grid(row=0, column=1, padx=(5, 0))
        self.DroneSelectionButtonFrame_2.grid(row=0, column=1, padx=(5, 0))
        self.DroneSelectionButton_3.grid(row=0, column=2, padx=(5, 0))
        self.DroneSelectionButtonFrame_3.grid(row=0, column=2, padx=(5, 0))
        self.DroneSelectionButton_4.grid(row=0, column=3, padx=(5, 0))
        self.DroneSelectionButtonFrame_4.grid(row=0, column=3, padx=(5, 0))

        # Proceed button

        self.Proceed = ctk.CTkButton(self.SelectionPanel, width=150, height=30, text="Proceed",
                                     fg_color=self.GeneralButtonColor,
                                     command=lambda i=0: self.ProceedButton())
        self.Proceed.place(x=225, y=550)

        self.ErrorPanel = None

        # Simulation/Production Switch

        SwitchPositionX = 175
        SwitchPositionY = 140

        self.IsSimulation = True

        self.SimulationProdLabel = ctk.CTkLabel(self.SelectionPanel, text="Simulation", font=("Helvetica", 13, "bold"))
        self.SimulationProdSwitch = ctk.CTkSwitch(self.SelectionPanel, text="Production",
                                                  font=("Helvetica", 13, "bold"),
                                                  command=self.ProdSimulationSwitched)
        self.SimulationProdLabel.place(x=SwitchPositionX, y=SwitchPositionY)
        self.SimulationProdSwitch.place(x=SwitchPositionX + 72, y=SwitchPositionY + 2)

        # Direct/Global switches
        self.DirectGlobalSwitchesList = []

        # Port panel

        self.PortPanelList = []

    def DroneButton1Clicked(self):
        self.ButtonFilterNumberPressed(0)
        self.DroneSelectionButton_1.configure(state="disabled", fg_color="#295e9e")
        self.DroneSelectionButton_2.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_3.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_4.configure(state='normal', fg_color="#9fc6f5")
        self.SelectedNumberOfDrones = 1
        self.RegeneratePortCard()
        self.RegenerateGlobalDirectSwitch()

    def DroneButton2Clicked(self):
        self.ButtonFilterNumberPressed(1)
        self.DroneSelectionButton_1.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_2.configure(state="disabled", fg_color="#295e9e")
        self.DroneSelectionButton_3.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_4.configure(state='normal', fg_color="#9fc6f5")
        self.SelectedNumberOfDrones = 2
        self.RegeneratePortCard()
        self.RegenerateGlobalDirectSwitch()

    def DroneButton3Clicked(self):
        self.ButtonFilterNumberPressed(2)
        self.DroneSelectionButton_1.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_2.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_3.configure(state="disabled", fg_color="#295e9e")
        self.DroneSelectionButton_4.configure(state='normal', fg_color="#9fc6f5")
        self.SelectedNumberOfDrones = 3
        self.RegeneratePortCard()
        self.RegenerateGlobalDirectSwitch()

    def DroneButton4Clicked(self):
        self.ButtonFilterNumberPressed(3)
        self.DroneSelectionButton_1.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_2.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_3.configure(state='normal', fg_color="#9fc6f5")
        self.DroneSelectionButton_4.configure(state="disabled", fg_color="#295e9e")
        self.SelectedNumberOfDrones = 4
        self.RegeneratePortCard()
        self.RegenerateGlobalDirectSwitch()

    def ProceedButton(self):
        if self.ErrorPanel != None:
            self.ErrorPanel.destroy()
        self.ErrorPanel = ctk.CTkFrame(self.SelectionPanel, width=554, height=250, fg_color="#262626")
        self.ErrorPanel.grid_propagate(False)
        ErrorList = []
        ErrorFound = False
        if self.SelectedGeofence is None:
            ErrorFound = True
            ErrorList.append(
                ctk.CTkLabel(self.ErrorPanel, text="Select a geofence before continuing.", fg_color="transparent",
                             font=("Helvetica", 14, "bold"), text_color="white"))
        if self.SelectedNumberOfDrones == 0:
            ErrorFound = True
            ErrorList.append(
                ctk.CTkLabel(self.ErrorPanel, text="Select the desired number of drones before continuing.",
                             fg_color="transparent",
                             font=("Helvetica", 14, "bold"), text_color="white"))
        if self.SelectedGeofence is not None and self.SelectedNumberOfDrones != 0:
            if self.SelectedGeofence.DroneCount != self.SelectedNumberOfDrones:
                ErrorFound = True
                ErrorList.append(
                    ctk.CTkLabel(self.ErrorPanel,
                                 text="The selected geofence is not suited for the number of drones selected.",
                                 fg_color="transparent",
                                 font=("Helvetica", 14, "bold"), text_color="white"))
        if not ErrorFound:
            if not self.IsDroneConfigInitialized:
                self.initialize_drone_config()
            else:
                self.restore_drone_config_view()
        if ErrorFound:
            self.ErrorPanel.place(x=10, y=600)
            WarningLabel = ctk.CTkLabel(self.ErrorPanel, text="Warning:", fg_color="transparent",
                                        font=("Helvetica", 14, "bold"), text_color="Yellow")
            WarningLabel.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="W")
            Index = 1
            for i in ErrorList:
                i.grid(row=Index, column=0, padx=20, pady=(5, 5), sticky="W")
                Index += 1

    def TestingButtonClicked(self):
        if self.SelectedGeofence != None:
            print(self.SelectedGeofence.GetName())

    def ProdSimulationSwitched(self):
        if self.IsSimulation:
            self.IsSimulation = False
            self.RegenerateGlobalDirectSwitch()
            self.RegeneratePortCard()
        else:
            self.IsSimulation = True
            self.RegeneratePortCard()
            self.RegenerateGlobalDirectSwitch()

    def RegenerateGlobalDirectSwitch(self):
        for i in self.DirectGlobalSwitchesList:
            values = i.values()
            for k in values:
                k.destroy()
        self.DirectGlobalSwitchesList.clear()

        if self.SelectedNumberOfDrones != 0:
            for i in range(1, self.SelectedNumberOfDrones + 1):
                drone_panel_name = f'DronePanel_{i}'
                drone_panel = getattr(self, drone_panel_name)

                label = ctk.CTkLabel(drone_panel, text="Global", font=("Helvetica", 12, "bold"))
                switch = ctk.CTkSwitch(drone_panel, text="Direct", font=("Helvetica", 12, "bold"), width=40)

                label.place(x=00, y=210)
                switch.place(x=38, y=212)

                PanelDict = {
                    "label": label,
                    "switch": switch,
                }

                self.DirectGlobalSwitchesList.append(PanelDict)

    def RegeneratePortCard(self):
        for i in self.PortPanelList:
            values = i.values()
            for k in values:
                k.destroy()
        self.PortPanelList.clear()

        if not self.IsSimulation:
            if self.SelectedNumberOfDrones != 0:
                for i in range(1, self.SelectedNumberOfDrones + 1):
                    drone_panel_name = f'DronePanel_{i}'
                    drone_panel = getattr(self, drone_panel_name)

                    mainFrame = ctk.CTkFrame(drone_panel, width=120, fg_color="transparent")
                    label = ctk.CTkLabel(mainFrame, text="Port")
                    textBox = ctk.CTkTextbox(mainFrame, height=30, width=110)

                    mainFrame.place(y=235)
                    label.place(y=5, x=45)
                    textBox.place(y=30, x=5)

                    PanelDict = {
                        "mainFrame": mainFrame,
                        "label": label,
                        "textBox": textBox
                    }

                    self.PortPanelList.append(PanelDict)

    def SetGeofenceButtonList(self, GeofenceList):
        if len(GeofenceList) > 0:
            for i in self.GeofenceCardList:
                for k in i:
                    k.destroy()
            self.GeofenceCardList.clear()
            if self.MapGeofenceToCard is not None:
                self.MapGeofenceToCard.clear()
            Index = 0
            image = Image.open("assets/GeofenceTemplateImage.png")
            for i in GeofenceList:

                # In order to create an image that is the union of the template image and the points present in each
                # geofence, we copy the template image and draw on it using the .Draw method. The way we retrieve points
                # from the geofence is the same as when we draw on the main canvas when we select a geofence.

                img = image.copy()
                draw = ImageDraw.Draw(img)

                # For the color palette we define [red, blue, green, yellow] with a custom value of alpha
                Alpha = 92
                ColorPalette = [(255, 0, 0, Alpha), (0, 0, 255, Alpha), (0, 255, 0, Alpha), (255, 255, 0, Alpha)]
                ColorIndex = 0

                # In this for loop we are taking each polygon from the points list. Each polygon is a list of
                # dictionaries, which only have defined the x and the y. After retrieving the x and the y (after
                # casting the dict to a list we perform an adjustment on the image, as the template has different
                # dimensions to the original drone lab image

                for Polygon in i.Points:
                    InPoints = []
                    for Point in range(len(list(Polygon))):
                        InPoints.append(
                            tuple([list(Polygon[Point].values())[0] - 62, list(Polygon[Point].values())[1] - 80]))
                    draw.polygon(InPoints, fill=ColorPalette[ColorIndex])
                    ColorIndex += 1

                # The resizing must be done at the end, so the geofence is drawn properly

                img_resized = img.resize((280, 150))
                TemplateImage = ImageTk.PhotoImage(img_resized)

                CurrentCard = []
                CurrentCard.append(ctk.CTkFrame(self.ScrollablePanel, fg_color="black", width=274, height=204))
                CurrentCard.append(
                    ctk.CTkButton(CurrentCard[0], fg_color="#baaea6", text_color="black", hover_color="#e1edd8",
                                  text=i.Name, width=270, height=200, image=TemplateImage, compound="bottom"))
                CurrentCard[1].configure(command=lambda i=i: self.GeofenceSelected(i))
                CurrentCard.append(
                    ctk.CTkButton(CurrentCard[0], fg_color="#2e1200", bg_color="#baaea6", text_color="white", width=20,
                                  text=str(i.DroneCount),
                                  hover=False, state="disabled"))

                CurrentCard[0].grid(row=0, column=Index, pady=1, padx=2)
                CurrentCard[0].grid_propagate(False)
                CurrentCard[1].grid(row=0, column=0, padx=2, pady=2)
                CurrentCard[1].grid_propagate(False)
                CurrentCard[2].grid(row=0, column=0, sticky="ne", padx=5, pady=5)
                Index += 1

                self.GeofenceCardList.append(CurrentCard)

            self.MapGeofenceToCard = {geofence: card for geofence, card in zip(GeofenceList, self.GeofenceCardList)}
            self.HighlightSelectedGeofence()
        else:
            for i in self.GeofenceCardList:
                for k in i:
                    k.destroy()
            self.GeofenceCardList.clear()

    def RestoreAllGeofenceList(self):
        self.CachedSelection = 0
        self.RegenerateGeofenceList()
        for i in self.NumberFilterButtonList:
            i.configure(state="normal", fg_color="#feffd4", text_color="black", hover_color="#c9c1a3", hover=True,
                        font=("Helvetica", 16, "bold"))
        self.NumberFilterButtonList[0].configure(state="disabled", fg_color="#d1a019",
                                                 text_color_disabled="black")

    def FavButtonClicked(self):
        if not self.StateFavButton:
            self.FavButton.configure(image=self.FavOnImage)
            self.StateFavButton = True
            self.RegenerateGeofenceList()

        else:
            self.FavButton.configure(image=self.FavOffImage)
            self.StateFavButton = False
            self.RegenerateGeofenceList()

    def HighlightSelectedGeofence(self):
        for k in range(len(list(self.MapGeofenceToCard.values()))):
            if list(self.MapGeofenceToCard.keys())[k].Name == self.SelectedGeofenceName:
                list(self.MapGeofenceToCard.values())[k][1].configure(fg_color="#807473", state="disabled")
            else:
                list(self.MapGeofenceToCard.values())[k][1].configure(fg_color="#baaea6", state="normal")

    def GetFavoriteGeofence(self, GeofenceList):
        ReturnGeofenceList = []
        for i in GeofenceList:
            if i.IsGeofenceFav and i.DroneCount == self.CachedSelection or i.IsGeofenceFav and self.CachedSelection == 0:
                ReturnGeofenceList.append(i)
        return ReturnGeofenceList

    def GeofenceSelected(self, Geofence):
        self.GeofenceCanvas.delete("polygon")
        self.SelectedGeofence = Geofence
        self.SelectedGeofenceName = Geofence.Name
        self.HighlightSelectedGeofence()

        ColorPalette = ["red", "blue", "green", "yellow"]
        ColorIndex = 0
        for k in Geofence.Points:
            InPoints = []
            for j in range(len(list(k))):
                InPoints.append(tuple(list(k)[j].values()))
            self.GeofenceCanvas.create_polygon(InPoints, fill=ColorPalette[ColorIndex], stipple="gray50",
                                               tags="polygon")
            ColorIndex += 1

    def InitializeList(self):
        self.ResetGeofenceList()

    def RefreshGeofenceList(self):
        self.ResetGeofenceList()
        self.RegenerateGeofenceList()

    def ResetGeofenceList(self):
        File = open('data/GeofenceData.json')
        Data = json.load(File)
        GeofenceList = []
        for i in Data['GeofenceList']:
            Values = i.values()
            GeofenceVar = Geofence.Geofence(
                list(Values)[0],
                list(Values)[1],
                list(Values)[2],
                list(Values)[3],
                list(Values)[4])
            GeofenceList.append(GeofenceVar)
        self.GeofenceList = GeofenceList

    def IsGeofenceInList(self, Geofence):
        Index = 0
        for i in self.GeofenceList:
            if Geofence.__eq__(i):
                return True
        return False

    def ButtonFilterNumberPressed(self, Number):
        self.CachedSelection = Number + 1
        self.RegenerateGeofenceList()

        # Changing the appearance of the currently selected option and the other options
        Index = 0
        for i in self.NumberFilterButtonList:
            i.configure(state="normal", fg_color="#feffd4", text_color="black", hover_color="#c9c1a3", hover=True,
                        font=("Helvetica", 16, "bold"))
            if Index == Number + 1:
                i.configure(state="disabled", fg_color="#d1a019", text_color_disabled="black")
            Index += 1

    def FilterByNumber(self, Number):
        GeofenceList = []
        for i in self.GeofenceList:
            if i.DroneCount == Number + 1:
                if self.StateFavButton and i.IsGeofenceFav or not self.StateFavButton:
                    GeofenceList.append(i)
        self.CachedSelection = Number + 1
        self.SetGeofenceButtonList(GeofenceList)

    def RegenerateGeofenceList(self):
        GeofenceListToDisplay = []
        for i in self.GeofenceList:
            # If CachedSelection == 0 we are displaying without filtering by any number of drones
            if self.CachedSelection == 0:
                if self.StateFavButton:
                    if i.IsGeofenceFav == self.StateFavButton:
                        GeofenceListToDisplay.append(i)
                else:
                    GeofenceListToDisplay.append(i)
            elif i.DroneCount == self.CachedSelection:
                if self.StateFavButton:
                    if i.IsGeofenceFav == self.StateFavButton:
                        GeofenceListToDisplay.append(i)
                else:
                    GeofenceListToDisplay.append(i)
        self.SetGeofenceButtonList(GeofenceListToDisplay)

    def register_callback(self, callback):
        """ Register a callback to be called when the value needs to be updated. """
        self.callbacks.append(callback)

    def notify_callbacks(self, new_value):
        """ Notify all registered callbacks with the new value. """
        for callback in self.callbacks:
            callback(new_value)




root = App()
root.mainloop()
