#!/usr/bin/env python3

import math

from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from interactive_markers.menu_handler import MenuHandler

from visualization_msgs.msg import (
    InteractiveMarker,
    InteractiveMarkerControl,
    InteractiveMarkerFeedback,
    Marker,
)


def create_target_marker(node, x, y, on_goal, on_start):

    # Create interactive marker server
    server = InteractiveMarkerServer(
        node, '/blueboat/challenge_1/interactive_marker'
    )

    # Create target marker
    marker = InteractiveMarker()
    marker.header.frame_id = 'world_ned'
    marker.name = 'challenge1_goal'
    marker.description = 'Challenge 1 target'
    marker.scale = 0.7

    marker.pose.position.x = float(x)
    marker.pose.position.y = float(y)
    marker.pose.orientation.w = 1.0

    # Create green sphere
    visual = InteractiveMarkerControl()
    visual.name = 'target'
    visual.interaction_mode = InteractiveMarkerControl.BUTTON
    visual.always_visible = True

    sphere = Marker()
    sphere.type = Marker.SPHERE
    sphere.scale.x = 0.25
    sphere.scale.y = 0.25
    sphere.scale.z = 0.25
    sphere.color.g = 1.0
    sphere.color.a = 1.0

    visual.markers.append(sphere)
    marker.controls.append(visual)

    # Add arrows to move the target
    for name, rotation in (
        ('move_x', (1.0, 0.0)),
        ('move_y', (math.sqrt(0.5), math.sqrt(0.5))),
    ):
        control = InteractiveMarkerControl()
        control.name = name
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        control.orientation.w = rotation[0]
        control.orientation.z = rotation[1]

        marker.controls.append(control)

    # Create menu
    menu = MenuHandler()
    menu.insert(
        'Start mission',
        callback=lambda feedback: on_start()
    )

    # Update target position when the marker moves
    def feedback_callback(feedback):

        if feedback.event_type == InteractiveMarkerFeedback.MOUSE_UP:
            on_goal(
                feedback.pose.position.x,
                feedback.pose.position.y
            )

    # Add marker to server
    server.insert(marker, feedback_callback=feedback_callback)

    # Add menu to marker
    menu.apply(server, marker.name)

    # Publish marker
    server.applyChanges()

    return server