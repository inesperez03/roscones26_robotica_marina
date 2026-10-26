#!/usr/bin/env python3

import math
import rclpy

from geometry_msgs.msg import Wrench
from sura_msgs.msg import Navigator
from controller_manager_msgs.srv import SwitchController

from challenge_1.target_marker import create_target_marker


def switch_controller(node, controller_name):
    # Connect to the controller manager
    client = node.create_client(
        SwitchController,
        '/blueboat/controller/controller_manager/switch_controller'
    )
    client.wait_for_service()

    # TODO 1: Complete the request to activate the controller.
    request = SwitchController.Request()
    # TODO 1: Set the controller(s) to activate and the strictness mode.

    # Send the request
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)


def send_force(publisher, force_x, torque_z):
    # Create a force command
    msg = Wrench()
    msg.force.x = float(force_x)
    msg.torque.z = float(torque_z)
    # Send the command
    publisher.publish(msg)


def calculate_force(distance_error, angle_error):
    # TODO 3: Calculate the forward force and yaw torque from the errors.
    # Consider proportional gains, command limits, and whether to turn
    # towards the target before advancing.
    force = 0.0
    torque = 0.0
    return force, torque


def gotopose():
    # Initialize ROS 2
    rclpy.init()
    node = rclpy.create_node('challenge1_gotopose')

    # Activate body_force controller
    switch_controller(node, 'body_force')

    # Create force publisher
    publisher = node.create_publisher(
        Wrench,
        'TODO_CONTROLLER_COMMAND_TOPIC',  # TODO 2: Set the body_force command topic.
        10
    )

    # Robot position, target and mission status
    robot = None
    target = (0.0, 0.0)
    mission_started = False

    # Get robot position
    def navigation_callback(msg):
        nonlocal robot
        robot = (
            msg.position.position.x,
            msg.position.position.y,
            msg.rpy.z
        )

    # Update target when the marker moves
    def goal_callback(x, y):
        nonlocal target
        target = (x, y)
        node.get_logger().info(f'Target: {target}')

    # Start mission from RViz
    def start_callback():
        nonlocal mission_started
        mission_started = True
        node.get_logger().info('Mission started!')

    # Subscribe to robot navigation
    node.create_subscription(
        Navigator,
        '/blueboat/navigator/navigation',
        navigation_callback,
        10
    )

    # Create interactive marker
    marker_server = create_target_marker(
        node,
        0.0, 0.0,
        goal_callback,
        start_callback
    )
    node.get_logger().info('Interactive marker created!')

    try:
        # Control loop at 10 Hz
        while rclpy.ok():
            # Update ROS 2 callbacks
            rclpy.spin_once(node, timeout_sec=0.1)

            # Wait for the mission to start
            if not mission_started or robot is None:
                send_force(publisher, 0.0, 0.0)
                continue

            x, y, yaw = robot
            target_x, target_y = target

            # Calculate distance error
            dx = target_x - x
            dy = target_y - y
            distance_error = math.hypot(dx, dy)

            # Stop when the target is reached
            if distance_error < 1.0:
                send_force(publisher, 0.0, 0.0)
                mission_started = False
                node.get_logger().info('Target reached!')
                continue

            # Calculate angle error
            desired_yaw = math.atan2(dy, dx)
            angle_error = math.atan2(
                math.sin(desired_yaw - yaw),
                math.cos(desired_yaw - yaw)
            )

            # Calculate force and torque using the controller
            force, torque = calculate_force(distance_error, angle_error)

            # Send force commands
            send_force(publisher, force, torque)

    except KeyboardInterrupt:
        pass

    finally:
        # Stop the robot if ROS 2 is still running
        if rclpy.ok():
            for _ in range(5):
                send_force(publisher, 0.0, 0.0)
                rclpy.spin_once(node, timeout_sec=0.1)

        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    gotopose()