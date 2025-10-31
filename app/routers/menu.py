from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from db.base import get_db
from models import menu as models
from schemas import menu as schemas
from routers.ws_menu import broadcast_menu_update

router = APIRouter(prefix="/menu", tags=["menu"])

active_connections: List[WebSocket] = []
# ------------------------
# Obtener todos los ítems
@router.get("/", response_model=List[schemas.MenuItemOut])
async def get_menu_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MenuItem))
    items = result.scalars().all()
    return items

@router.websocket("/ws/menu")
async def websocket_menu(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print("🟢 Cliente conectado al WebSocket de menú")

    try:
        while True:
            # Puedes recibir mensajes si el cliente envía algo, pero aquí solo escuchamos
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("🔴 Cliente desconectado")
# ------------------------
# Obtener ítem por ID
@router.get("/{item_id}", response_model=schemas.MenuItemOut)
async def get_menu_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MenuItem).where(models.MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@router.post("/", response_model=schemas.MenuItemOut)
async def create_menu_item(
    payload: schemas.MenuItemCreate,
    db: AsyncSession = Depends(get_db),
):
    db_item = models.MenuItem(**payload.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    # Notificar creación
    await broadcast_menu_update({
        "type": "menu_created",
        "item": {
            "id": db_item.id,
            "name": db_item.name,
            "price": float(db_item.price) if db_item.price is not None else None,
            "category": db_item.category,
            "amount": db_item.amount,
            "available": db_item.available,
        }
    })
    return db_item

# ------------------------
# Actualizar ítem
@router.put("/{item_id}", response_model=schemas.MenuItemOut)
async def update_menu_item(item_id: int, payload: schemas.MenuItemUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MenuItem).where(models.MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for k, v in payload.dict(exclude_unset=True).items():
        setattr(item, k, v)

    await db.commit()
    await db.refresh(item)
    # Notificar actualización
    await broadcast_menu_update({
        "type": "menu_updated",
        "item": {
            "id": item.id,
            "name": item.name,
            "price": float(item.price) if item.price is not None else None,
            "category": item.category,
            "amount": item.amount,
            "available": item.available,
        }
    })
    return item

@router.delete("/{item_id}")
async def delete_menu_item(item_id: int, payload: schemas.MenuItemUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MenuItem).where(models.MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()
    # Notificar eliminación
    await broadcast_menu_update({
        "type": "menu_deleted",
        "item_id": item_id
    })
    return {"ok": True}


async def broadcast_menu(db: AsyncSession):
    """Envia el menú actualizado a todos los clientes conectados"""
    result = await db.execute(select(MenuItem))
    items = result.scalars().all()

    data = [
        {
            "id": i.id,
            "name": i.name,
            "price": i.price,
            "available": i.available,
            "amount": i.amount,
            "category": i.category,
            "image_url": i.image_url,
        }
        for i in items
    ]

    # Enviar a todos los conectados
    for conn in active_connections:
        await conn.send_text(json.dumps({"type": "menu_update", "data": data}))