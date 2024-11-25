from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Dict, Any, Optional
import logging
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD
import cv2
import base64
from aiortc import MediaStreamTrack
import json


logging.basicConfig(level=logging.INFO)
#Config logging to console
logger = logging.getLogger()
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global connection instance
go2_connection: Optional[Go2WebRTCConnection] = None

# Track active WebSocket connections
active_connections: set[WebSocket] = set()

async def recv_camera_stream(track: MediaStreamTrack):
    while True:
        frame = await track.recv()
        # Convert frame to BGR format
        img = frame.to_ndarray(format="bgr24")
        # Encode frame to JPEG
        _, buffer = cv2.imencode('.jpg', img)
        # Convert to base64 string
        jpg_as_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send frame to all connected clients
        for connection in active_connections:
            try:
                await connection.send_text(jpg_as_base64)
            except:
                active_connections.remove(connection)

@app.websocket("/ws/video")
async def video_websocket(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    
    if not go2_connection:
        await websocket.close()
        return
    
    try:
        # Enable video channel if not already enabled
        go2_connection.video.switchVideoChannel(True)
        # Add callback for video frames
        go2_connection.video.add_track_callback(recv_camera_stream)
        
        # Keep connection alive until client disconnects
        try:
            while True:
                await websocket.receive_text()
        except:
            pass
        finally:
            active_connections.remove(websocket)
            
    except Exception as e:
        logging.error(f"Error in video websocket: {e}")
        await websocket.close()

@app.on_event("startup")
async def startup_event():
    global go2_connection
    try:
        go2_connection = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="192.168.2.126")
        await go2_connection.connect()
    except Exception as e:
        logging.error(f"Failed to initialize connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Go2")

@app.get("/status")
async def get_status():
    if not go2_connection:
        raise HTTPException(status_code=503, detail="Robot not connected")
    
    try:
        response = await go2_connection.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"], 
            {"api_id": 1001}
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/motion/mode/{mode}")
async def set_motion_mode(mode: str):
    if not go2_connection:
        raise HTTPException(status_code=503, detail="Robot not connected")
    
    try:
        response = await go2_connection.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"], 
            {
                "api_id": 1002,
                "parameter": {"name": mode}
            }
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/action/{command}")
async def execute_action(command: str, parameters: Dict[str, Any] = None):
    if not go2_connection:
        raise HTTPException(status_code=503, detail="Robot not connected")
    
    logging.info(f"Executing action: {command} with parameters: {parameters}")
    if command not in SPORT_CMD:
        raise HTTPException(status_code=400, detail=f"Unknown command: {command}")
    
    try:
        # Check current mode before moving
        request_data = {
            "api_id": SPORT_CMD[command]
        }
        if parameters:
            request_data["parameter"] = parameters
            
        logging.info(f"Sending command with data: {request_data}")
        response = await go2_connection.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            request_data
        )
        
        # Add a small delay between commands
        await asyncio.sleep(0.1)
        
        logging.info(f"Command response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/move")
async def move_robot(parameters: Dict[str, float]):
    if not go2_connection:
        raise HTTPException(status_code=503, detail="Robot not connected")
    
    logging.info(f"Moving robot with parameters: {parameters}")
    
    try:
        # Check current mode before moving
        mode_response = await go2_connection.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"], 
            {"api_id": 1001}
        )
        
        if mode_response['data']['header']['status']['code'] == 0:
            data = json.loads(mode_response['data']['data'])
            current_mode = data['name']
            logging.info(f"Current motion mode: {current_mode}")
            
            # Switch to normal mode if needed
            if current_mode != "normal":
                logging.info("Switching to normal mode...")
                await go2_connection.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["MOTION_SWITCHER"], 
                    {
                        "api_id": 1002,
                        "parameter": {"name": "normal"}
                    }
                )
                await asyncio.sleep(0.5)  # Reduced wait time for mode switch

        # Send move command
        response = await go2_connection.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {
                "api_id": SPORT_CMD["Move"],
                "parameter": parameters
            }
        )
        
        # Add a small delay after sending the command
        await asyncio.sleep(0.05)  # 50ms delay
        
        return response
    except Exception as e:
        logging.error(f"Error moving robot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
