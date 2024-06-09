import threading
import time

import paho.mqtt.client as mqtt
import json
from modules.Dron import Dron


def publish_telemetry_info(telemetry_info):
    global sending_topic, client
    client.publish(sending_topic + '/telemetryInfo', json.dumps(telemetry_info))


def publish_parameters(parameters):
    global sending_topic, client
    print('los publico en ' + sending_topic + '/parameters')

    client.publish(sending_topic + '/parameters', json.dumps(parameters))


def publish_event(event):
    global sending_topic, client
    client.publish(sending_topic + '/' + event)
    print('he publicado: ', sending_topic + '/' + event)


def on_message(cli, userdata, message):
    global sending_topic, client
    global dron

    splited = message.topic.split("/")
    origin = splited[0]  # aqui tengo el nombre de la aplicación que origina la petición
    command = splited[2]  # aqui tengo el comando

    sending_topic = "autopilotService1/" + origin  # lo necesitaré para enviar las respuestas
    print (f" Recieved command '{command}'")

    print(f"Drone state '{dron.state}'")

    if command == 'connect':
        print('vamos a conectar')
        connection_string = 'tcp:127.0.0.1:5763'
        baud = 115200
        dron.connect(connection_string, baud)
        dron.state = "conectado"
        publish_event('connected')

    if command == 'startTelemetry':
        dron.send_telemetry_info(publish_telemetry_info)

    if command == 'stopTelemetry':
        dron.stop_sending_telemetry_info()

    if command == 'getParameters':
        print('pido parametros')
        if dron.state == 'conectado':
            dron.getParams(message.payload, blocking=False,
                           callback=publish_parameters)  # tiene que enviar una respuesta

    if command == 'setParameters':
        if dron.state == 'conectado':
            dron.setParams(message.payload)

    if command == 'arm':
        if dron.state == 'conectado':
            dron.arm()
            publish_event('armed')

    if command == 'takeOff':
        if dron.state == 'armed':  ## CHECK TYPO IT WAS ARMADO HACER CONVENCION
            print('voy a despegar')
            dron.takeOff(5, blocking=False, callback=publish_event, params='flying')
            print(" ya he ordenado despegar")

    if command == 'RTL':
        if dron.state == 'flying':  # PONIA VOLANDO PERO ERA volando
            dron.RTL()

    if command == 'Land':
        if dron.state == 'flying':
            dron.Land(blocking=False, callback=publish_event, params='landed')

    if command == 'startGo':
        if dron.state == 'flying':
            dron.startGo()

    if command == 'stopGo':
        if dron.state == 'flying':
            dron.stopGo()

    if command == 'go':
        if dron.state == ('flyingç'
                          ''):
            direction = message.payload.decode("utf-8")
            dron.go(direction)


def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        print("connected OK Returned code=", rc)
        connected = True
    else:
        print("Bad connection Returned code=", rc)


broker_address = "broker.hivemq.com"
broker_port = 1883

client = mqtt.Client("autopilotService1")
dron = Dron()
client.on_message = on_message
client.on_connect = on_connect

client.connect(broker_address, broker_port)
client.subscribe('+/autopilotService1/#')
print('autopilotService1 esperando peticiones')
client.loop_forever()
