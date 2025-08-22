import asyncio
import websockets
import json
import cv2
import base64
import time

def detect_accident():
    # Simulating accident detection logic
    return True

last_notification_time = 0

async def process_video_stream(websocket):
    global last_notification_time
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
        
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
                
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode()
            
            # Send frame
            await websocket.send(json.dumps({
                "type": "video_frame",
                "frame": jpg_as_text
            }))
            
            # Check for accident and send notification every 10 seconds
            current_time = time.time()
            if detect_accident() and current_time - last_notification_time >= 10:
                await websocket.send(json.dumps({
                    "type": "notification",
                    "message": "Accident detected! Click to view details."
                }))
                last_notification_time = current_time
            
            await asyncio.sleep(0.033)  # ~30 FPS
            
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        cap.release()
        print("Camera released")

async def main():
    async with websockets.serve(process_video_stream, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")