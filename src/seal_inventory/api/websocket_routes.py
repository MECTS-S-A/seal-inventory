from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from seal_inventory.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws/{owner_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        owner_id: str,
):
    await manager.connect(
        owner_id,
        websocket,
    )

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(
            owner_id,
            websocket,
        )