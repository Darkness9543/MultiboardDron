'''from dronekit import connect

vehicle = connect('tcp:127.0.0.1:5763', wait_ready=False, baud=115200)
vehicle.wait_ready(True, timeout=50000)
metersNorth = vehicle.location.local_frame.north # used for the y position
metersEast = vehicle.location.local_frame.east # used for the x position
altitude = vehicle.location.local_frame.down # used for the z position
print (metersNorth)'''


from pymavlink import mavutil

# Conectarse al vehículo (por ejemplo, utilizando la conexión MAVProxy)
master = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
# Configurar el filtro para recibir solo mensajes de tipo LOCAL_POSITION_NED
master.mav.request_data_stream_send(
    master.target_system,    # ID del sistema del objetivo
    master.target_component, # ID del componente del objetivo
    mavutil.mavlink.MAV_DATA_STREAM_POSITION, # Tipo de flujo de datos
    100,                     # Frecuencia de actualización (Hz)
    1                        # Habilitar (1) o deshabilitar (0) el flujo de datos
)
# poner a 0 los dos parametros anteriores para desabilitar ese flujo de datos
# Esperar por mensajes
while True:
    msg = master.recv_match(type='LOCAL_POSITION_NED', blocking=True)
    north = msg.y  # Posición al norte en metros (posición Y)
    east = msg.x   # Posición al este en metros (posición X)
    down = -msg.z  # Posición hacia abajo en metros (posición Z)
    print("Posiciones: ", north, east, down)