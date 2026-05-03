import math
import os
import signal
from typing import Optional

import rclpy
from nav_msgs.msg import OccupancyGrid
from rclpy.node import Node


def _quaternion_to_yaw(z: float, w: float) -> float:
    return math.atan2(2.0 * w * z, 1.0 - 2.0 * z * z)


class MapAutosaver(Node):
    def __init__(self) -> None:
        super().__init__('map_autosaver')

        self.declare_parameter('map_topic', '/map')
        self.declare_parameter('map_file', '')
        self.declare_parameter('free_thresh', 0.25)
        self.declare_parameter('occupied_thresh', 0.65)

        self.map_topic = self.get_parameter('map_topic').get_parameter_value().string_value
        self.map_file = self.get_parameter('map_file').get_parameter_value().string_value
        self.free_thresh = self.get_parameter('free_thresh').value
        self.occupied_thresh = self.get_parameter('occupied_thresh').value

        self.latest_map: Optional[OccupancyGrid] = None
        self._map_saved = False

        self.create_subscription(OccupancyGrid, self.map_topic, self._map_callback, 10)
        self.get_logger().info(
            f"Waiting for map on '{self.map_topic}'. Autosave target: {self.map_file}"
        )

        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

    def _map_callback(self, msg: OccupancyGrid) -> None:
        self.latest_map = msg

    def _handle_shutdown_signal(self, signum, frame) -> None:
        del frame
        if self._map_saved:
            return

        self.get_logger().info(f'Received signal {signum}. Saving latest map before exit.')
        self._save_latest_map()
        self._map_saved = True
        raise KeyboardInterrupt

    def _save_latest_map(self) -> None:
        if self.latest_map is None:
            self.get_logger().warning('No map received on /map yet, skipping autosave.')
            return

        map_file = self.map_file
        if not map_file:
            self.get_logger().error('Parameter map_file is empty, cannot save map.')
            return

        output_dir = os.path.dirname(map_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        pgm_path = f'{map_file}.pgm'
        yaml_path = f'{map_file}.yaml'

        width = self.latest_map.info.width
        height = self.latest_map.info.height
        data = list(self.latest_map.data)
        occupied_value = self.occupied_thresh * 100.0
        free_value = self.free_thresh * 100.0

        with open(pgm_path, 'wb') as pgm_file:
            pgm_file.write(f'P5\n{width} {height}\n255\n'.encode('ascii'))
            for row in range(height - 1, -1, -1):
                for col in range(width):
                    value = data[row * width + col]
                    if value < 0:
                        pixel = 205
                    elif value >= occupied_value:
                        pixel = 0
                    elif value <= free_value:
                        pixel = 254
                    else:
                        pixel = 205
                    pgm_file.write(bytes((pixel,)))

        origin = self.latest_map.info.origin
        yaw = _quaternion_to_yaw(origin.orientation.z, origin.orientation.w)
        image_name = os.path.basename(pgm_path)

        with open(yaml_path, 'w', encoding='ascii') as yaml_file:
            yaml_file.write(f'image: {image_name}\n')
            yaml_file.write(f'resolution: {self.latest_map.info.resolution}\n')
            yaml_file.write(
                f'origin: [{origin.position.x}, {origin.position.y}, {yaw}]\n'
            )
            yaml_file.write('negate: 0\n')
            yaml_file.write(f'occupied_thresh: {self.occupied_thresh}\n')
            yaml_file.write(f'free_thresh: {self.free_thresh}\n')
            yaml_file.write('mode: trinary\n')

        self.get_logger().info(f'Saved map to {yaml_path} and {pgm_path}')


def main() -> None:
    rclpy.init()
    node = MapAutosaver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if not node._map_saved:
            node._save_latest_map()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
