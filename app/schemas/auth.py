from pydantic import BaseModel, EmailStr, constr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class LoginIn(BaseModel):
    dni: str
    password: str

class RegisterPayload(BaseModel):
    dni: str
    password: constr(min_length=6)  # mínimo 6 caracteres
    full_name: str