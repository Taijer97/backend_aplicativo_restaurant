from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from db.base import get_db
from models.order import Order
from schemas.order import OrderOut, CreateOrderIn

router = APIRouter(prefix="/orders", tags=["orders"])

connected_clients: List[WebSocket] = []

@router.post("/", response_model=OrderOut)
async def create_order(payload: CreateOrderIn, db: AsyncSession = Depends(get_db)):
    db_order = Order(
        table_id=None,  # Opcional, si viene table_code luego buscar table_id
        status="pending",
        total=sum([item.quantity * 0 for item in payload.items])  # calcular total según menú
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderOut])
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    return orders

# ------------------------
# WebSocket de pedidos en tiempo real
@router.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            for client in connected_clients:
                if client != websocket:
                    await client.send_json(data)
    except Exception:
        connected_clients.remove(websocket)
