# Курс «Робототехника · ROS 2»

Репозиторий практических работ по курсу робототехники (НГУ).

## ПР06. Модель робота, tf2 и QoS преобразований

### Цель работы

Собрать параметризованную модель Ackermann-робота в URDF/Xacro, связать корпус, камеру, лидар и IMU в одном дереве tf2, показать на `/tf_static`, как durability решает, увидит ли поздний подписчик преобразования, и доказать корректность геометрии и описания структурными проверками.

---

### Порядок локального воспроизведения ПР06

#### 1. Сборка пакетов и запуск тестов

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select course_description
source install/setup.bash
``` 

#### 2. Запуск модели и проверка QoS (Стадия 1)  

Запускаем robot_state_publisher и RViz, чтобы развернуть Xacro в URDF и проверить статические преобразования.

```bash  
export ROS_DOMAIN_ID=16

# В терминале 1: запуск отображения робота
ros2 launch course_description display.launch.py  
``` 

В открывшемся RViz: смени Fixed Frame на base_link, нажми Add и добавь RobotModel.

```bash 
# В терминале 2: сохранение доказательств работы QoS
mkdir -p evidence/pr06
{
  echo '## topic info /tf_static'
  ros2 topic info /tf_static --verbose
  echo '## echo transient_local'
  timeout 4 ros2 topic echo /tf_static --once \
    --qos-durability transient_local --qos-reliability reliable; echo "exit=$?"
  echo '## echo volatile'
  timeout 4 ros2 topic echo /tf_static --once \
    --qos-durability volatile --qos-reliability reliable; echo "exit=$?"
} > evidence/pr06/tf-qos.txt 2>&1  
``` 

Ожидаемый результат: первая подписка (transient_local) печатает преобразования и завершается с exit=0, вторая (volatile) ничего не получает и завершается с exit=124. В конец файла tf-qos.txt необходимо дописать текстовое объяснение разницы между /tf и /tf_static.

#### 3. Воспроизведение сбоя геометрии (Стадия 2 — «Сломать»)  

Нужно сломать дерево связей: сделать camera_link родителем lidar_link вместо base_link в файле vehicle.urdf.xacro, сохранив прежний offset.

```bash
# Пересборка после поломки
colcon build --symlink-install --packages-select course_description
source install/setup.bash

# В терминале 1: перезапуск системы со сломанной моделью
ros2 launch course_description display.launch.py

# В терминале 2: сохранение доказательства неверного положения
echo "=== ДО ИСПРАВЛЕНИЯ (СЛОМАНО) ===" > evidence/pr06/model-check.txt
timeout 3s ros2 run tf2_ros tf2_echo base_link lidar_link >> evidence/pr06/model-check.txt
```

Ожидаемый результат: координаты лидара изменятся с [0.0, 0.0, 0.1] на [0.25, 0.0, 0.15] (он «улетит» вперед и вверх), что доказывает неверное положение сенсора.  

#### 4. Восстановление связей (Стадия 3 — «Доказать»)  

Возвращаем base_link в качестве родителя для lidar_link и проверяем, что геометрия восстановлена.

```bash
# Пересборка после починки
colcon build --symlink-install --packages-select course_description
source install/setup.bash

# В терминале 1: перезапуск исправленной системы
ros2 launch course_description display.launch.py

# В терминале 2: проверка корректных координат и структуры URDF
echo -e "\n=== ПОСЛЕ ИСПРАВЛЕНИЯ (ПРАВИЛЬНО) ===" >> evidence/pr06/model-check.txt
timeout 3s ros2 run tf2_ros tf2_echo base_link lidar_link >> evidence/pr06/model-check.txt

xacro src/course_description/urdf/vehicle.urdf.xacro > /tmp/vehicle.urdf
check_urdf /tmp/vehicle.urdf >> evidence/pr06/model-check.txt
```

Ожидаемый результат: команда tf2_echo снова показывает правильные координаты [0.0, 0.0, 0.1], а check_urdf подтверждает, что дерево связно, и base_link имеет 7 дочерних узлов.  

### Автоматическая проверка  

```bash
python3 .course-kit/v1/tools/check_practice.py PR06 --submission .
```

