from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.user_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect_user(
            self,
            username: str,
            websocket: WebSocket,
    ):
        await websocket.accept()

        self.user_connections[username].append(
            websocket
        )

        print(f"USER CONNECTED: {username}")

    def disconnect_user(
            self,
            username: str,
            websocket: WebSocket,
    ):
        if username not in self.user_connections:
            return

        try:
            self.user_connections[username].remove(
                websocket
            )

            if not self.user_connections[username]:
                del self.user_connections[username]

        except ValueError:
            pass

    async def send_to_user(
            self,
            username: str,
            payload: dict,
    ):
        if username not in self.user_connections:
            print(
                f"User {username} offline"
            )
            return

        dead = []

        for ws in self.user_connections[username]:
            try:
                await ws.send_json(payload)

            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect_user(
                username,
                ws,
            )


manager = ConnectionManager()