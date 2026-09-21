# PR02. Типы сообщений и поля

Дистрибутив: ROS 2 Jazzy, `ROS_DOMAIN_ID=16`.

## Два основных топика

| Топик | Тип сообщения | Назначение |
|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Команды движения черепахе: turtlesim **подписан** на этот топик |
| `/turtle1/pose` | `turtlesim/msg/Pose` | Текущая поза черепахи: turtlesim **публикует** в этот топик |

Проверка типов выполнена командами:
```bash
ros2 topic type /turtle1/pose
# turtlesim/msg/Pose

ros2 interface show geometry_msgs/msg/Twist
# Vector3 linear, Vector3 angular
```

## Назначение полей Twist

`geometry_msgs/msg/Twist` описывает скорость в свободном пространстве,
разложенную на линейную и угловую части:

```
Vector3 linear
    float64 x
    float64 y
    float64 z
Vector3 angular
    float64 x
    float64 y
    float64 z
```

| Поле | Назначение | Используется в turtlesim? |
|---|---|---|
| `linear.x` | Линейная скорость вперёд/назад (м/с) | **Да** — вперёд/назад |
| `linear.y` | Линейная скорость влево/вправо (м/с) | Нет |
| `linear.z` | Линейная скорость вверх/вниз (м/с) | Нет |
| `angular.x` | Угловая скорость вокруг оси X (рад/с) | Нет |
| `angular.y` | Угловая скорость вокруг оси Y (рад/с) | Нет |
| `angular.z` | Угловая скорость вокруг оси Z (рад/с) | **Да** — поворот |

В работе использовались:
- `linear.x = 1.0` — ехать вперёд,
- `angular.z = 0.5` — поворачивать против часовой стрелки.

Знак `angular.z`:
- `> 0` — поворот против часовой стрелки,
- `< 0` — по часовой стрелке,
- `= 0` — движение по прямой.

## Поля Pose

Сообщение `turtlesim/msg/Pose`, которое публикует turtlesim:

```
float32 x
float32 y
float32 theta
float32 linear_velocity
float32 angular_velocity
```

| Поле | Назначение |
|---|---|
| `x`, `y` | Координаты черепахи в поле turtlesim |
| `theta` | Ориентация (рад), 0 — вдоль оси X |
| `linear_velocity` | Текущая линейная скорость |
| `angular_velocity` | Текущая угловая скорость |

