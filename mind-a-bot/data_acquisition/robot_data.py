import asyncio
import logging
import sys
from go2_webrtc_driver.constants import RTC_TOPIC

# Enable logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def display_data(message):
    """Display the robot's state in a formatted manner."""
    imu_state = message['imu_state']

    # Clear the entire screen and reset cursor position to the top
    sys.stdout.write("\033[H\033[J")

    print("Go2 Robot Status")
    print("===================")
    # Print robot data
    print(f"Mode: {message['mode']}")
    print(f"Progress: {message['progress']}")
    print(f"Gait Type: {message['gait_type']}")
    print(f"Foot Raise Height: {message['foot_raise_height']} m")
    print(f"Position: {message['position']}")
    print(f"Body Height: {message['body_height']} m")
    print(f"Velocity: {message['velocity']}")
    print(f"Yaw Speed: {message['yaw_speed']}")
    print(f"Range Obstacle: {message['range_obstacle']}")
    print(f"Foot Force: {message['foot_force']}")
    print(f"Foot Position (Body): {message['foot_position_body']}")
    print(f"Foot Speed (Body): {message['foot_speed_body']}")
    print("-------------------")
    # Print IMU data
    print(f"IMU - Quaternion: {imu_state['quaternion']}")
    print(f"IMU - Gyroscope: {imu_state['gyroscope']}")
    print(f"IMU - Accelerometer: {imu_state['accelerometer']}")
    print(f"IMU - RPY: {imu_state['rpy']}")
    print(f"IMU - Temperature: {imu_state['temperature']}°C")

    # Optionally, flush to ensure immediate output
    sys.stdout.flush()


async def acquire_robot_data(conn):
    """Continuously acquire robot status data."""
    def sportmodestatus_callback(message):
        current_message = message['data']
        display_data(current_message)

    conn.datachannel.pub_sub.subscribe(RTC_TOPIC['LF_SPORT_MOD_STATE'], sportmodestatus_callback)

    # Keep the program running to allow event handling
    try:
        while True:
            await asyncio.sleep(1)  # Adjust this sleep duration if necessary
    except KeyboardInterrupt:
        logging.info("Exiting gracefully...")
        sys.exit(0)