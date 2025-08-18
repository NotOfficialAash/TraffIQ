import asyncio
import websockets
import json

async def handle_signal_change(data):
    # Process the signal change
    intersection_id = data['intersectionId']
    signal_id = data['signalId']
    new_state = data['newState']
    coordinates = data['coordinates']
    
    print(f"Changing signal {signal_id} at intersection {intersection_id} to {new_state}")
    print(f"Location: {coordinates}")
    
    # Add your signal control logic here
    # e.g., send commands to actual traffic signals

async def handle_websocket(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'signal_change':
                await handle_signal_change(data['data'])
                
                # Send confirmation back to client
                await websocket.send(json.dumps({
                    "type": "signal_update_confirmation",
                    "status": "success",
                    "intersectionId": data['data']['intersectionId'],
                    "signalId": data['data']['signalId']
                }))
    
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    async with websockets.serve(handle_websocket, "localhost", 8765):
        print("Signal control server started on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")