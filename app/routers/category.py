from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from db.base import get_db
from models import category as models
from schemas import category as schemas

router = APIRouter(prefix="/category", tags=["category"])


@router.get("/", response_model=List[schemas.CategoryOut])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category))
    categories = result.scalars().all()
    return categories

@router.get("/{category_id}", response_model=schemas.CategoryOut)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category).where(models.Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=schemas.CategoryOut)
async def create_category(payload: schemas.CategoryIn, db: AsyncSession = Depends(get_db)):
    db_category = models.Category(**payload.dict())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=schemas.CategoryOut)
async def update_category(category_id: int, payload: schemas.CategoryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category).where(models.Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category).where(models.Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()
    return {"detail": "Category deleted"}