from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.stream_manager import stream_manager

router = APIRouter()


@router.websocket("/stream")
async def stream(ws: WebSocket) -> None:
    await stream_manager.connect(ws)
    try:
        while True:
            # Keep the connection alive; accept client pings/messages.
            await ws.receive_text()
    except WebSocketDisconnect:
        await stream_manager.disconnect(ws)
