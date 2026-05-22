from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.connections = defaultdict(list)

    async def connect(
            self,
            site_id: str,
            websocket: WebSocket,
    ):
        await websocket.accept()

        self.connections[site_id].append(
            websocket
        )

    def disconnect(
            self,
            site_id: str,
            websocket: WebSocket,
    ):
        if websocket in self.connections[site_id]:
            self.connections[site_id].remove(
                websocket
            )

    async def send_to_site(
            self,
            site_id,
            message,
    ):
        for ws in self.connections.get(site_id, []):
            await ws.send_json(message)


manager = ConnectionManager()