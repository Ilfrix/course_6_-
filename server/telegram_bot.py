import logging
from typing import Dict, List
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
import schemas

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./pizzeria.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_order_info(order_hash: str) -> Dict:
    db = next(get_db())
    
    order = db.query(models.Order)\
             .filter(models.Order.order_hash == order_hash)\
             .first()
    
    if not order:
        return None
    
    items = db.query(models.OrderItem)\
             .filter(models.OrderItem.order_id == order.id)\
             .all()
    
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "items": [{"id": item.id, 
                   "order_id": item.order_id, 
                   "pizza_name": item.pizza_name, 
                   "quantity": item.quantity, 
                   "price": item.price} 
                   for item in items]
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Отправь мне Уникальный номер заказа, и я покажу информацию о нём.\n'
        'Например, отправь: 5fc32595-e919-4cad-804d-ced3038942b4'
    )

async def handle_order_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        
        order_hash = str(update.message.text)
        order_info = await get_order_info(order_hash)
        
        if order_info:
            items_text = "\n".join(
                f"  - Товар: {item['pizza_name']}, Количество: {item['quantity']}"
                for item in order_info["items"]
            )
            response = (
                f"Заказ ID: {order_info['id']}\n"
                f"Статус: {order_info['status']}\n"
                f"Товары:\n{items_text}"
            )
        else:
            response = "Заказ не найден или у вас нет к нему доступа."
            
        await update.message.reply_text(response)
    except ValueError:
        await update.message.reply_text("Пожалуйста, отправьте корректный ID заказа (число).")

def main() -> None:
    application = Application.builder().token("5994362789:AAG46EnxLhtgbwV3v9uymwn365bj0L1VmYI").build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_id))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()