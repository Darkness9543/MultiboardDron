class Geofence:

    def __init__(self,
                 DroneCount: int = 2,
                 Name: str = "Geofence_Default",
                 IsGeofenceFav: bool = False,
                 Coordinates=None):
        if Coordinates is None:
            Coordinates = [
                {
                    "Type": "polygon",
                    "Waypoints":
                        [
                            {"lat": 41.276428, "lon": 1.988215},
                            {"lat": 41.276167, "lon": 1.988333},
                            {"lat": 41.276357, "lon": 1.989130},
                            {"lat": 41.276614, "lon": 1.989012}
                        ]
                },
                {
                    "Type": "polygon",
                    "Waypoints":
                        [
                            {"lat": 41.276442, "lon": 1.988651},
                            {"lat": 41.276375, "lon": 1.988572},
                            {"lat": 41.276346, "lon": 1.988725},
                            {"lat": 41.276442, "lon": 1.988820}
                        ]
                }
            ]

        self.DroneCount = DroneCount
        self.Name = Name
        self.IsGeofenceFav = IsGeofenceFav
        self.Coordinates = Coordinates

    def GetName(self):
        return self.Name

    def PrintCoordinates(self):
        i = 0
        for Coord in self.Coordinates:
            print("Coordinate index " + str(i) + ": " + str(Coord))
            i = i + 1

