from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    created_at: str
    is_active: bool

class AuthMeResponse(UserResponse):
    jwt: str   # just for demonstration; normally we wouldn't return the token