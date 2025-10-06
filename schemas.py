from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    name: str
    email: str
    password: str
    activated: Optional[bool]
    admin: Optional[bool]
    
    class Config:
        from_attributes = True
        
class OrderSchema(BaseModel):
    user_id: int
    
    class Config:
        from_attributes = True
        
class LoginSchema(BaseModel):
    email: str
    password: str
    
    class Config:
        from_attributes = True
    
class OrderItemSchema(BaseModel):
    quantity: int
    flavor: str
    size: int
    unit_price: float
    
    class Config:
        from_attributes = True
        

class ResponseOrderSchema(BaseModel):
    id: int
    status: str
    price: float
    
    class Config:
        from_attributes = True
