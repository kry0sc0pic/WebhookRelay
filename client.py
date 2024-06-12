import asyncio
import websockets
import json
import requests

# WebSocket server URL
WEBSOCKET_URL = "ws://localhost:8900/ws"

# URL to send the POST request
POST_URL = "http://localhost:8000/"

async def receive_data():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        while True:
            data = await websocket.recv()
            data_json = json.loads(data)
            headers = data_json["headers"]
            body = data_json["body"]

            # Send the POST request
            try:
                response = requests.post(POST_URL, headers=headers, data=body)
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.text}")
            except Exception as e:
                print(e)


            # Handle the response as needed


asyncio.get_event_loop().run_until_complete(receive_data())