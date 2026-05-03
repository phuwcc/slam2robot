import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/phuc/ros2_ws/src/slam2robot/install/slam2robot'
