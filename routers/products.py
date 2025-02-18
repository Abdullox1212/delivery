from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Product, User
from schemas import ProductCreate, ProductResponse
from utils import get_current_user  # auth.py dan chaqiramiz

router = APIRouter(prefix="/products", tags=["Products"])

# ✅ Oddiy userlar ham mahsulotlarni ko‘ra oladi
@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# ✅ Faqat admin mahsulot qo‘shishi mumkin
@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:  # Faqat adminlar ruxsat
        raise HTTPException(status_code=403, detail="Faqat admin yaratishi mumkin")
    
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product
