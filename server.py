import json

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
import threading
import os

app = FastAPI()


class WebSocketManager:
    def __init__(self):
        self._websockets = []
        self._lock = threading.Lock()

    def add(self, websocket):
        with self._lock:
            self._websockets.append(websocket)

    async def send(self, message):
        with self._lock:
            for s in self._websockets:
                await s.send_json(message)

    def remove(self, websocket):
        with self._lock:
            self._websockets.remove(websocket)


manager = WebSocketManager()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Example</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&display=swap" rel="stylesheet">
    </head>
    <style>
    .bricolage-grotesque{
  font-family: "Bricolage Grotesque", sans-serif;
  font-optical-sizing: auto;
  font-weight: 700;
  font-size: 100px;
  font-style: normal;
  font-variation-settings:
    "wdth" 100;
}</style>
    <body class="bricolage-grotesque">
        Webhook Relay
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        manager.add(websocket)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.remove(websocket)


@app.post("/send")
async def send_data(request: Request):
    headers = dict(request.headers)
    body = await request.body()
    data = {
        "headers": headers,
        "body": body.decode()
    }
    await manager.send(data)
    return {"message": "Data sent over WebSocket"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8900)))
