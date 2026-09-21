# ПР02  
  
## Три команды Linux  
  
### pwd  
**Назначение:** Проверить расположение репозитория  
**Результат:** /home/art/ros2-pr01/PR02  
  
### ls -a  
**Назначение:** Показать содержимое каталога, включая скрытые файлы  
**Результат:** '.', '.course-kit', '.gitignore', 'README.md', 'src', '..', 'evidence', 'install',        'robotics-course-kit-v1.tar.gz', 'build', '.git', 'log', 'robotics-course-kit-v1.tar.gz.sha256.txt'  
  
### printenv ROS_DISTRO ROS_DOMAIN_ID  
**Назначение:** Прочитать переменные окружения  
**Результат:** `ROS_DISTRO=jazzy`, `ROS_DOMAIN_ID=16`  

## Чем > отличается от |  
**>** — это перенаправление потока в файл. cmd > file.txt пишет stdout команды в файл, заменяя его содержимое. Работает с файловой системой.

**|** — это конвейер между процессами. cmd1 | cmd2 передаёт stdout команды cmd1 на stdin команды cmd2. Файл не создаётся, данные идут напрямую.  

## Чем source отличается от запуска новой программы  
**source file** (то же, что . file) — выполняет скрипт в текущей оболочке. Переменные (ROS_DISTRO, PATH, AMENT_PREFIX_PATH) остаются в текущем терминале после завершения.

**Запуск ./script.sh или bash script.sh** создаёт дочерний процесс. Все переменные, заданные внутри, исчезают, когда процесс заканчивается. Именно поэтому после colcon build нужен source install/setup.bash — иначе текущий терминал не увидит новый пакет.  

## Launch-файл

### Содержимое `src/turtle_bringup/launch/sim.launch.py`

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen',
        ),
    ])
```

`generate_launch_description()` возвращает список действий. `Node` — действие запуска процесса (аналог `ros2 run` с двумя аргументами: `package` и `executable`).

### Фрагмент `setup.py` (в существующем `setup(...)`)
```python
from glob import glob

data_files=[
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
],
```

### `colcon build --symlink-install --packages-select turtle_bringup`
- Назначение: пересобрать пакет после добавления launch-файла.
- Результат: `Summary: 1 package finished`. Лог — `evidence/pr02/build.txt`.

### `ros2 pkg prefix turtle_bringup` и `ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"`
- Назначение: убедиться, что launch-файл установлен как ресурс пакета.
- Результат: в `install/.../share/turtle_bringup/launch/` виден `sim.launch.py`.

### `ros2 launch turtle_bringup sim.launch.py`
- Назначение: запустить turtlesim через наш launch-файл.
- Результат: открылось окно turtlesim, в графе появилась нода `/turtlesim`.

### `ros2 node list --no-daemon --spin-time 2`
- Назначение: показать активные ноды без демона, с ожиданием 2 с.
- Результат: `/turtlesim`.

### Остановка
Ctrl+C в терминале A. Окно turtlesim закрылось, `ros2 node list` больше не показывает `/turtlesim`.

---

## Связь команды с движением

### `ros2 interface show geometry_msgs/msg/Twist`
- Назначение: посмотреть структуру сообщения Twist.
- Результат:
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
`Twist` — две тройки чисел: `linear` (линейная скорость) и `angular` (угловая). Для turtlesim используем `linear.x` и `angular.z`.

### `ros2 topic type /turtle1/pose`
- Назначение: узнать тип сообщения позы.
- Результат: `turtlesim/msg/Pose` (Jazzy).

### Поза ДО движения
```bash
ros2 topic echo /turtle1/pose --once
```
- Назначение: получить одно сообщение с текущей позой.
- Результат (ДО):
```
x: 5.54444561004639
y: 5.54444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```
Черепаха в центре, смотрит вдоль X, скорости нулевые.

### Одна команда движения
```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
- Назначение: отправить ровно одно сообщение Twist: вперёд 1.0 м/с, поворот 0.5 рад/с.
- Ожидаемое направление: вперёд по дуге против часовой стрелки (`angular.z > 0`), старт от точки (5.54, 5.54).
- Результат публикации:
```
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=...x=1.0..., angular=...z=0.5)
```
Опубликовано одно сообщение — дальше издатель завершился.

### Поза ПОСЛЕ
```bash
ros2 topic echo /turtle1/pose --once
```
- Результат (ПОСЛЕ):
```
x: 6.50930881500244
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
```

### До / после
| | x | y | theta |
|---|---|---|---|
| **ДО** | 5.5444 | 5.5444 | 0.0000 |
| **ПОСЛЕ** | 6.5093 | 5.7970 | 0.5040 |

Вывод: одна публикация Twist заставляет черепаху кратко двинуться по дуге и остановиться. Чтобы движение шло непрерывно, команду нужно повторять (`--rate`).

---

## Сбой по имени топика и исправление (до / сбой / после)

### Состояние «ДО» — правильный топик
```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
Черепаха двигалась. Поза изменилась: `x=6.5093, y=5.7970, theta=0.504`.

