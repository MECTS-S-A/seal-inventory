from collections import defaultdict
from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(
            self,
            owner_id: str,
            websocket: WebSocket,
    ):
        await websocket.accept()

        self.active_connections[owner_id].append(websocket)

        print(
            f"[{datetime.now()}] "
            f"CONNECTED owner={owner_id} "
            f"connections={len(self.active_connections[owner_id])}"
        )

    def disconnect(
            self,
            owner_id: str,
            websocket: WebSocket,
    ):
        if owner_id not in self.active_connections:
            return

        try:
            self.active_connections[owner_id].remove(websocket)

            if not self.active_connections[owner_id]:
                del self.active_connections[owner_id]

        except ValueError:
            pass

        print(
            f"[{datetime.now()}] "
            f"DISCONNECTED owner={owner_id}"
        )

    async def send_to_owner(
            self,
            owner_id: str,
            payload: dict,
    ):
        if owner_id not in self.active_connections:
            print(
                f"Owner {owner_id} offline. "
                f"Notification not delivered."
            )
            return

        dead_connections = []

        for ws in self.active_connections[owner_id]:
            try:
                await ws.send_json(payload)

            except Exception:
                dead_connections.append(ws)

        for ws in dead_connections:
            self.disconnect(owner_id, ws)

    async def broadcast(
            self,
            payload: dict,
    ):
        for owner_id in list(self.active_connections.keys()):
            await self.send_to_owner(
                owner_id,
                payload,
            )

    def is_online(
            self,
            owner_id: str,
    ) -> bool:
        return owner_id in self.active_connections

    def online_users(self):
        return list(self.active_connections.keys())


manager = ConnectionManager()