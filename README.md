# Курс «Робототехника · ROS 2»

Репозиторий практических работ по курсу робототехники (НГУ).

---

## ПР05. Launch, QoS и повтор записи

### Цель работы
Сборка всей системы одной launch-командой с аргументами и пространством имён (`namespace`). Запись потока данных в формат MCAP. Демонстрация несовместимости профилей QoS на живом потоке (best_effort-издатель и reliable-подписчик) и её исправление. Проверка восстановленной совместимости как на живом потоке, так и на повторе записи (replay) с использованием QoS override.

---

### Порядок локального воспроизведения ПР05

#### 1. Сборка пакетов
```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select patrol course_bringup
source install/setup.bash  
```

#### 2. Запуск тестов
```bash
python3 -m pytest src/patrol/test
```  

#### 3. Воспроизведение сбоя QoS (Стадия 2)  
Для того чтобы увидеть сбой, нужно запустить систему в пространстве имён /robot_a, где издатель (pose_relay) публикует данные с профилем best_effort, а подписчик (проверка через CLI) пытается слушать их с профилем reliable.  
```bash
export ROS_DOMAIN_ID=16

# В терминале 1: запуск системы со сломанным QoS (reliable-подписчик)
ros2 launch course_bringup patrol.launch.py namespace:=robot_a subscriber_reliability:=reliable record:=false

# В терминале 2: ожидаемый таймаут (сообщения не приходят)
timeout 3s ros2 topic echo /robot_a/sensor_pose --qos-reliability reliable --once > evidence/pr05/qos-before.txt  
```
Ожидаемый результат: команда ros2 topic echo завершится по таймауту (через 3 секунды), файл qos-before.txt останется пустым. Это доказательство того, что несовместимые профили QoS блокируют доставку, хотя сам топик виден в ros2 topic list.  
  
#### 4. Запись исправленного потока (Стадия 3)  
Теперь нужно перезапустить систему с совместимым профилем (best_effort), проверить, что данные идут, и записать их в файл формата MCAP.  
```bash  
# В терминале 1: перезапуск с совместимым QoS
ros2 launch course_bringup patrol.launch.py namespace:=robot_a subscriber_reliability:=best_effort record:=false

# В терминале 2: проверка живого потока и запись доказательства
timeout 3s ros2 topic echo /robot_a/sensor_pose --qos-reliability best_effort --once > evidence/pr05/qos-after.txt

# Запись потока в MCAP (остановить через Ctrl+C после появления первых сообщений)
ros2 bag record -s mcap -o evidence/pr05/bag --topics /robot_a/sensor_pose

# Информация о bag-файле и копирование метаданных
ros2 bag info evidence/pr05/bag -s mcap >> evidence/pr05/qos-after.txt
cp evidence/pr05/bag/metadata.yaml evidence/pr05/bag-metadata.yaml  
```  

#### 5. Проверка повтора записи (Replay)  
Чтобы доказать, что запись воспроизводится корректно с тем же профилем QoS, используется файл config/qos-overrides.yaml. Убедись, что он существует и содержит правильные настройки.  
```bash  
# В терминале 1: запуск реплея с применением QoS override
ros2 bag play evidence/pr05/bag -s mcap --qos-profile-overrides-path config/qos-overrides.yaml

# В терминале 2: проверка доставки сообщений из записи
timeout 3s ros2 topic echo /robot_a/sensor_pose --qos-reliability best_effort --once  
```  

### Автоматическая проверка  
```bash
python3 .course-kit/v1/tools/check_practice.py PR05 --submission .
```

