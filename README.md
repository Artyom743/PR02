# Курс «Робототехника · ROS 2»

Репозиторий практических работ по курсу робототехники (НГУ).

## ПР02. Терминал, пакет и запуск turtlesim

**Цель работы**

Создание и сборка ament-пакета `turtle_bringup`, написание launch-файла `sim.launch.py` для автоматического развёртывания узлов, исследование доставки управляющих сообщений через CLI и воспроизведение дефекта несовпадения имени топика (`/cmd_vel` vs `/turtle1/cmd_vel`).

### Порядок локального воспроизведения ПР02

#### 1. Сборка пакета

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup
source install/setup.bash
```
#### 2. Запуск симулятора через launch

```bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```

#### 3. Управление движением через CLI

```bash
# Получение начальной позы:
ros2 topic echo /turtle1/pose --once

# Отправка команды движения (линейная скорость 1.0, угловая 0.5):
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'

# Проверка изменившейся позы:
ros2 topic echo /turtle1/pose --once
```

#### 4. Воспроизведение дефекта неверного имени топика

```bash
# Публикация в /cmd_vel (у симулятора подписчик на /turtle1/cmd_vel):
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'

# Проверка конечных точек топиков:
ros2 topic info /cmd_vel --verbose          # Subscription count: 0
ros2 topic info /turtle1/cmd_vel --verbose  # Subscription count: 1 (/turtlesim)
```

#### 5. Восстановление доставки

Отправка в корректный топик `/turtle1/cmd_vel` восстанавливает движение черепахи.

### Автоматическая проверка

```bash
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```
