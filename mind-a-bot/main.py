from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging
import yaml
import uvicorn
import asyncio
from utils.webrtc_conn import WebRTCConnectionHandler
from data_acquisition.robot_data import acquire_robot_data  # Import the new function
from contextlib import asynccontextmanager

# LOAD YAML CONFIG
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)
config = load_config()


# CONFIGURE LOGGING
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CONSTANTS
app = FastAPI()
conn_handler = WebRTCConnectionHandler()

class ControlRequest(BaseModel):
    rtc_topic: str
    api_id: int
    optional_param: Optional[str] = None  # Optional parameter if needed


@asynccontextmanager
async def lifespan():
    # Connect to the robot in the background
    await conn_handler.connect()
    await asyncio.create_task(acquire_robot_data(conn_handler.connection))
    yield
    await conn_handler.connection.close()


@app.post("/control")
async def control_robot(control_request: ControlRequest):
    logging.info(f"Received control request: {control_request}")

    # Access the configuration values
    robot_ip = config['robot']['ip']
    webrtc_method = config['robot']['webrtc_connection_method']

    # Log the robot IP and WebRTC connection method
    logging.info(f"Robot IP: {robot_ip}, WebRTC Method: {webrtc_method}")

    # Here you would typically publish the command to the robot
    # For now, we'll just log the request
    response = {
        "rtc_topic": control_request.rtc_topic,
        "api_id": control_request.api_id,
        "optional_param": control_request.optional_param
    }
    if not control_request.optional_param:
        response.pop("optional_param")

    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
