from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from db.base import get_db
from models.user import User
from sqlalchemy.future import select

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 --- Password Hashing ---
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])  # bcrypt solo usa los primeros 72 chars

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)

# 🔑 --- JWT Token ---
def create_access_token(data: dict, expires_delta: int = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, **data}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

# 👤 --- User Authentication ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user

# 🔒 --- Role-based Access ---
def role_required(allowed_roles: list):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role_id not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker

EMPLOYEE_ROLES = [1, 2, 3, 4, 6]
CLIENT_ROLE = [5, None]

def employee_required():
    return role_required(EMPLOYEE_ROLES)

def customer_required():
    return role_required([CLIENT_ROLE])

# Permisos por rol (ajusta según tu modelo)
ROLE_PERMISSIONS = {
    1: {"read", "crud"},  # admin (super user con lectura y CRUD)
    2: {"crud"},          # mozo
    3: {"crud"},          # cocina
    4: {"crud"},          # delivery
    6: {"crud"},          # caja
    5: {"read"},          # cliente (solo lectura)
}

def _get_role_id(user) -> int:
    return user.role_id.value if hasattr(user.role_id, "value") else user.role_id

def permission_required(required: str):
    async def checker(current_user: User = Depends(get_current_user)):
        role_id = _get_role_id(current_user)
        perms = ROLE_PERMISSIONS.get(role_id, set())
        if required not in perms:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return checker
