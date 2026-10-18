import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from turtlesim.msg import Pose  # на Lyrical может быть turtlesim_msgs.msg


class PoseRelay(Node):
    def __init__(self):
        super().__init__('pose_relay')

        # Best effort publisher — сенсорный поток
        sensor_qos = QoSProfile(
            depth=10,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.BEST_EFFORT,
        )
        self.pub = self.create_publisher(Pose, 'sensor_pose', sensor_qos)

        # Подписка на turtlesim тоже best effort (сенсорные данные)
        self.sub = self.create_subscription(
            Pose, '/turtle1/pose', self.callback, sensor_qos
        )

    def callback(self, msg: Pose):
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PoseRelay()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()