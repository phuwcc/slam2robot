#!/usr/bin/env python3
"""Sequential arm controller for l1 and l2 joints."""

import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class ArmSequentialController(Node):
    """Publish sequential position commands for the arm joints."""

    def __init__(self) -> None:
        super().__init__("arm_sequential_controller")
        self.publisher = self.create_publisher(
            Float64MultiArray,
            "/joint_position_controller/commands",
            10,
        )

        self.current_l1 = 0.0
        self.current_l2 = 0.0
        self.l1_limits = (-0.4, 1.57)
        self.l2_limits = (-0.4, 1.57)

    def clamp(self, value: float, limits: tuple[float, float]) -> float:
        return max(limits[0], min(limits[1], value))

    def publish_command(self, l1: float, l2: float) -> None:
        msg = Float64MultiArray()
        msg.data = [l1, l2]
        self.publisher.publish(msg)
        self.get_logger().info(f"Published command l1={l1:.3f}, l2={l2:.3f}")

    def print_usage(self) -> None:
        print("Nhap 2 gia tri: l1 l2 (rad). Vi du: 0.5 0.3")
        print(
            f"Gioi han: l1 {self.l1_limits[0]} den {self.l1_limits[1]} rad, "
            f"l2 {self.l2_limits[0]} den {self.l2_limits[1]} rad"
        )
        print("Nhap q de thoat.")

    def run(self) -> None:
        self.print_usage()

        while rclpy.ok():
            try:
                user_input = input("Nhap lenh (l1 l2): ").strip()
            except EOFError:
                break

            if user_input.lower() == "q":
                break

            parts = user_input.split()
            if len(parts) != 2:
                print("Sai dinh dang, can 2 gia tri.")
                continue

            try:
                target_l1 = self.clamp(float(parts[0]), self.l1_limits)
                target_l2 = self.clamp(float(parts[1]), self.l2_limits)
            except ValueError:
                print("Gia tri khong hop le.")
                continue

            print(f"Dang dua l1 den {target_l1:.3f} rad...")
            self.publish_command(target_l1, self.current_l2)
            time.sleep(2.0)

            print(f"Dang dua l2 den {target_l2:.3f} rad...")
            self.publish_command(target_l1, target_l2)
            time.sleep(2.0)

            self.current_l1 = target_l1
            self.current_l2 = target_l2
            print("Hoan tat.\n")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ArmSequentialController()
    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down arm controller node...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