### Состояние «СБОЙ» — публикация в `/cmd_vel`
```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
- `--rate 1` — 1 сообщение в секунду, непрерывно.
- `--wait-matching-subscriptions 0` — не ждать подписчиков; при `--once` публикация зависла бы, потому что подписчика нет.

Результат издателя: каждую секунду печатает `publishing #N: ...`. Ошибок нет. **Черепаха стоит.**

#### Диагностика в C
```bash
ros2 topic info /cmd_vel --verbose
```
```
Type: geometry_msgs/msg/Twist
Publisher count: 1
Node name: _ros2cli_8272
Endpoint type: PUBLISHER
Subscription count: 0
```
Тип правильный, но **подписчиков ноль**.

```bash
ros2 topic info /turtle1/cmd_vel --verbose
```
```
Type: geometry_msgs/msg/Twist
Publisher count: 0
Subscription count: 1
Node name: turtlesim
Endpoint type: SUBSCRIPTION
```
Здесь наоборот: есть подписчик `/turtlesim`, но нет издателя.

#### Сравнение

| | `/cmd_vel` (сбой) | `/turtle1/cmd_vel` (правильно) |
|---|---|---|
| Тип | `geometry_msgs/msg/Twist` | `geometry_msgs/msg/Twist` |
| Издателей | 1 (`_ros2cli_8272`) | 0 (до исправления) |
| Подписчиков | **0** | **1 (`turtlesim`)** |
| Итог | сообщения уходят в пустоту | turtlesim принимает команды |

После остановки ошибочного издателя (Ctrl+C в B) команда `ros2 topic info /cmd_vel --verbose` вернула `Unknown topic '/cmd_vel'` — топик исчез, потому что у него не осталось ни издателей, ни подписчиков.

**Почему правильного типа сообщения недостаточно:** топик в ROS 2 адресуется **именем**, а не типом. Даже если структура сообщения совпадает, но имя топика отличается — доставки не будет. Издатель и подписчик должны сойтись на одном имени.

### Состояние «ПОСЛЕ» — исправлено только имя
```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
Результат издателя:
```
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=...x=1.0..., angular=...z=0.5)
publishing #2: ...
publishing #3: ...
```
Черепаха **непрерывно** движется вперёд по дуге против часовой стрелки.

#### Проверка в C
```bash
ros2 topic info /turtle1/cmd_vel --verbose
```
```
Publisher count: 1
Node name: _ros2cli_8331
Endpoint type: PUBLISHER

Subscription count: 1
Node name: turtlesim
Endpoint type: SUBSCRIPTION
```
Издатель и подписчик на одном топике — доставка работает.

#### Остановка
Ctrl+C в B. Новых команд нет, turtlesim плавно тормозит черепаху. Проверка:
```bash
ros2 topic echo /turtle1/pose --once
```
`linear_velocity` и `angular_velocity` снова нулевые.

### Сводная таблица до / сбой / после

| Этап | Команда в B | Топик | Подписчики | Наблюдение |
|---|---|---|---|---|
| **ДО** | `ros2 topic pub --once /turtle1/cmd_vel ...` | `/turtle1/cmd_vel` | 1 (`turtlesim`) | черепаха сдвинулась по дуге, поза изменилась |
| **СБОЙ** | `ros2 topic pub --rate 1 ... /cmd_vel ...` | `/cmd_vel` | **0** | издатель печатает `publishing #N`, черепаха стоит |
| **ПОСЛЕ** | `ros2 topic pub --rate 1 ... /turtle1/cmd_vel ...` | `/turtle1/cmd_vel` | 1 (`turtlesim`) | черепаха непрерывно едет по дуге |

**Итог:** исправлено **только имя топика**. Тип `geometry_msgs/msg/Twist`, скорости `linear.x=1.0, angular.z=0.5` и `ROS_DOMAIN_ID=16` не менялись. Доставка восстановилась именно за счёт совпадения имени топика. 

### Почему правильного типа сообщения недостаточно

В опыте использовалось **то же самое** сообщение `geometry_msgs/msg/Twist`
с теми же полями `linear.x=1.0` и `angular.z=0.5`. Менялось только имя топика:

- `/cmd_vel` — сбой, подписчиков 0;
- `/turtle1/cmd_vel` — успех, подписчик `/turtlesim`.

Причина в том, что в ROS 2 **топик адресуется именем, а не типом**.

Издатель и подписчик соединяются, только если у них совпадают **три вещи**:

1. **Имя топика** — `/turtle1/cmd_vel` у обоих.
2. **Тип сообщения** — `geometry_msgs/msg/Twist` у обоих.
3. **QoS-профиль** — в нашем случае `RELIABLE`, `VOLATILE`, `KEEP_LAST` (значения по умолчанию совпали).

Тип — необходимое, но **не достаточное** условие. Даже идеально структурированное сообщение, отправленное в `cmd_vel`, не дойдёт до turtlesim, потому что его подписка объявлена на другое имя. Проверка
`ros2 topic info /cmd_vel --verbose` показала `Subscription count: 0` — никто не слушает этот топик. Сообщения уходят в пустоту, ошибки при этом не возникает: ROS 2 считает нормальным публиковать топик без подписчиков (это разрешает флаг `--wait-matching-subscriptions 0`).
