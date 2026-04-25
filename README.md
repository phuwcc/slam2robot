# SLAM2ROBOT - ROS 2 Simulation Package

![Ubuntu 22.04](https://img.shields.io/badge/Ubuntu-22.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-34a853?style=for-the-badge&logo=ros&logoColor=white)
![Gazebo](https://img.shields.io/badge/Gazebo-Classic-FFB200?style=for-the-badge&logo=gazebo&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 1. Giới thiệu

Package `slam2robot` mô phỏng robot bánh xích có tay máy 2 bậc tự do trong Gazebo, kèm các cảm biến phục vụ SLAM 2D:

- LiDAR `/scan`
- Camera `/camera/image_raw`
- IMU `/imu`
- Odom từ plugin `gazebo_ros_diff_drive`

Hiện package hỗ trợ:

- Mô phỏng robot trong Gazebo
- Điều khiển robot bằng `cmd_vel`
- Điều khiển tay máy 2 khớp
- Chạy `Cartographer 2D` để dựng bản đồ

## 2. Yêu cầu hệ thống

Đã kiểm tra với:

- Ubuntu 22.04
- ROS 2 Humble

Cài dependency:

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
  ros-humble-cartographer-ros
```

Nếu chưa có workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

Đặt package `slam2robot` vào `~/ros2_ws/src`.

## 3. Build package

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select slam2robot
source install/setup.bash
```

Mỗi terminal mới nên chạy:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

## 4. Chạy mô phỏng Gazebo

```bash
ros2 launch slam2robot gazebo.launch.py
```

Launch này sẽ:

- nạp `robot_description`
- mở Gazebo với `turtlebot3_world`
- spawn robot vào môi trường
- khởi tạo controller cho tay máy

## 5. Điều khiển robot

Mở terminal mới:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Node này publish lên `/cmd_vel`.

Phím thường dùng:

- `i`: tiến
- `,`: lùi
- `j`: quay trái
- `l`: quay phải
- `k`: dừng

## 6. Điều khiển tay máy

Mở terminal mới:

```bash
ros2 run slam2robot arm_controller
```

Node publish lên:

```bash
/joint_position_controller/commands
```

Nhập theo dạng:

```text
l1 l2
```

Ví dụ:

```text
0.5 0.3
1.0 1.2
```

Giới hạn hiện tại:

- `l1`: `-0.4 -> 1.57` rad
- `l2`: `-0.4 -> 1.57` rad

Nhập `q` để thoát.

## 7. Chạy SLAM Cartographer 2D

### Cách 1: Chạy toàn bộ bằng một launch

```bash
ros2 launch slam2robot cartographer.launch.py
```

Launch này sẽ:

- khởi động Gazebo
- chạy `cartographer_node`
- chạy `occupancy_grid_node`
- mở RViz

### Cách 2: Gazebo đã chạy sẵn

Nếu bạn đã chạy:

```bash
ros2 launch slam2robot gazebo.launch.py
```

thì có thể chạy riêng Cartographer:

```bash
ros2 launch slam2robot cartographer.launch.py start_gazebo:=false
```

### Topic và frame dùng cho SLAM

- Scan: `/scan`
- Odom: `/odom`
- Base frame: `base_link`
- Map frame: `map`

### Lưu bản đồ sau khi quét xong

Cartographer chỉ tạo bản đồ runtime. Nếu muốn lưu map để dùng tiếp với Nav2 hoặc map_server:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

Hoặc dùng launch đã bọc sẵn trong package:

```bash
ros2 launch slam2robot cartographer.launch.py start_gazebo:=false start_slam:=false start_rviz:=false save_map:=true
```

Lưu vào đường dẫn khác:

```bash
ros2 launch slam2robot cartographer.launch.py start_gazebo:=false start_slam:=false start_rviz:=false save_map:=true map_file:=/tmp/my_map
```

## 8. Xem robot trong RViz

Nếu chỉ muốn xem model:

```bash
ros2 launch slam2robot display.launch.py
```

## 9. Topic hữu ích

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

## 10. Lệnh kiểm tra nhanh

Kiểm tra controller:

```bash
ros2 control list_controllers
```

Kiểm tra laser:

```bash
ros2 topic echo /scan --once
```

Kiểm tra TF:

```bash
ros2 run tf2_tools view_frames
```
