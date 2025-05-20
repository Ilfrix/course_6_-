from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None

class OrderItemCreate(BaseModel):
    pizza_name: str
    quantity: int
    price: float

class OrderItemResponse(OrderItemCreate):
    id: int
    order_id: int

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    order_hash: str
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True

class OrderWithItems(BaseModel):
    id: int
    user_id: int
    status: str
    order_hash: str
    items: List[OrderItemResponse]
    
    class Config:
        orm_mode = True