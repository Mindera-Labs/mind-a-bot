import asyncio
import logging
import json
import sys
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD

# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)


async def main():
    try:
        # Choose a connection method (uncomment the correct one)
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="192.168.2.126")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, serialNumber="B42D2000XXXXXXXX")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.Remote, serialNumber="B42D2000XXXXXXXX", username="email@gmail.com", password="pass")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)

        # Connect to the WebRTC service.
        await conn.connect()

        # # Set Volume to 10%
        # print("Setting volume to 10% (1/10)...")
        # await conn.datachannel.pub_sub.publish_request_new(
        #     RTC_TOPIC["VUI"],
        #     {
        #         "api_id": 1003,
        #         "parameter": {"volume": 1}
        #     }
        # )
        # await asyncio.sleep(5)


        ####### NORMAL MODE ########
        print("Checking current motion mode...")

        # Get the current motion_switcher status
        response = await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"],
            {"api_id": 1001}
        )

        if response['data']['header']['status']['code'] == 0:
            data = json.loads(response['data']['data'])
            current_motion_switcher_mode = data['name']
            print(f"Current motion mode: {current_motion_switcher_mode}")

        # Switch to "normal" mode if not already
        if current_motion_switcher_mode != "normal":
            print(f"Switching motion mode from {current_motion_switcher_mode} to 'normal'...")
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORTS_MOD"],
                {
                    "api_id": 1002,
                    "parameter": {"name": "normal"}
                }
            )
            await asyncio.sleep(5)  # Wait while it stands up


        # Perform a "Move Forward" movement
        print("Moving forward...")
        data_points = []
        for i in range(30):
            # Generate or compute the parameters for each data point
            # Here, we're incrementing tFromStart by 1.0 each time as an example
            data_point = {
                "t_from_start": 1 * (i + 1),  # e.g., 1.0, 2.0, ..., 30.0
                "x": 0.1 * (i + 1),  # Example: Increment x by 1.0 each step
                "y": 0.0 * (i + 1),  # Example: Increment y by 1.0 each step
                "yaw": 0.0 * (i + 1),  # Example: Increment yaw by 1.0 each step
                "vx": 1.0,  # Velocity in x (constant)
                "vy": 1.0,  # Velocity in y (constant)
                "vyaw": 0.0  # Yaw rate (constant)
            }
            data_points.append(data_point)

        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"],
            {
                "api_id": SPORT_CMD["TrajectoryFollow"],
                "parameter": data_points
            }
        )

        """
         def TrajectoryFollow(self, path: list):
        l = len(path)
        if l != SPORT_PATH_POINT_SIZE:
            return SPORT_ERR_CLIENT_POINT_PATH

        path_p = []
        for i in range(l):
            point = path[i]
            p = {}
            p["t_from_start"] = point.timeFromStart
            p["x"] = point.x
            p["y"] = point.y
            p["yaw"] = point.yaw
            p["vx"] = point.vx
            p["vy"] = point.vy
            p["vyaw"] = point.vyaw
            path_p.append(p)
            
        parameter = json.dumps(path_p)
        code = self._CallNoReply(SPORT_API_ID_TRAJECTORYFOLLOW, parameter)
        return code
        {
              float tFromStart; // Time at which the path point is located
              float x; //x position
              float y; //y position
              float yaw; // Yaw angle
              float vx; //x speed
              float vy; //y speed
              float vyaw; // Yaw speed
            } PathPoint;"""

        await asyncio.sleep(30)



    except ValueError as e:
        # Log any value errors that occur during the process.
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C to exit gracefully.
        print("\nProgram interrupted by user")
        sys.exit(0)