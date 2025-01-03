import math
import threading
import time

from modules.message_handler import MessageHandler
from pymavlink import mavutil

''' Esta función sirve exclusivamente para detectar cuándo el dron se desarma porque 
ha pasado mucho tiempo desde que se armó sin despegar'''


def _handle_heartbeat(self, msg):
    if self.takeTelemetry:
        if msg.base_mode == 89 and self.state == 'armed':
            self.state = 'connected'
        mode = mavutil.mode_string_v10(msg)
        if not 'Mode(0x000000' in str(mode):
            self.flightMode = mode


def _record_telemetry_info(self, msg):
    if self.takeTelemetry and msg:
        msg = msg.to_dict()

        self.lat = float(msg['lat'] / 10 ** 7)
        self.lon = float(msg['lon'] / 10 ** 7)
        self.alt = float(msg['relative_alt'] / 1000)
        self.heading = float(msg['hdg'] / 100)
        if self.state == 'connected' and self.alt > 0.5:
            self.state = 'flying'
        if self.state == 'flying' and self.alt < 0.5:
            self.state = 'connected'
        vx = float(msg['vx'])
        vy = float(msg['vy'])
        self.groundSpeed = math.sqrt(vx * vx + vy * vy) / 100



def _record_local_telemetry_info(self, msg):
    if self.takeTelemetry and msg:
        self.position = [msg.x, msg.y, msg.z]

def _connect(self, connection_string, baud, callback=None, params=None):
    print("Flag 0")
    self.vehicle = mavutil.mavlink_connection(connection_string, baud)
    self.message_handler = MessageHandler(self.vehicle)
    print("Flag 0.1")
    self.message_handler.wait_for_message('HEARTBEAT', timeout=1)
    print("Flag 0.2")
    self.state = "connected"
    self.takeTelemetry = True
    print("Flag 1")


    self.message_handler.register_handler('HEARTBEAT', self._handle_heartbeat)
    self.message_handler.register_handler('GLOBAL_POSITION_INT', self._record_telemetry_info)
    self.message_handler.register_handler('LOCAL_POSITION_NED', self._record_local_telemetry_info)
    print("Flag 2")
    # Pido datos globales
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system, self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
        1e6 / self.frequency,  # frecuencia con la que queremos paquetes de telemetría
        0, 0, 0, 0,  # Unused parameters
        0
    )
    print("Flag 3")
    # Pido también datos locales
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system, self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        mavutil.mavlink.MAVLINK_MSG_ID_LOCAL_POSITION_NED,  # The MAVLink message ID
        1e6 / self.frequency,
        0, 0, 0, 0,  # Unused parameters
        0
    )
    print("Flag 4")

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
    print("Flag 5")


def connect(self,
            connection_string,
            baud,
            freq=4,
            blocking=True,
            callback=None,
            params=None):
    self.frequency = freq
    print("Connecting...")
    self._connect(connection_string, baud)
    print('ya estoy conectado')



def disconnect(self):
    print("Disconnecting...")
    self.state = "disconnected"
    if self.message_handler:
        self.message_handler.stop()
    # paramos el envío de datos de telemetría
    self.stop_sending_telemetry_info()
    self.stop_sending_local_telemetry_info()
    if hasattr(self, "vehicle"):
        self.vehicle.close()
    return True