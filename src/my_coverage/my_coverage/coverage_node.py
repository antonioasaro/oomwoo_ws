import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class Coverage(Node):
    """Drive forward; when the path ahead is blocked, turn until it clears.
    Combined with SLAM, this bounces around a room and maps it."""

    def __init__(self):
        super().__init__('coverage')
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_subscription(LaserScan, 'scan', self.on_scan, 10)
        self.clear = True
        self.turn_dir = 1.0
        self.create_timer(0.1, self.tick)   # 10 Hz control loop

    def on_scan(self, msg):
        n = len(msg.ranges)
        if n == 0:
            return
        # Check the forward +/- 25 deg sector (forward = scan index 0 for this LiDAR;
        # adjust 'center' if your scan's zero points elsewhere).
        sector = int(math.radians(25) / msg.angle_increment)
        idxs = [(i) % n for i in range(-sector, sector + 1)]
        fwd = [msg.ranges[i] for i in idxs
               if msg.range_min < msg.ranges[i] < msg.range_max]
        was_clear = self.clear
        self.clear = (min(fwd) > 0.35) if fwd else True
        if was_clear and not self.clear:
            self.turn_dir *= -1.0        # alternate turn direction each time we hit something

    def tick(self):
        cmd = Twist()
        if self.clear:
            cmd.linear.x = 0.20          # m/s forward
        else:
            cmd.angular.z = 0.8 * self.turn_dir   # rad/s turn until clear
        self.pub.publish(cmd)


def main():
    rclpy.init()
    node = Coverage()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
    