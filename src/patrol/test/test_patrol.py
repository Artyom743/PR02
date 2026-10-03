from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from patrol.patrol import select_command


def test_compute_cmd_vel_without_pose():
    """Без полученной позы нода должна выдавать нулевую команду."""
    comd = select_command(None)
    assert isinstance(comd, Twist)
    assert comd.linear.x == 0.0
    assert comd.linear.y == 0.0
    assert comd.linear.z == 0.0
    assert comd.angular.x == 0.0
    assert comd.angular.y == 0.0
    assert comd.angular.z == 0.0


def test_compute_cmd_vel_with_pose():
    """Нода должна выдавать linear.x=0.5 и angular.z=0.3."""
    pose = Pose(x=5.54, y=5.54, theta=0.0, linear_velocity=0.0, angular_velocity=0.0)
    comd = select_command(pose)
    assert isinstance(comd, Twist)
    assert comd.linear.x == 0.5
    assert comd.linear.y == 0.0
    assert comd.linear.z == 0.0
    assert comd.angular.x == 0.0
    assert comd.angular.y == 0.0
    assert comd.angular.z == 0.3