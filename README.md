# 🤖 SLAM2ROBOT - ROS 2 Simulation Package

![Ubuntu 22.04](https://img.shields.io/badge/Ubuntu-22.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-34a853?style=for-the-badge&logo=ros&logoColor=white)
![Gazebo](https://img.shields.io/badge/Gazebo-Classic-FFB200?style=for-the-badge&logo=gazebo&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## 📌 Giới thiệu

Package `slam2robot` là môi trường mô phỏng robot bánh xích tích hợp tay máy 2 bậc tự do trong Gazebo, có thêm cảm biến để chạy SLAM 2D.

Hệ thống bao gồm:

- Mô hình **URDF + mesh**
- Tích hợp **Camera, LiDAR, IMU**
- Odom từ plugin **gazebo_ros_diff_drive**
- Điều khiển **diff-drive bằng bàn phím**
- Sử dụng **ros2_control** cho 2 khớp tay `l1`, `l2`
- Node `arm_controller` để nhập góc điều khiển tay máy
- Launch `gazebo.launch.py` để chọn map và thuật toán SLAM

---

## ✨ Thành phần chính

- 🚗 Robot bánh xích
- 🤖 Tay máy 2 khớp quay
- 📡 Hệ thống cảm biến:
  - LiDAR (`/scan`)
  - Camera (`/camera/image_raw`)
  - IMU (`/imu`)
- 🗺️ SLAM:
  - Cartographer 2D
  - Gmapping
  - Occupancy Grid (`/map`)
- 🎮 Điều khiển:
  - Bàn phím (`/cmd_vel`)
  - Nhập góc tay máy

---

## 🛠️ 1. Yêu cầu hệ thống

Môi trường đã kiểm tra với:

- **Ubuntu 22.04**
- **ROS 2 Humble**

### Cài đặt dependencies

```bash
sudo apt update
sudo apt install -y \
  ros-humble-gazebo-ros \
  ros-humble-gazebo-ros2-control \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-xacro \
  ros-humble-joint-state-publisher-gui \
  ros-humble-rviz2 \
  ros-humble-turtlebot3-gazebo \
  ros-humble-teleop-twist-keyboard \
  ros-humble-cartographer \
  ros-humble-cartographer-ros \
  ros-humble-slam-gmapping \
  ros-humble-nav2-map-server
```

Nếu chưa có workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

Đặt package `slam2robot` vào trong `~/ros2_ws/src`.

## 2. Build package

```bash
cd ~/ros2_ws
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --packages-select slam2robot
source install/setup.bash
```

Nếu chỉ build lại package này sau khi sửa launch/URDF/config, nên dùng lại đúng chuỗi lệnh trên để tránh dính file build cũ.

Mỗi terminal mới đều nên chạy:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

## 3. Chạy mô phỏng Gazebo

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py world:=world_1 slam:=cartographer
```

Launch này sẽ:

- Nạp `robot_description`
- Mở Gazebo với một trong 5 world: `world_1` ... `world_5`
- Spawn robot vào môi trường
- Khởi tạo `joint_state_broadcaster`
- Khởi tạo `joint_position_controller` cho cánh tay
- Chạy một trong 2 thuật toán SLAM: `cartographer` hoặc `gmapping`
- Không mở RViz

Ví dụ:

```bash
ros2 launch slam2robot gazebo.launch.py world:=world_3 slam:=gmapping
```

Nếu muốn nạp sẵn một map tham chiếu trong thư mục `map/` và vẫn chạy SLAM:

```bash
ros2 launch slam2robot gazebo.launch.py \
  world:=world_3 \
  slam:=cartographer \
  selected_map:=warehouse.yaml \
  map_file:=warehouse_scan
```

Ý nghĩa:

- `selected_map:=warehouse.yaml`: nạp map tham chiếu từ `share/slam2robot/map/warehouse.yaml`
- `slam:=cartographer` hoặc `slam:=gmapping`: chọn thuật toán SLAM
- `map_file:=warehouse_scan`: lưu ra `share/slam2robot/map/warehouse_scan.yaml` và `.pgm`

Để xem trên RViz, mở terminal khác và chạy:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot display.launch.py use_sim_time:=true start_joint_state_publisher_gui:=false
```

RViz sẽ hiển thị:

- `Reference Map`: map đã chọn
- `SLAM Map`: map robot đang quét realtime
- Robot và các frame TF

## 4. Điều khiển robot di chuyển bằng bàn phím

Robot sử dụng plugin `gazebo_ros_diff_drive`, vì vậy có thể điều khiển bằng `cmd_vel`.

Mở terminal mới:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Node này mặc định publish lên `/cmd_vel`.

Phím hay dùng:

- `i`: tiến
- `,`: lùi
- `j`: quay trái
- `l`: quay phải
- `k`: dừng

## 5. Điều khiển cánh tay

Mở terminal mới:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run slam2robot arm_controller
```

Node `arm_controller` publish lên topic:

```bash
/joint_position_controller/commands
```

Cách nhập:

```text
l1 l2
```

Ví dụ:

```text
0.5 0.3
1.0 1.2
```

Ý nghĩa:

- Robot đưa `l1` tới góc mục tiêu
- Chờ 2 giây
- Sau đó đưa `l2` tới góc mục tiêu

Giới hạn hiện tại:

- `l1`: `-0.4 -> 1.57` rad
- `l2`: `-0.4 -> 1.57` rad

Nhập:

```text
q
```

để thoát node.

---

## 6. Xem robot trong RViz

Nếu muốn xem nhanh model trong RViz:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot display.launch.py
```

File RViz dùng chung hiện tại là:

```bash
rviz/robot.rviz
```

---

## 7. Chạy SLAM Cartographer 2D

### Cách 1: Chạy toàn bộ bằng một launch

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py world:=world_1 slam:=cartographer
```

Launch này sẽ khởi động Gazebo, chạy Cartographer và mở RViz.

### Cách 2: Gazebo đã chạy sẵn

Nếu bạn đã chạy sẵn:

```bash
ros2 launch slam2robot gazebo.launch.py world:=world_1 slam:=cartographer
```

thì có thể chạy riêng Cartographer:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py start_gazebo:=false world:=world_1 slam:=cartographer
```

### Topic và frame dùng cho SLAM

- Scan: `/scan`
- Odom: `/odom`
- Base frame: `base_link`
- Map frame: `map`

File cấu hình:

- Cartographer: `config/cartographer_2d.lua`
- Gmapping: `config/gmapping.yaml`

### Lưu bản đồ sau khi quét xong

`gazebo.launch.py` hiện đã bật autosave mặc định. Khi bạn dừng launch bằng `Ctrl+C`, node `map_autosaver` sẽ ghi:

- `<map_file>.yaml`
- `<map_file>.pgm`

vào thư mục `map/` hoặc đường dẫn bạn truyền qua tham số `map_file`.

Nếu `map_file` là đường dẫn tương đối, launch sẽ tự hiểu là lưu trong thư mục `share/slam2robot/map/`.

Hoặc dùng chính `gazebo.launch.py`:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py start_gazebo:=false start_slam:=false start_rviz:=false save_map:=true world:=world_1 slam:=cartographer
```

Lưu vào đường dẫn khác:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py start_gazebo:=false start_slam:=false start_rviz:=false save_map:=true world:=world_1 slam:=cartographer map_file:=/tmp/my_map
```

---

## 8. Topic hữu ích

Kiểm tra topic:

```bash
ros2 topic list
```

Một số topic quan trọng:

- `/cmd_vel`
- `/joint_states`
- `/joint_position_controller/commands`
- `/scan`
- `/camera/image_raw`
- `/camera/camera_info`
- `/imu`
- `/map`

---

## 9. Lệnh kiểm tra nhanh

Kiểm tra controller:

```bash
ros2 control list_controllers
```

Kiểm tra joint state:

```bash
ros2 topic echo /joint_states --once
```

Kiểm tra lidar:

```bash
ros2 topic echo /scan --once
```

Kiểm tra TF:

```bash
ros2 run tf2_tools view_frames
```

---

## 10. Thứ tự chạy đầy đủ

### Mô phỏng + điều khiển tay máy

**Terminal 1:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py world:=world_1 slam:=cartographer
```

**Terminal 2:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot display.launch.py
```

**Terminal 3:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Terminal 4:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run slam2robot arm_controller
```

### Chạy SLAM Cartographer 2D

**Terminal 1:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py world:=world_1 slam:=cartographer
```

**Terminal 2:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Di chuyển robot để quét bản đồ.

**Terminal 3:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py start_gazebo:=false start_slam:=false start_rviz:=false save_map:=true world:=world_1 slam:=cartographer map_file:=~/my_map
```

Lệnh ở `Terminal 3` dùng để lưu map sau khi quét xong.
