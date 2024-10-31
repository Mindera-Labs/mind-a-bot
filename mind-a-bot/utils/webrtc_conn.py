import logging
import yaml
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod


class WebRTCConnectionHandler:
    def __init__(self, config_file='config.yaml'):
        self.config = self.load_config(config_file)
        self.connection = self.create_connection()

    @staticmethod
    def load_config(config_file):
        """Load configuration from a YAML file."""
        with open(config_file, "r") as file:
            return yaml.safe_load(file)

    def create_connection(self):
        """Create and return a WebRTC connection based on the configuration."""
        connection_method = WebRTCConnectionMethod[self.config['robot']['webrtc_connection_method']]
        robot_ip = self.config['robot']['ip']

        try:
            conn = Go2WebRTCConnection(connection_method, ip=robot_ip)
            return conn
        except Exception as e:
            logging.error(f"Failed to create WebRTC connection: {e}")
            raise

    async def connect(self):
        """Connect to the Go2 robot."""
        try:
            await self.connection.connect()
            logging.info(
                f"Connected to robot at {self.config['robot']['ip']} using connection method {self.config['robot']['webrtc_connection_method']}.")
        except Exception as e:
            logging.error(f"Error during connection: {e}")
            raise

    # handle connection closing
    async def close(self):
        """Close the WebRTC connection."""
        await self.connection.disconnect()
        logging.info("Connection closed.")

# Example of usage (commented out, can be used for testing this module)
# if __name__ == "__main__":
#     conn_handler = WebRTCConnectionHandler()
#     asyncio.run(conn_handler.connect())