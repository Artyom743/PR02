# Эксперименты с параметрами ноды patrol (ПР04)

## 1. Запуск симулятора и ноды

### Запуск узлов
```bash
$ export ROS_DOMAIN_ID=16
$ ros2 launch turtle_bringup sim.launch.py &
$ ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel &
```

---

## 2. Динамическое изменение параметров и частоты публикации

### Замер начальной частоты (по умолчанию 10.0 Гц)
```bash
$ ros2 param get /patrol publish_hz
Double value is: 10.0

$ ros2 topic hz /turtle1/cmd_vel
average rate: 10.001
	min: 0.100s max: 0.100s std dev: 0.00021s window: 11
average rate: 10.001
	min: 0.099s max: 0.100s std dev: 0.00025s window: 22
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00045s window: 32
average rate: 9.999
	min: 0.099s max: 0.101s std dev: 0.00042s window: 42
average rate: 10.001
	min: 0.099s max: 0.101s std dev: 0.00041s window: 53
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00043s window: 64
```

### Переключение частоты на 5.0 Гц
```bash
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful

$ ros2 topic hz /turtle1/cmd_vel
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00018s window: 7
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00014s window: 13
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00012s window: 18
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00011s window: 24
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00010s window: 29
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00009s window: 34
```
При успешной валидации параметра старый таймер отменяется и уничтожается (`timer.cancel()`, `timer.destroy()`), после чего создаётся новый таймер с периодом `1.0 / 5.0 = 0.2 с`. Частота публикации в топик снизилась до 5.0 Гц.

### Изменение скоростей `linear_speed` и `turn_rate`
```bash
$ ros2 param set /patrol linear_speed 0.8
Set parameter successful

$ ros2 param set /patrol turn_rate -0.5
Set parameter successful

$ ros2 topic echo /turtle1/cmd_vel --once
linear:
  x: 0.8
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: -0.5
---
```
Команды движения немедленно отражают обновленные параметры скорости.

---

## 3. Воспроизведение дефекта (отказ при отсутствии валидации)

### Модель дефекта
Если проверка параметров отключена, передача значения `publish_hz = 0.0` приводит к попытке вычисления периода таймера делением на ноль:
```python
period = 1.0 / hz  # ZeroDivisionError: float division by zero
```
В рантайме ROS 2 это приводит к необработанному исключению внутри `parameters_callback`:
```text
Traceback (most recent call last):
    File "/home/art/ros2-pr01/PR02/build/patrol/patrol/patrol.py", line 81, in _create_timer
        period = 1.0 / hz
ZeroDivisionError: float division by zero
```
В результате узел аварийно завершает работу либо остаётся в некорректном полуразрушенном состоянии (старый таймер отменён, новый не создан, управление прервано).

---

## 4. Доказательство устранения дефекта (валидация параметров)

### Попытка установки некорректных значений через CLI
```bash
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be in (1.0, 30.0), got 0.0

$ ros2 param set /patrol publish_hz -5.0
Setting parameter failed: publish_hz must be in (1.0, 30.0), got -5.0

$ ros2 param get /patrol publish_hz
Double value is: 10.0
```
Значение `0.0` отклонено колбэком установки параметров (`SetParametersResult(successful=False, reason=...)`).
Активное состояние узла полностью сохранено: таймер продолжает публиковать команды с частотой 5.0 Гц.

### Тестирование граничных условий в тестах
Модульные тесты функции валидации (`validate_parameter_value`) покрывают:
- Допустимые частоты (1.0, 5.0, 10.0, 30.0 Гц) -> `passed`.
- Нулевую частоту (0.0 Гц) -> отклонено (`passed`).
- Отрицательную частоту (-1.0 Гц) -> отклонено (`passed`).
- Запредельную частоту (31.0 Гц) -> отклонено (`passed`).
- Нечисловые и неконечные значения (`NaN`, `Inf`) -> отклонено (`passed`).
- Диапазоны скоростей `linear_speed` (0.0 .. 1.0) и `turn_rate` (-1.0 .. 1.0) -> `passed`.

---

## 5. Вызов сервиса `/clear` и инспекция действий (Action)

### Вызов сервиса `/clear`
```bash
$ ros2 service call /clear std_srvs/srv/Empty {}
waiting for service to become available...
requester: making request: std_srvs.srv.Empty_Request()

response:
std_srvs.srv.Empty_Response()
```
Траектория черепахи на экране симулятора успешно очищена.

### Обнаружение доступных actions
```bash
$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
```

### Отличие сервисного запроса от цели действия (Goal)
Сервисный запрос (Service Request) предназначен для синхронной или короткой атомарной операции по схеме «запрос — ответ» без промежуточной обратной связи и возможности отмены выполнения в процессе. 

Цель действия (Action Goal) предназначена для длительных асинхронных задач (например, физического перемещения робота или поворота на заданный угол), поддерживает непрерывную передачу промежуточного прогресса (Feedback), а также позволяет клиенту прервать или отменить выполнение цели (Cancel Goal) до её завершения.
