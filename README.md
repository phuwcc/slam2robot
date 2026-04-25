# 🤖 SLAM2ROBOT - ROS 2 Simulation Package

![Ubuntu 22.04](https://img.shields.io/badge/Ubuntu-22.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-34a853?style=for-the-badge&logo=ros&logoColor=white)
![Gazebo](https://img.shields.io/badge/Gazebo-Classic-FFB200?style=for-the-badge&logo=gazebo&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## 📌 Giới thiệu

Package `slam2robot` là một môi trường mô phỏng robot bánh xích tích hợp tay máy 2 bậc tự do trong Gazebo.

Hệ thống bao gồm:

- Mô hình **URDF + mesh**
- Tích hợp **Camera, LiDAR, IMU**
- Điều khiển **diff-drive bằng bàn phím**
- Sử dụng **ros2_control** cho 2 khớp tay `l1`, `l2`
- Node `arm_controller` để nhập góc điều khiển tay máy

---

## ✨ Thành phần chính

- 🚗 Robot bánh xích (Tracked Robot)
- 🤖 Tay máy 2 khớp quay
- 📡 Hệ thống cảm biến:
  - LiDAR (`/scan`)
  - Camera (`/camera/image_raw`)
  - IMU (`/imu`)
- 🎮 Điều khiển:
  - Bàn phím (`cmd_vel`)
  - Nhập góc tay máy

---

## 🛠️ 1. Yêu cầu hệ thống (Prerequisites)

Môi trường đã kiểm tra với **ROS 2 Humble**

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
  ros-humble-teleop-twist-keyboard

Nếu chưa có workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

Đặt package `slam2robot` vào trong `~/ros2_ws/src`.

## 2. Build Package

```bash
cd ~/ros2_ws
rm -rf build/ install/ log/
source /opt/ros/humble/setup.bash
colcon build --packages-select slam2robot
source install/setup.bash
```

Mỗi terminal mới đều nên chạy:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

## 3. Run Gazebo

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py
```

Launch nay sẽ:

- Nap `robot_description`
- Mo Gazebo voi `turtlebot3_world`
- Spawn robot vào thế giới
- Khởi tạo `joint_state_broadcaster`
- Khởi tạo `joint_position_controller` cho cánh tay

## 4. Điều khiển Robot di chuyển bằng bàn phím

Robot sử dụng plugin `gazebo_ros_diff_drive`, vì vậy có thể điều khiển bằng `cmd_vel`.

Mở terminal mới:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Node này mặc định publish lên `/cmd_vel`, phù hợp với diff-drive trong URDF.

Phím hay dùng:

- `i`: tiến
- `,`: lùi
- `j`: quay trái
- `l`: quay phải
- `k`: dừng

## 5. Điều Khiển Cánh Tay

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

## 6. Xem Robot Trong RViz

Nếu muốn xem nhanh model trong RViz thay vì Gazebo:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot display.launch.py
```

---

## 7. Topic Hữu Ích

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

---

## 8. Lệnh Kiểm Tra Nhanh

Kiểm tra controller:

```bash
ros2 control list_controllers
```

Kiểm tra joint state:

```bash
ros2 topic echo /joint_states --once
```

Kiểm tra camera:

```bash
ros2 topic echo /camera/camera_info --once
```

Kiểm tra lidar:

```bash
ros2 topic echo /scan --once
```

---

## 9. Thứ Tự Chạy Đầy Đủ

**Terminal 1:**
```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam2robot gazebo.launch.py
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

Đọc dữ liệu từ sensor:

```bash
ros2 topic echo /imu
ros2 topic echo /scan
```

---

## 10. Lỗi Thường Gặp

`ros2 run slam2robot arm_controller` không chạy:

- Kiểm tra đã `colcon build`  
- Kiểm tra đã `source install/setup.bash`  

Controller bị treo ở `waiting for service /controller_manager/list_controllers`:

- Tắt Gazebo cũ  
- Build lại package  
- Launch lại từ đầu  

Robot không đi được bằng bàn phím:

- Kiểm tra `teleop_twist_keyboard` đã cài  
- Kiểm tra topic `/cmd_vel` có dữ liệu:

```bash
ros2 topic echo /cmd_vel
```

Cánh tay không nhúc nhích:

- Kiểm tra controller:

```bash
ros2 control list_controllers
```

- Kiểm tra topic lệnh:

```bash
ros2 topic echo /joint_position_controller/commands
```
