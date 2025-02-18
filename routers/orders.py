# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database import get_db
# from models import Order, User, Product
# from schemas import OrderCreate, OrderResponse
# from utils import get_current_user
# import requests
# from fastapi import BackgroundTasks
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# router = APIRouter(prefix="/orders", tags=["Orders"])

# BOT_TOKEN = "7468217626:AAEI6PsD5wjUlXlRDcdftxi2vnn9udebj80"
# CHAT_ID = "7149602547"

# FASTAPI_URL = "http://127.0.0.1:8000/update_delivery"

# @router.post("/", response_model=OrderResponse)
# def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     product = db.query(Product).filter(Product.id == order.product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

#     total_price = order.total_price if order.total_price else product.price * order.quantity  # 👈 Avtomatik hisoblash

#     new_order = Order(
#         user_id=current_user.id,  # Hozircha 1, lekin auth qo'shilgandan keyin dinamik bo'ladi
#         product_id=product.id,
#         quantity=order.quantity,
#         total_price=total_price,
#         address=order.address
#     )
#     db.add(new_order)
#     db.commit()
#     db.refresh(new_order)

#     # 📩 **Telegram botga xabar yuborish**
#     message = f"""📦 Yangi buyurtma!
# 🆔 Order ID: {new_order.id}
# 📍 Manzil: {new_order.address}
# 📦 Mahsulot : {product.name}
# 📏 Miqdor: {new_order.quantity}
# 💰 Narxi: {new_order.total_price} so‘m
# 🚚 Yetkazib berildimi?"""

#     # Inline button
#     keyboard = InlineKeyboardMarkup().add(
#         InlineKeyboardButton("✅ Yetkazib berdik!", url=f"{FASTAPI_URL}/{new_order.id}")
#     )

#     telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     data = {
#         "chat_id": CHAT_ID,
#         "text": message,
#         "reply_markup": keyboard
#     }
#     requests.post(telegram_url, json=data)  # Telegramga xabar yuborish
    

#     return new_order



# @router.post("/update_delivery/{order_id}")
# def update_delivery(order_id: int, db: Session = Depends(get_db)):
#     order = db.query(Order).filter(Order.id == order_id).first()
    
#     if not order:
#         return {"error": "Order not found!"}

#     order.delivered = True  # ✅ Yetkazib berildi deb belgilaymiz
#     db.commit()

#     # 📨 **Telegramdagi eski xabarni yangilash**
#     message = f"✅ Buyurtma #{order.id} yetkazildi!"
#     telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     data = {
#         "chat_id": CHAT_ID,
#         "text": message
#     }
#     requests.post(telegram_url, json=data)

#     return {"success": "Order delivered!"}




# @router.get("/", response_model=list[OrderResponse])
# def get_orders(db: Session = Depends(get_db)):
#     return db.query(Order).all()



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, User, Product
from schemas import OrderCreate, OrderResponse
from utils import get_current_user
import requests

router = APIRouter(prefix="/orders", tags=["Orders"])

BOT_TOKEN = "7468217626:AAEI6PsD5wjUlXlRDcdftxi2vnn9udebj80"
CHAT_ID = "7149602547"
FASTAPI_URL = "http://127.0.0.1:8000/orders/update_delivery"

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    total_price = order.total_price if order.total_price else product.price * order.quantity

    new_order = Order(
        user_id=current_user.id,
        product_id=product.id,
        quantity=order.quantity,
        total_price=total_price,
        address=order.address
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 📩 Telegram botga xabar yuborish
    message = f"""
📦 Yangi buyurtma!
🆔 Order ID: {new_order.id}
📍 Manzil: {new_order.address}
📦 Mahsulot: {product.name}
📏 Miqdor: {new_order.quantity}
💰 Narxi: {new_order.total_price} so‘m
🚚 Yetkazib berildimi?"""

    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Yetkazib berdik!", "url": f"{FASTAPI_URL}/{new_order.id}"}
        ]]
    }

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "reply_markup": keyboard
    }
    response = requests.post(telegram_url, json=data)

    # ✅ Xabarning ID sini olish va bazaga saqlash
    message_data = response.json()
    message_id = message_data.get("result", {}).get("message_id")
    if message_id:
        new_order.message_id = message_id  # Order modeliga saqlaymiz
        db.commit()  # 🔄 Yangilash

    return new_order


@router.get("/update_delivery/{order_id}")
def update_delivery(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        return {"error": "Order not found!"}

    order.delivered = True
    db.commit()

    # 🛑 Xabarni o‘chirish uchun message_id ni olish
    if order.message_id:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
        data = {
            "chat_id": CHAT_ID,
            "message_id": order.message_id
        }
        requests.post(telegram_url, json=data)

    # ✅ Buyurtma yetkazilganligi haqida yangi xabar yuborish
    message = f"✅ Buyurtma #{order.id} yetkazildi!"
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(telegram_url, json=data)

    return {"success": "Order delivered!"}


@router.get("/", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()
