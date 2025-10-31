from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.base import get_db
import models.sub_category as models
import schemas.sub_category as schemas

router = APIRouter(
    prefix="/sub_categories",
    tags=["sub_categories"],
)

@router.get("/", response_model=list[schemas.SubCategoryOut])
async def get_sub_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.SubCategory))
    sub_categories = result.scalars().all()
    return sub_categories

@router.get("/{sub_category_id}", response_model=schemas.SubCategoryOut)
async def get_sub_category(sub_category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.SubCategory).where(models.SubCategory.id == sub_category_id))
    sub_category = result.scalars().first()
    if not sub_category:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    return sub_category

@router.post("/", response_model=schemas.SubCategoryOut)
async def create_sub_category(sub_category: schemas.SubCategoryIn, db: AsyncSession = Depends(get_db)):
    db_sub_category = models.SubCategory(
        name=sub_category.name,
        description=sub_category.description,
        img=sub_category.img
    )
    db.add(db_sub_category)
    await db.commit()
    await db.refresh(db_sub_category)
    return db_sub_category

@router.put("/{sub_category_id}", response_model=schemas.SubCategoryOut)
async def update_sub_category(sub_category_id: int, sub_category: schemas.SubCategoryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.SubCategory).where(models.SubCategory.id == sub_category_id))
    db_sub_category = result.scalars().first()
    if not db_sub_category:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    update_data = sub_category.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sub_category, key, value)
    await db.commit()
    await db.refresh(db_sub_category)
    return db_sub_category

@router.delete("/{sub_category_id}", response_model=schemas.SubCategoryOut)
async def delete_sub_category(sub_category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.SubCategory).where(models.SubCategory.id == sub_category_id))
    db_sub_category = result.scalars().first()
    if not db_sub_category:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    await db.delete(db_sub_category)
    await db.commit()
    return db_sub_category
