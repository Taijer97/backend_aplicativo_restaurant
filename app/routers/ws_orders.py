# app/routers/ws_orders.py
from fastapi import APIRouter, WebSocket
from typing import List

router = APIRouter()
connected_clients: List[WebSocket] = []

@router.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # data: {"order_id": 1, "status": "preparing"}
            for client in connected_clients:
                if client != websocket:
                    await client.send_json(data)
    except Exception:
        connected_clients.remove(websocket)
