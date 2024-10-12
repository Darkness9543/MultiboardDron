import threading
import time

import paho.mqtt.client as mqtt
import json
from Dron import Dron


class AutopilotService:
    def __init__(self,
                 port: str = "",
                 autopilotNumber: int= 1):
        self.port = port
        self.autopilotNumber = autopilotNumber

        self._stop_event = threading.Event()

        broker_address = "broker.hivemq.com"
        broker_port = 1883

        self.client = mqtt.Client(str("autopilotService" + str(self.autopilotNumber)))
        self.dron = Dron()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

        self.client.connect(broker_address, broker_port)
        self.client.subscribe(str("+/autopilotService" + str(self.autopilotNumber)+ "/#"))
        print('autopilotService esperando peticiones')
        print('autopilot, puerto selectionado ' + self.port)
        print('autopilot, numero ' + str(self.autopilotNumber))

    def publish_telemetry_info(self, telemetry_info):
        self.client.publish(self.sending_topic + '/telemetryInfo', json.dumps(telemetry_info))

    def publish_parameters(self, parameters):
        print('los publico en ' + self.sending_topic + '/parameters')

        self.client.publish(self.sending_topic + '/parameters', json.dumps(parameters))

    def publish_event(self, event):
        self.client.publish(self.sending_topic + '/' + event)
        print('he publicado: ', self.sending_topic + '/' + event)

    def on_message(self, cli, userdata, message):

        splited = message.topic.split("/")
        origin = splited[0]  # aqui tengo el nombre de la aplicación que origina la petición
        command = splited[2]  # aqui tengo el comando

        self.sending_topic = str("autopilotService" + str(self.autopilotNumber)+ "/") + origin  # lo necesitaré para enviar las respuestas
        print(f" Autopilot: Recieved command '{command}'")

        if command == 'connect':
            print('vamos a conectar')
            # connection_string = 'tcp:127.0.0.1:5763'
            connection_string = self.port
            print("Port: " + self.port)
            baud = 115200
            self.dron.connect(connection_string, baud, freq=10)
            self.dron.state = "connected"
            self.publish_event('connected')

        if command == 'startTelemetry':
            self.dron.send_telemetry_info(self.publish_telemetry_info)

        if command == 'stopTelemetry':
            self.dron.stop_sending_telemetry_info()

        if command == 'getParameters':
            print('pido parametros')
            if self.dron.state == 'connected':
                self.dron.getParams(json.loads(message.payload.decode('utf-8')), blocking=False,
                                    callback=self.publish_parameters)  # tiene que enviar una respuesta

        if command == 'setParameters':
            if self.dron.state == 'connected':
                self.dron.setParams(json.loads(message.payload.decode('utf-8')))
        if command == 'setGeofence':
            print("Set geofence petition received...")
            if self.dron.state == 'connected':
                print("Continuing with setgeofence")
                self.dron.setScenario(json.loads(message.payload.decode('utf-8')))
                print(f"Geofence set done for autopilot {self.autopilotNumber}")
                self.publish_event('geofenceSet')
        if command == 'arm':
            if self.dron.state == 'connected':
                print("armando")
                self.dron.arm(blocking=False)
                self.publish_event('armed')

        if command == 'takeOff':
            if self.dron.state == 'armed':  ## CHECK TYPO IT WAS ARMADO HACER CONVENCION
                print('voy a despegar')
                self.dron.takeOff(5, blocking=False, callback=self.publish_event, params='flying')
                print(" ya he ordenado despegar")

        if command == 'RTL':
            if self.dron.state == 'flying':  # PONIA VOLANDO PERO ERA volando
                self.dron.RTL(blocking=False)

        if command == 'Land':
            if self.dron.state == 'flying':
                self.dron.Land(blocking=False, callback=self.publish_event, params='landed')

        if command == 'move':
            direction = message.payload.decode("utf-8")
            self.dron.go(direction)

        if command == 'move_to':
            pass

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK Returned code=", rc)
            self.connected = True
        else:
            print("Bad connection Returned code=", rc)

    def run(self):
        self.client.loop_start()

        try:
            while not self._stop_event.is_set():
                # Perform any periodic tasks here if necessary
                time.sleep(0.1)  # Sleep briefly to reduce CPU usage
        finally:
            self.dron.disconnect()
            self.client.loop_stop()
            self.client.disconnect()
            print(f"AutopilotService {self.autopilotNumber} has been stopped.")

    def stop(self):
        """Signal the thread to stop."""
        self._stop_event.set()



