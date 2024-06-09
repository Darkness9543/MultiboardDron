class Geofence:

    def __init__(self,
                 DroneCount: int = 2,
                 Name: str = "GeofenceName",
                 IsGeofenceFav: bool = False,
                 Coordinates=None,
                 Points=None):
        if Coordinates is None:
            Coordinates = [
                {"lat": 1, "lon": 1},
                {"lat": 10, "lon": 10},
                {"lat": 1, "lon": 10},
                {"lat": 10, "lon": 1}
            ]
        if Points is None:
            Points = [
                [
                    {"x": 1, "y": 1},
                    {"x": 10, "y": 1},
                    {"x": 10, "y": 10},
                    {"x": 1, "y": 10},
                    {"x": 1, "y": 1}
                ],
                [
                    {"x": 20, "y": 1},
                    {"x": 30, "y": 1},
                    {"x": 30, "y": 10},
                    {"x": 20, "y": 10},
                    {"x": 20, "y": 1}
                ]
            ]
        self.DroneCount = DroneCount
        self.Name = Name
        self.IsGeofenceFav = IsGeofenceFav
        self.Coordinates = Coordinates
        self.Points = Points

    def GetName(self):
        return self.Name

    def PrintCoordinates(self):
        i = 0
        for Coord in self.Coordinates:
            print("Coordinate index " + str(i) + ": " + str(Coord))
            i = i + 1

    def PrintPoints(self):
        i = 0
        for Point in self.Points:
            print("Point index " + str(i) + ": " + str(Point))
            i = i + 1

    def __eq__(self, other):
        if not isinstance(other, Geofence):
            return NotImplemented
        return (self.DroneCount == other.DroneCount and
                self.Name == other.Name and
                self.IsGeofenceFav == other.IsGeofenceFav and
                self.Coordinates == other.Coordinates and
                self.Points == other.Points)

    def __hash__(self):
        points_hashable = tuple(tuple(frozenset(point.items()) for point in sublist) for sublist in self.Points)
        coordinates_hashable = tuple(frozenset(coord.items()) for coord in self.Coordinates)
        return hash((self.DroneCount, self.Name, self.IsGeofenceFav, coordinates_hashable, points_hashable))
