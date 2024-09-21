from pymavlink import mavutil

# Start a connection listening to a UDP port
the_connection = mavutil.mavlink_connection('tcp:127.0.0.1:5762')

# Wait for the first heartbeat
#   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" %
      (the_connection.target_system, the_connection.target_component))

frame1 = mavutil.mavlink.MAV_FRAME_LOCAL_NED # posicion respecto a home, NED
frame2 = mavutil.mavlink. MAV_FRAME_LOCAL_OFFSET_NED # desplazamiento respecto a posición del dron, NEd
frame3 = mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED # desplazamiento respecto a posición del dron, Alante, derecha, arriba
msg = the_connection.mav.command_long_encode(
    0, 0,  # Sistema y componente (0 para sistema no tripulado)
    mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,  # Comando para cambiar la velocidad de navegación
    0,  # Confirmando
    0,  # Velocidad vertical (sin cambios)
    3,  # Velocidad de navegación (m/s)
    -1,  # Velocidad máxima (-1 para no limitar)
    0, 0, 0, 0)  # Parámetros adicionales (no utilizados)

# Enviar el mensaje al dron
'''master.mav.send(msg)

msg = the_connection.mav.command_long_encode(
        0, 0,  # Sistema y componente (0 para sistema no tripulado)
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,  # Comando para cambiar la velocidad
        0,  # Confirmando
        0,  # Velocidad vertical (sin cambios)
        0,  # Velocidad hacia adelante (sin cambios)
        1,  # Velocidad hacia los lados (m/s)
        0,  # Velocidad de arrastre (sin cambios)
        0, 0, 0)  # Parámetros adicionales (no utilizados)
'''
# Enviar el mensaje al dron
the_connection.mav.send(msg)


'''the_connection.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, the_connection.target_system,
                         the_connection.target_component, frame1, int(0b110111111000), 200, 400, -10, 0, 0, 0, 0, 0, 0, 45, 0.5))
'''
'''the_connection.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, the_connection.target_system,
                         the_connection.target_component, frame3, int(0b1100111111000111), 0, 0,0, 4, 0, 0, 0, 0, 0, 45, 0.5))
'''

#the_connection.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(10, the_connection.target_system,
#                        the_connection.target_component, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, int(0b110111111000), int(-35.3629849 * 10 ** 7), int(149.1649185 * 10 ** 7), 10, 0, 0, 0, 0, 0, 0, 1.57, 0.5))


while 1:
    msg = the_connection.recv_match(
        type='HEARTBEAT', blocking=True)
    print(msg)