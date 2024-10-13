from GeofenceClass import Geofence
class DroneInfo:
    def __init__(self,
                 geofence: Geofence = None,
                 DroneId: int = 0,
                 Status: str = "disconnected",
                 Fence_Altitude_Max: float = 0,
                 Fence_Enabled: int = 0,
                 Geofence_Margin: float = 0,
                 Geofence_Action: int = 0,
                 RTL_Altitude: float = 0,
                 Pilot_Speed_Up: float = 0,
                 FLTMode6: float = 0,
                 WP_YAW_BEHAVIOR: int = 0,
                 Vel: float = 0,
                 Alt: float = 0,
                 State: float = 0,
                 Lat: float = 0,
                 Lon: float = 0,
                 Heading: float = 0
                 ):
        self.DroneId = DroneId
        self.Status = Status
        self.Fence_Altitude_Max = Fence_Altitude_Max
        self.Fence_Enabled = Fence_Enabled
        self.Geofence_Margin = Geofence_Margin
        self.Geofence_Action = Geofence_Action
        self.RTL_Altitude = RTL_Altitude
        self.Pilot_Speed_Up = Pilot_Speed_Up
        self.FLTMode6 = FLTMode6
        self.WP_YAW_BEHAVIOR = WP_YAW_BEHAVIOR

        self.vel = Vel
        self.alt = Alt
        self.state = State
        self.lat = Lat
        self.lon = Lon
        self.heading = Heading

        self.geofence = geofence

    def setDroneInfoParameters(self, Fence_Altitude_Max, Fence_Enabled, Geofence_Margin, Geofence_Action, RTL_Altitude,
                               Pilot_Speed_Up, FLTMode6, WP_YAW_BEHAVIOR):
        self.Fence_Altitude_Max = Fence_Altitude_Max
        self.Fence_Enabled = Fence_Enabled
        self.Geofence_Margin = Geofence_Margin
        self.Geofence_Action = Geofence_Action
        self.RTL_Altitude = RTL_Altitude
        self.Pilot_Speed_Up = Pilot_Speed_Up
        self.FLTMode6 = FLTMode6
        self.WP_YAW_BEHAVIOR = WP_YAW_BEHAVIOR

    def setTelemetryInfo(self, value, parameter):
        setattr(self, parameter, value)
