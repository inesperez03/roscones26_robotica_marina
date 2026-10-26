#!/usr/bin/env python3

import math
import time
import rclpy
from sura_msgs.msg import Navigator, SuraWrenchCommand
from controller_manager_msgs.srv import SwitchController
from rclpy.signals import SignalHandlerOptions


# Posiciones de los robots y marcas de tiempo de sus últimas medidas
blueboat = None
bluerov = None
blueboat_time = 0.0
bluerov_time = 0.0


def switch_controller(node, controller_name):
    # Conectar con el gestor de controladores del BlueROV
    client = node.create_client(
        SwitchController,
        '/bluerov/controller/controller_manager/switch_controller'
    )
    client.wait_for_service()

    # TODO 1: Completar la petición para activar el controlador indicado.
    request = SwitchController.Request()
    # TODO: añadir controller_name a la lista de controladores que se activarán
    # TODO: elegir el modo de ejecución (ver README)

    # Enviar la petición
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    node.get_logger().info(f'{controller_name}: activación solicitada')


def send_force(publisher, force_x, force_y, force_z, torque_z):
    # Crear un comando destinado al árbitro de SURA
    msg = SuraWrenchCommand()
    msg.requester = 'surface_following'
    msg.controller = 'depth_hold'
    msg.priority = 90

    # Asignar fuerzas y par
    msg.wrench.force.x = float(force_x)
    msg.wrench.force.y = float(force_y)
    msg.wrench.force.z = float(force_z)
    msg.wrench.torque.z = float(torque_z)

    publisher.publish(msg)


def calculate_force(error_x, error_y, depth_error, yaw_error, yaw):
    # TODO 3: Diseñar el control del BlueROV para seguir al BlueBoat.
    # Los errores X/Y están expresados en el mundo; las fuerzas X/Y, en el robot.
    # Puedes utilizar la estrategia de control que prefieras (ver README).
    # Devolver: force_x, force_y, force_z, torque_z.
    raise NotImplementedError('TODO 3: calcular fuerzas y par')


def blueboat_callback(msg):
    global blueboat, blueboat_time

    # Posición y orientación del robot de superficie
    blueboat = (
        msg.position.position.x,
        msg.position.position.y,
        msg.rpy.z
    )
    blueboat_time = time.monotonic()


def bluerov_callback(msg):
    global bluerov, bluerov_time

    # Posición, profundidad y orientación del robot submarino
    bluerov = (
        msg.position.position.x,
        msg.position.position.y,
        msg.position.position.z,
        msg.rpy.z
    )
    bluerov_time = time.monotonic()


def surface_following():
    # Inicializar ROS 2
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = rclpy.create_node('challenge3_surface_following')

    # Activar los controladores
    switch_controller(node, 'body_force')
    switch_controller(node, 'depth_hold')

    # TODO 2: Completar el tópico del árbitro de SURA para el BlueROV.
    publisher = node.create_publisher(
        SuraWrenchCommand,
        'TODO_ARBITRATOR_WRENCH_TOPIC',
        10
    )

    # Recibir la navegación del BlueBoat
    node.create_subscription(
        Navigator,
        '/blueboat/navigator/navigation',
        blueboat_callback,
        10
    )

    # Recibir la navegación del BlueROV
    node.create_subscription(
        Navigator,
        '/bluerov/navigator/navigation',
        bluerov_callback,
        10
    )

    node.get_logger().info('Esperando datos de navegación de los dos robots...')
    last_log = 0.0

    try:
        # Bucle de control
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)
            now = time.monotonic()

            # Esperar a recibir medidas recientes de ambos robots
            if blueboat is None or bluerov is None:
                continue

            if now - blueboat_time > 1.0 or now - bluerov_time > 1.0:
                continue

            boat_x, boat_y, boat_yaw = blueboat
            rov_x, rov_y, rov_z, rov_yaw = bluerov

            # Errores de posición en el sistema de referencia global
            error_x = boat_x - rov_x
            error_y = boat_y - rov_y
            distance_error = math.hypot(error_x, error_y)

            # Error de profundidad (referencia del escenario: z = 3,0)
            depth_error = 3.0 - rov_z

            # Diferencia de orientación normalizada al intervalo [-pi, pi]
            yaw_error = math.atan2(
                math.sin(boat_yaw - rov_yaw),
                math.cos(boat_yaw - rov_yaw)
            )

            # Calcular fuerzas y par mediante el control diseñado
            force_x, force_y, force_z, torque_z = calculate_force(
                error_x, error_y, depth_error, yaw_error, rov_yaw
            )

            # Alcanzar primero la profundidad objetivo
            if abs(depth_error) > 0.5:
                force_x = 0.0
                force_y = 0.0

            # Enviar comandos al árbitro
            send_force(publisher, force_x, force_y, force_z, torque_z)

            # Mostrar el estado del seguimiento
            if now - last_log > 2.0:
                node.get_logger().info(
                    f'Distancia: {distance_error:.2f} m | '
                    f'Profundidad: {rov_z:.2f} m | '
                    f'Error de orientación: {math.degrees(yaw_error):.1f} grados'
                )
                last_log = now

    except KeyboardInterrupt:
        pass
    finally:
        # Enviar órdenes nulas al detener el programa
        if rclpy.ok():
            for _ in range(5):
                send_force(publisher, 0.0, 0.0, 0.0, 0.0)
                rclpy.spin_once(node, timeout_sec=0.05)

        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    surface_following()