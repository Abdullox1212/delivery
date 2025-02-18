from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Category, User
from schemas import CategoryCreate, CategoryResponse
from utils import get_current_user  # auth.py dan chaqiramiz

router = APIRouter(prefix="/categories", tags=["Categories"])

# ✅ Oddiy userlar ham ko‘ra oladi
@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

# ✅ Faqat admin kategoriya qo‘shishi mumkin
@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:  # Faqat adminlar ruxsat
        raise HTTPException(status_code=403, detail="Faqat admin yaratishi mumkin")
    
    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category
