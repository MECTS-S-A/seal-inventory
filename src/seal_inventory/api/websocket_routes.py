from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from seal_inventory.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws/{username}")
async def websocket_endpoint(
        websocket: WebSocket,
        username: str,
):
    await manager.connect_user(
        username,
        websocket,
    )

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect_user(
            username,
            websocket,
        )