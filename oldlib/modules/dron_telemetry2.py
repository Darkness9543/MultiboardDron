import json
import math
import threading
import time

from pymavlink import mavutil


def _prepare_telemetry_info(self):
    self.alt = 0
    self.groundSpeed = 0
    self.heading = 0
    self.sendTelemetryInfo = True
    while self.sendTelemetryInfo:
        #msg = self.vehicle.recv_match(type='AHRS2', blocking= True).to_dict()
        msg = self.vehicle.recv_match( blocking= True)
        if msg.get_type()  =='GLOBAL_POSITION_INT':
            msg = msg.to_dict()
            self.lat = float(msg['lat'] / 10 ** 7)
            self.lon = float(msg['lon'] / 10 ** 7)
            self.alt = float(msg['relative_alt']/1000)
            self.heading = float(msg['hdg'] / 100)

            vx =  float(msg['vx'])
            vy = float(msg['vy'])
            self.groundSpeed = math.sqrt( vx*vx+vy*vy)/100

        elif msg.get_type()  =='LOCAL_POSITION_NED':
            self.position = [msg.x, msg.y, msg.z]

        time.sleep(1)


def _send_telemetry_info (self,  process_telemetry_info):
    self.sendTelemetryInfo = True
    while self.sendTelemetryInfo:
        # msg = self.vehicle.recv_match(type='AHRS2', blocking= True).to_dict()

        telemetry_info = {
            'lat': self.lat,
            'lon': self.lon,
            'alt': self.alt,
            'groundSpeed': self.groundSpeed,
            'heading': self.heading,
            'state': self.state,
            'posX':  self.position[0],
            'posY':self.position[1],
            'posZ':self.position[2]
        }
        print('global ', telemetry_info)

        if self.id == None:
            process_telemetry_info(telemetry_info)
        else:
            process_telemetry_info(self.id, telemetry_info)
        time.sleep(1)



def send_telemetry_info(self, process_telemetry_info):
    prepareThread = threading.Thread(target=self._prepare_telemetry_info)
    prepareThread.start()

    telemetryThread = threading.Thread(target=self._send_telemetry_info, args=[process_telemetry_info,])
    telemetryThread.start()

def stop_sending_telemetry_info(self):
    self.sendTelemetryInfo = False