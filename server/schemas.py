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
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True


class OrderWithItems(BaseModel):
    id: int
    user_id: int
    status: str
    items: List[OrderItemResponse]
    
    class Config:
        orm_mode = True


# class OrderItem(Base):
#     __tablename__ = "order_items"

#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(Integer, ForeignKey("orders.id"))
#     pizza_name = Column(String)
#     quantity = Column(Integer)
#     price = Column(Float)