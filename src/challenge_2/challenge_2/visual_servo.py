#!/usr/bin/env python3

import time
import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from sura_msgs.msg import SuraWrenchCommand
from controller_manager_msgs.srv import SwitchController
from rclpy.qos import qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions


# Datos del marcador ArUco
camera_matrix = None
distortion = None
aruco = None
last_detection = 0.0

bridge = CvBridge()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)


def switch_controller(node, controller_name):
    # Conectar con el gestor de controladores
    client = node.create_client(
        SwitchController,
        '/bluerov/controller/controller_manager/switch_controller'
    )
    client.wait_for_service()

    # TODO 1: Completar la solicitud de activación (controladores y modo de ejecución).
    request = SwitchController.Request()
    # TODO: indicar qué controlador se quiere activar
    # TODO: indicar el modo de ejecución de la solicitud

    # Enviar la solicitud
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    node.get_logger().info(f'{controller_name}: activación solicitada')


def send_force(publisher, force_x, force_y, force_z, torque_z):
    # Crear el comando para el árbitro
    msg = SuraWrenchCommand()
    msg.requester = 'pbvs'
    msg.controller = 'depth_hold'
    msg.priority = 90

    # Asignar las fuerzas y el par
    msg.wrench.force.x = float(force_x)
    msg.wrench.force.y = float(force_y)
    msg.wrench.force.z = float(force_z)
    msg.wrench.torque.z = float(torque_z)

    publisher.publish(msg)


def calculate_force(distance_error, horizontal_error, vertical_error, yaw_error):
    # TODO 4: Diseñar una estrategia de control propia para reducir los errores de pose.
    # Tener en cuenta el sentido de los ejes y los límites de las órdenes (ver README).
    # Devolver: force_x, force_y, force_z, torque_z
    raise NotImplementedError('TODO 4: calcular fuerzas y par')


def camera_info_callback(msg):
    global camera_matrix, distortion

    # Obtener los parámetros de calibración de la cámara
    camera_matrix = np.array(msg.k).reshape(3, 3)
    distortion = np.array(msg.d)


def image_callback(msg):
    global aruco, last_detection

    if camera_matrix is None:
        return

    # Convertir la imagen de ROS a OpenCV
    image = bridge.imgmsg_to_cv2(msg, 'bgr8')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detectar marcadores ArUco
    corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)

    if ids is None:
        return

    # Buscar únicamente el marcador ArUco de ID 0
    for i, marker_id in enumerate(ids.flatten()):
        if marker_id != 0:
            continue

        # Estimar la pose 6D (tamaño del marcador: 0,5 m)
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            [corners[i]], 0.5, camera_matrix, distortion
        )

        # Obtener la posición 3D
        x, y, z = tvecs[0][0]

        # Obtener la orientación del marcador
        rotation, _ = cv2.Rodrigues(rvecs[0][0])
        normal = rotation[:, 2]

        # Calcular el error de orientación
        yaw_error = np.arctan2(normal[0], -normal[2])

        # Guardar la pose del ArUco
        if z > 0:
            aruco = (float(x), float(y), float(z), float(yaw_error))
            last_detection = time.monotonic()

        return


def visual_servoing():
    # Inicializar ROS 2
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = rclpy.create_node('challenge2_visual_servoing')

    # Activar los controladores
    switch_controller(node, 'body_force')
    switch_controller(node, 'depth_hold')

    # TODO 2: Completar el tópico de comandos del árbitro (ver README).
    publisher = node.create_publisher(
        SuraWrenchCommand,
        'TODO_ARBITRATOR_WRENCH_TOPIC',
        10
    )

    # Suscribirse a la calibración de la cámara
    node.create_subscription(
        CameraInfo,
        '/bluerov/stonefish/front_camera/camera_info',
        camera_info_callback,
        qos_profile_sensor_data
    )

    # Suscribirse a las imágenes de la cámara
    node.create_subscription(
        Image,
        '/bluerov/front_camera/camera/image_raw',
        image_callback,
        qos_profile_sensor_data
    )

    node.get_logger().info('Esperando al marcador ArUco de ID 0...')

    goal_reached = False
    aruco_lost = False

    try:
        # Bucle de control
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)

            # Esperar a que se detecte el ArUco
            if aruco is None or time.monotonic() - last_detection > 0.5:
                if not aruco_lost and last_detection > 0:
                    node.get_logger().warn('¡Se ha perdido el ArUco!')
                    aruco_lost = True
                continue

            # Avisar cuando vuelva a detectarse el ArUco
            if aruco_lost:
                node.get_logger().info('¡ArUco detectado de nuevo!')
                aruco_lost = False

            aruco_x, aruco_y, aruco_z, aruco_yaw = aruco

            # TODO 3: Calcular los errores respecto a la pose deseada del ArUco.
            # Definir distance_error, horizontal_error, vertical_error y yaw_error.
            # Consultar la pose objetivo y el sentido de los ejes en el README.
            raise NotImplementedError('TODO 3: calcular los errores de pose')

            # Detenerse cuando se alcance el objetivo
            if (abs(distance_error) < 1.5 and
                abs(horizontal_error) < 0.25 and
                abs(vertical_error) < 0.25 and
                abs(yaw_error) < 0.15):

                if not goal_reached:
                    node.get_logger().info('¡Objetivo alcanzado!')
                    goal_reached = True

                send_force(publisher, 0.0, 0.0, 0.0, 0.0)
                continue

            goal_reached = False

            # Calcular las fuerzas y el par
            force_x, force_y, force_z, torque_z = calculate_force(
                distance_error, horizontal_error, vertical_error, yaw_error
            )

            # Enviar los comandos al árbitro
            send_force(publisher, force_x, force_y, force_z, torque_z)

            # Mostrar los errores y las fuerzas
            print(
                f'Errores: {distance_error:.2f}, {horizontal_error:.2f}, '
                f'{vertical_error:.2f}, {yaw_error:.2f} | '
                f'Fuerzas: {force_x:.1f}, {force_y:.1f}, '
                f'{force_z:.1f}, {torque_z:.1f}',
                flush=True
            )

    except KeyboardInterrupt:
        pass
    finally:
        # Detener el robot
        if rclpy.ok():
            for _ in range(5):
                send_force(publisher, 0.0, 0.0, 0.0, 0.0)
                rclpy.spin_once(node, timeout_sec=0.1)

        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    visual_servoing()