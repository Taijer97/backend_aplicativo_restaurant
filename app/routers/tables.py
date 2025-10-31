from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from db.base import get_db
from models import table as models
from schemas import table as schemas

router = APIRouter(prefix="/tables", tags=["tables"])

@router.post("/", response_model=schemas.TableOut)
async def create_table(table: schemas.TableOut, db: AsyncSession = Depends(get_db)):
    db_table = models.Table(**table.dict())
    db.add(db_table)
    await db.commit()
    await db.refresh(db_table)
    return db_table

@router.get("/", response_model=List[schemas.TableOut])
async def get_tables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Table))
    tables = result.scalars().all()
    return tables

@router.put("/{table_id}", response_model=schemas.TableOut)
async def update_table(table_id: int, payload: schemas.TableOut, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Table).where(models.Table.id == table_id))
    db_table = result.scalars().first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(db_table, key, value)
    await db.commit()
    await db.refresh(db_table)
    return db_table

@router.delete("/{table_id}")
async def delete_table(table_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Table).where(models.Table.id == table_id))
    db_table = result.scalars().first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    await db.delete(db_table)
    await db.commit()
    return {"detail": "Table deleted"}
