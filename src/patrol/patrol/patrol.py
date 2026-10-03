import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose 


def select_command(pose: Pose | None) -> Twist:
    """Чистая функция: по последней позе выбрать команду Twist.

    Если позы ещё нет — нулевая команда.
    Иначе — linear.x=0.5, angular.z=0.3.
    """
    cmd = Twist()
    if pose is None:
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
    else:
        cmd.linear.x = 0.5
        cmd.angular.z = 0.3
    return cmd


class Patrol(Node):
    def __init__(self):
        super().__init__('patrol')

        # Подписка хранится как поле объекта
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
        )
        self.last_pose: Pose | None = None

        # Издатель в относительный cmd_vel
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # Таймер 0.1 с
        self.timer = self.create_timer(0.1, self.timer_callback)

    def pose_callback(self, msg: Pose):
        # Callback только сохраняет последнее сообщение
        self.last_pose = msg

    def timer_callback(self):
        cmd = select_command(self.last_pose)
        self.publisher.publish(cmd)
        self.get_logger().info(
            f'cmd: linear.x={cmd.linear.x}, angular.z={cmd.angular.z}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()