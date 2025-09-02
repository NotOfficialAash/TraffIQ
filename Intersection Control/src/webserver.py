"""
================================================================================
Project: Smart Traffic and Accident Monitoring System
File: webserver.py
Author(s): Aashrith Srinivasa.
License: See LICENSE file in the repository for full terms.
Description:
    WebSocket server for the traffic and accident monitoring system. 
    Streams raw camera frames to the frontend and handles 
    start/stop control messages.
================================================================================
"""


import cv2
import json
import base64
import asyncio
import websockets
import logging as log


streaming_enabled = False
latest_frame = None
frame_interval = 0.05


async def vhandler(websocket):
    global streaming_enabled, latest_frame
    log.info("Websocket Client Connected")

    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "start_video":
                streaming_enabled = True
                log.info("Streaming Started to Client")

                await websocket.send(json.dumps({"status" : "streaming started"}))


                while streaming_enabled and websocket.state == websockets.protocol.State.OPEN:
                    if latest_frame is not None:
                        _, buffer = cv2.imencode(".jpg", latest_frame)
                        frame_b64 = base64.b64encode(buffer).decode("utf-8")

                        await websocket.send(json.dumps({"type": "video_frame", "frame": frame_b64}))

                    await asyncio.sleep(frame_interval)

            elif msg_type == "stop_video":
                streaming_enabled = False
                log.info("Streaming Stopped to Client")
                await websocket.send(json.dumps({"status": "streaming stopped"}))

    except websockets.exceptions.ConnectionClosed:
        log.error("Websocket Connection Closed")
    
    except Exception as e:
        log.exception("Unexpected Exception Occured")

    finally:
        streaming_enabled = False
        log.info("Client Disconnected. Stopped Streaming")


def run(host, port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def start():
        server = await websockets.serve(vhandler, host, port)
        log.info("Websocket Started")
        return server
    
    server = loop.run_until_complete(start())

    try:
        loop.run_forever()

    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
