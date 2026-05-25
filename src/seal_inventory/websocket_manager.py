from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(
            self,
            owner_id: str,
            websocket: WebSocket,
    ):
        await websocket.accept()

        self.active_connections[owner_id].append(
            websocket
        )

    def disconnect(
            self,
            owner_id: str,
            websocket: WebSocket,
    ):
        if owner_id in self.active_connections:
            self.active_connections[owner_id].remove(
                websocket
            )

    async def send_to_owner(
            self,
            owner_id: str,
            payload: dict,
    ):
        if owner_id not in self.active_connections:
            return

        dead_connections = []

        for ws in self.active_connections[owner_id]:
            try:
                await ws.send_json(payload)
            except Exception:
                dead_connections.append(ws)

        for ws in dead_connections:
            self.disconnect(owner_id, ws)


manager = ConnectionManager()