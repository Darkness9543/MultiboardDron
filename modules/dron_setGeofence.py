import json
import threading

import pymavlink
from pymavlink.mavutil import default_native
import pymavlink.dialects.v20.all as dialect
from pymavlink import mavutil
import time



def _setGEOFence(self, fence_waypoints, callback=None, params = None):
    fence_list = json.loads(fence_waypoints)

    # el primer wp lo envio primero para que haga de FENCE_RETURN_POINT
    message = dialect.MAVLink_fence_point_message(target_system=self.vehicle.target_system,
                                                  target_component=self.vehicle.target_component,
                                                  idx=0, count=len(fence_list)+1, lat=fence_list[0]['lat'],
                                                  lng=fence_list[0]['lon'])
    self.vehicle.mav.send(message)
    idx = 0
    while idx < len(fence_list):
        message = dialect.MAVLink_fence_point_message(target_system=self.vehicle.target_system,
                                                      target_component=self.vehicle.target_component,
                                                      idx=idx, count=len(fence_list)+1, lat=fence_list[idx]['lat'],
                                                      lng=fence_list[idx]['lon'])
        self.vehicle.mav.send(message)

    if callback != None:
        if self.id == None:
            if params == None:
                callback()
            else:
                callback(params)
        else:
            if params == None:
                callback(self.id)
            else:
                callback(self.id, params)


def setGEOFence(self, fence_waypoints, blocking=True, callback=None, params = None):
    if blocking:
        self._setGEOFence(fence_waypoints)
    else:
        setGEOFenceThread= threading.Thread(target=self._setGEOFence, args=[fence_waypoints, callback, params])
        setGEOFenceThread.start()

