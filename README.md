# Курс «Робототехника · ROS 2»

Репозиторий практических работ по курсу робототехники (НГУ).

---

## ПР04. Параметризуем движение

### Цель работы
Параметризация параметров движения и таймера ноды `patrol` (`linear_speed`, `turn_rate`, `publish_hz`). Валидация входных значений параметров без разрушения активного состояния (отклонение некорректных значений, в том числе 0.0, отрицательных чисел, NaN и значений вне допустимых диапазонов). Динамическое изменение периода таймера (`1 / publish_hz`) с корректной остановкой и уничтожением предыдущего таймера при изменении частоты.

---

### Порядок локального воспроизведения ПР04

#### 1. Сборка пакетов
```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
```

#### 2. Запуск тестов
```bash
python3 -m pytest src/patrol/test
```

#### 3. Запуск симулятора и ноды патрулирования
```bash
export ROS_DOMAIN_ID=16

# В терминале 1: запуск симулятора
ros2 launch turtle_bringup sim.launch.py

# В терминале 2: запуск ноды patrol с переназначением топика
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

#### 4. Динамическое управление параметрами через CLI
```bash
# Получение текущего значения частоты публикации:
ros2 param get /patrol publish_hz

# Изменение частоты публикации на 5.0 Гц:
ros2 param set /patrol publish_hz 5.0

# Замер частоты топика (подтверждение изменения потока на ~5 Гц):
ros2 topic hz /turtle1/cmd_vel

# Попытка установки недопустимой частоты 0.0 (отклоняется валидатором):
ros2 param set /patrol publish_hz 0.0

# Проверка сохранения прежней частоты (5.0 Гц):
ros2 param get /patrol publish_hz
```

#### 5. Вызов сервиса очистки и инспекция actions
```bash
# Вызов сервиса очистки экрана turtlesim:
ros2 service call /clear std_srvs/srv/Empty {}

# Поиск доступных действий (actions):
ros2 action list -t
```

---

### Автоматическая проверка
```bash
python3 .course-kit/v1/tools/check_practice.py PR04 --submission .
```
