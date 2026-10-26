import rclpy
from rclpy.node import Node


class Challenge4Node(Node):
    def __init__(self):
        super().__init__("challenge_4")


def main(args=None):
    rclpy.init(args=args)
    node = Challenge4Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
