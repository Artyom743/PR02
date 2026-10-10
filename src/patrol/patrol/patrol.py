import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


# --- Границы допустимых значений ---
LINEAR_SPEED_RANGE = (0.0, 1.0)
TURN_RATE_RANGE = (-1.0, 1.0)
PUBLISH_HZ_RANGE = (1.0, 30.0)


def _is_finite_number(value) -> bool:
    """Проверка: число, не bool, конечное (не NaN, не inf)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


def validate_linear_speed(value) -> bool:
    return _is_finite_number(value) and LINEAR_SPEED_RANGE[0] <= value <= LINEAR_SPEED_RANGE[1]


def validate_turn_rate(value) -> bool:
    return _is_finite_number(value) and TURN_RATE_RANGE[0] <= value <= TURN_RATE_RANGE[1]


def validate_publish_hz(value) -> bool:
    """Ключевая проверка: 0, отрицательные, NaN и inf отклоняются."""
    if not _is_finite_number(value):
        return False
    return PUBLISH_HZ_RANGE[0] <= value <= PUBLISH_HZ_RANGE[1]


def select_command(pose: Pose | None,
                   linear_speed: float = 0.5,
                   turn_rate: float = 0.3) -> Twist:
    """Чистая функция: по позе и параметрам собрать Twist."""
    cmd = Twist()
    if pose is None:
        return cmd
    cmd.linear.x = float(linear_speed)
    cmd.angular.z = float(turn_rate)
    return cmd


class Patrol(Node):
    def __init__(self):
        super().__init__('patrol')

        # --- Объявление параметров со значениями по умолчанию ---
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)
        self.declare_parameter('publish_hz', 10.0)

        self.linear_speed = self.get_parameter('linear_speed').value
        self.turn_rate = self.get_parameter('turn_rate').value
        self.publish_hz = self.get_parameter('publish_hz').value

        # --- Подписка и издатель ---
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)
        self.last_pose: Pose | None = None

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # --- Таймер ---
        self.timer = None
        self._create_timer(self.publish_hz)

        # --- Колбэк на изменение параметров ---
        self.add_on_set_parameters_callback(self.parameters_callback)

    def _create_timer(self, hz: float):
        """Останавливает старый таймер и создаёт новый с периодом 1/hz."""
        if self.timer is not None:
            self.timer.cancel()
            self.destroy_timer(self.timer)
            self.timer = None
        period = 1.0 / hz
        self.timer = self.create_timer(period, self.timer_callback)

    def parameters_callback(self, params):
        """Валидация ДО применения. Возвращает SetParametersResult."""
        from rcl_interfaces.msg import SetParametersResult

        for p in params:
            if p.name == 'linear_speed' and not validate_linear_speed(p.value):
                return SetParametersResult(
                    successful=False,
                    reason=f'linear_speed must be in {LINEAR_SPEED_RANGE}, got {p.value}')
            if p.name == 'turn_rate' and not validate_turn_rate(p.value):
                return SetParametersResult(
                    successful=False,
                    reason=f'turn_rate must be in {TURN_RATE_RANGE}, got {p.value}')
            if p.name == 'publish_hz' and not validate_publish_hz(p.value):
                return SetParametersResult(
                    successful=False,
                    reason=f'publish_hz must be in {PUBLISH_HZ_RANGE}, got {p.value}')

        # Все значения валидны — применяем
        for p in params:
            if p.name == 'linear_speed':
                self.linear_speed = float(p.value)
            elif p.name == 'turn_rate':
                self.turn_rate = float(p.value)
            elif p.name == 'publish_hz':
                new_hz = float(p.value)
                if new_hz != self.publish_hz:
                    self.publish_hz = new_hz
                    self._create_timer(new_hz)

        return SetParametersResult(successful=True)

    def pose_callback(self, msg: Pose):
        self.last_pose = msg

    def timer_callback(self):
        cmd = select_command(self.last_pose, self.linear_speed, self.turn_rate)
        self.publisher.publish(cmd)
        self.get_logger().info(
            f'cmd: linear.x={cmd.linear.x}, angular.z={cmd.angular.z}')


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