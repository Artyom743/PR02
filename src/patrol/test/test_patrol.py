import math
import pytest
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from patrol.patrol import (
    select_command,
    validate_linear_speed,
    validate_turn_rate,
    validate_publish_hz,
)


def test_select_command_without_pose():
    cmd = select_command(None)
    assert isinstance(cmd, Twist)
    assert cmd.linear.x == 0.0
    assert cmd.angular.z == 0.0


def test_select_command_uses_params():
    pose = Pose(x=5.54, y=5.54, theta=0.0,
                linear_velocity=0.0, angular_velocity=0.0)
    cmd = select_command(pose, linear_speed=0.7, turn_rate=-0.4)
    assert cmd.linear.x == pytest.approx(0.7)
    assert cmd.angular.z == pytest.approx(-0.4)


# --- publish_hz ---

@pytest.mark.parametrize('hz', [1.0, 5.0, 10.0, 30.0])
def test_publish_hz_valid(hz):
    assert validate_publish_hz(hz) is True


@pytest.mark.parametrize('hz', [0.0, -1.0, 0.5, 31.0, float('nan'), float('inf')])
def test_publish_hz_invalid(hz):
    assert validate_publish_hz(hz) is False


def test_publish_hz_change_10_to_5():
    """10 → 5 Гц допустимо."""
    assert validate_publish_hz(10.0)
    assert validate_publish_hz(5.0)


def test_publish_hz_zero_rejected():
    """Ноль — воспроизводимый отказ."""
    assert validate_publish_hz(0.0) is False


def test_publish_hz_negative_rejected():
    assert validate_publish_hz(-3.0) is False


def test_publish_hz_nan_rejected():
    assert validate_publish_hz(float('nan')) is False


# --- linear_speed / turn_rate ---

@pytest.mark.parametrize('v', [0.0, 0.5, 1.0])
def test_linear_speed_valid(v):
    assert validate_linear_speed(v) is True


@pytest.mark.parametrize('v', [-0.1, 1.1, float('nan')])
def test_linear_speed_invalid(v):
    assert validate_linear_speed(v) is False


@pytest.mark.parametrize('w', [-1.0, 0.0, 0.3, 1.0])
def test_turn_rate_valid(w):
    assert validate_turn_rate(w) is True


@pytest.mark.parametrize('w', [-1.1, 1.1, float('nan')])
def test_turn_rate_invalid(w):
    assert validate_turn_rate(w) is False