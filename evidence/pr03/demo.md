# Отчёт по практической работе ПР03: Исследование работы ROS 2-ноды patrol

## 1. Архитектурные механизмы ROS 2 и Python

### rclpy.init(args=args) — запуск контекста библиотеки
Данный вызов выполняет первичную настройку клиентской библиотеки RCL для Python: формирует глобальный контекст процесса, разбирает аргументы командной строки, относящиеся к ROS (в частности, --ros-args, переназначения -r и параметры -p), регистрирует обработчики системных сигналов и поднимает транспортный слой DDS. Пока rclpy.init() не выполнен, создание любых сущностей ROS 2 — нод, издателей, подписок, таймеров — невозможно.

### rclpy.spin(node) — цикл обработки событий
Этот вызов передаёт управление исполнителю (по умолчанию — SingleThreadedExecutor), который в бесконечном цикле извлекает события из очереди DDS и диспетчеризует их. Событиями являются: приход сообщений в подписки, срабатывание таймеров, готовность ответов на сервисные вызовы. Для каждого события вызывается соответствующая функция обратного вызова. spin удерживает ноду активной до момента запроса завершения (например, через rclpy.shutdown()).

### Callbacks — событийная модель работы
Вместо активного опроса сокетов в цикле while True разработчик регистрирует обработчики:
- **pose_callback** — активируется исполнителем при появлении нового сообщения в топике /turtle1/pose. Получает готовый объект Pose и кэширует его в self.latest_pose.
- **timer_callback** — срабатывает с фиксированной периодичностью (0.1 с, т.е. 10 Гц). Внутри вызывается чистая функция compute_cmd_vel, а результат оформляется в сообщение Twist и публикуется.

### Ctrl+C и корректное завершение
Нажатие Ctrl+C генерирует сигнал SIGINT, который перехватывается блоком try ... except KeyboardInterrupt, выводя процесс из rclpy.spin(). Далее в секции finally выполняются:
- **node.destroy_node()** — удаление подписок, издателей, таймеров и освобождение ресурсов DDS-сущностей;
- **rclpy.shutdown()** — финализация контекста RCL и остановка внутренних потоков.

---

## 2. Эксперимент «Сломать»: некорректное имя топика

### Запуск без переназначения
```bash
ros2 run patrol patrol
```
Терминал:
```text
[INFO] [1791054573.269976520] [patrol]: cmd: linear.x=0.5, angular.z=0.3
```

### Поведение turtlesim
Черепаха **не двигается**.

### Анализ графа
```bash
ros2 topic info /cmd_vel --verbose
```
Вывод:
```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: patrol
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.a0.a1.e3.40.8d.4b.00.00.00.00.00.00.14.03
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 0
```

```bash
ros2 topic info /turtle1/cmd_vel --verbose
```
Вывод:
```text
Type: geometry_msgs/msg/Twist

Publisher count: 0

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.a0.a1.bf.40.68.88.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

### Причина сбоя:
Издатель в ноде patrol становится `/cmd_vel`, тогда как turtlesim подписан на `/turtle1/cmd_vel`. Имена не совпадают — у `/cmd_vel` нет ни одного подписчика, команды до черепахи не доходят.

---

## 3. Эксперимент «Доказать»: исправление через remapping

### Запуск с переназначением
```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

### Поведение turtlesim
Черепаха непрерывно движется вперед и поворачивается по дуге окружности (`linear.x = 0.5`, `angular.z = 0.3`).

### Проверка сопряжения топика:
```bash
ros2 topic info /turtle1/cmd_vel --verbose
```
Вывод:
```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: patrol
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.a0.a1.22.42.1b.d3.00.00.00.00.00.00.14.03
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.a0.a1.bf.40.68.88.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

### Измерение частоты публикации (10 секунд)
```bash
ros2 topic hz /turtle1/cmd_vel --window 100
```
Вывод:
```text
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00030s window: 100
```
*Результат*: средняя частота составляет ~10.0 Гц, что в точности соответствует заданному периоду таймера 0.1 с.

### Остановка ноды и поведение turtlesim:
После `Ctrl+C` публикация команд прекращается. `turtlesim` не тормозит мгновенно: в симуляторе заложен внутренний таймаут (0.5–1.0 с), по истечении которого при отсутствии новых команд скорость плавно снижается до нуля. Прекращение работы управляющего процесса не является для симулятора командой остановки.