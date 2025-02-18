from pydantic import BaseModel, EmailStr
from typing import Optional

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# --- Order Schemas ---
class OrderBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    total_price: float

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    total_price: Optional[float] = None
    address: str

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_price: float
    address: str
    delivered: bool  # 👈 Orderning holati

    class Config:
        orm_mode = True