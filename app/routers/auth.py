from re import I
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User
from schemas.user import UserCreate, UserOut, UserFull
from schemas.auth import LoginIn, TokenResponse
from db.base import get_db
from core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Mantener el mismo endpoint, pero agregar validación de roles

EMPLOYEE_ROLES = [1, 2, 3, 4, 6]
CLIENT_ROLE = 5

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    if payload.role_id not in EMPLOYEE_ROLES + [CLIENT_ROLE]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    print(payload)
    if payload.email:
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalars().first()
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Truncar la contraseña a 72 caracteres si existe
    password_to_hash = payload.password[:72] if payload.password else None
    print(password_to_hash)
    new_user = User(
        dni=payload.dni,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=get_password_hash(password_to_hash) if password_to_hash else None,
        role_id=payload.role_id
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    token = create_access_token({
        "user_id": new_user.id,
        "role": new_user.role_id.value if hasattr(new_user.role_id, 'value') else new_user.role_id
    })
    
    return TokenResponse(access_token=token, token_type="bearer")
    
@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.dni == payload.dni))
    user = result.scalars().first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"user_id": user.id, "role": user.role_id.value if hasattr(user.role_id, 'value') else user.role_id})
    return {"access_token": token, "token_type": "bearer"}
