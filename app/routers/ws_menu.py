from fastapi import APIRouter, WebSocket
from typing import List
from jose import jwt, JWTError
import os

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

router = APIRouter()
connected_menu_clients: List[WebSocket] = []

async def broadcast_menu_update(data: dict):
    for client in list(connected_menu_clients):
        try:
            await client.send_json(data)
        except Exception:
            try:
                await client.close()
            except Exception:
                pass
            if client in connected_menu_clients:
                connected_menu_clients.remove(client)

@router.websocket("/ws/menu")
async def websocket_menu(websocket: WebSocket):
    # Token opcional por query param: ?token=<JWT>
    token = websocket.query_params.get("token")
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if not payload.get("user_id"):
                await websocket.close(code=4401)
                return
        except JWTError:
            await websocket.close(code=4401)
            return

    await websocket.accept()
    connected_menu_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # echo/broadcast de mensajes entrantes
            for client in connected_menu_clients:
                if client != websocket:
                    await client.send_json(data)
    except Exception:
        if websocket in connected_menu_clients:
            connected_menu_clients.remove(websocket)