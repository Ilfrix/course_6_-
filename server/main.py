from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from database import SessionLocal, engine
import models
import schemas
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройки для JWT
SECRET_KEY = "SuperPizzeria"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 45

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Лучше поправить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функции для работы с паролями и токенами
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=45)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    
    refresh_token = str(uuid.uuid4())
    
    db = SessionLocal()
    try:
        db_refresh_token = models.RefreshToken(
            user_id=user_id,
            token=refresh_token,
            expires_at=expire
        )
        db.add(db_refresh_token)
        db.commit()
        db.refresh(db_refresh_token)
    finally:
        db.close()
    
    return refresh_token

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:

        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=1)
    refresh_token = create_refresh_token(user.id, refresh_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@app.post("/refresh-token", response_model=schemas.Token)
async def refresh_access_token(request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    db_refresh_token = db.query(models.RefreshToken)\
                         .filter(models.RefreshToken.token == request.refresh_token)\
                         .first()
    if not db_refresh_token or db_refresh_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Генерируем новые токены
    new_access_token = create_access_token(
        data={"sub": str(db_refresh_token.user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Создаем новый refresh-токен
    new_refresh_token = create_refresh_token(db_refresh_token.user_id, timedelta(days=1))
    
    # Удаляем старый токен
    db.delete(db_refresh_token)
    db.commit()
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }

@app.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.get("/menu")
async def get_menu():
    return [
        {"id": 1, "name": "Маргарита", "price": 350, "description": "Томатный соус, моцарелла, базилик"},
        {"id": 2, "name": "Пепперони", "price": 450, "description": "Томатный соус, моцарелла, пепперони"},
        {"id": 3, "name": "Гавайская", "price": 400, "description": "Томатный соус, моцарелла, курица, ананас"},
        {"id": 4, "name": "Четыре сыра", "price": 500, "description": "Сливочный соус, моцарелла, пармезан, дор блю, чеддер"},
    ]


@app.post("/orders/", response_model=schemas.OrderWithItems)
async def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        order_hash = str(uuid.uuid4())
        db_order = models.Order(
            user_id=current_user.id,
            order_hash=order_hash
        )
        db.add(db_order)
        db.flush()
        order_items = []
        
        # Добавляем товары в заказ
        for item in order.items:
            db_item = models.OrderItem(
                order_id=db_order.id,
                pizza_name=item.pizza_name,
                quantity=item.quantity,
                price=item.price
            )
            db.add(db_item)
            order_items.append(db_item)
        
        db.commit()
        db.refresh(db_order)
        
        return {
            "id": db_order.id,
            "user_id": db_order.user_id,
            "status": db_order.status,
            "order_hash": db_order.order_hash,
            "items": order_items
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/", response_model=List[schemas.OrderWithItems])
async def read_user_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    orders = db.query(models.Order)\
               .filter(models.Order.user_id == current_user.id)\
               .order_by(models.Order.id.desc())\
               .all()
    
    result = []
    for order in orders:
        items = db.query(models.OrderItem)\
                 .filter(models.OrderItem.order_id == order.id)\
                 .all()
        
        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "order_hash": order.order_hash,
            "items": items
        })
    
    return result

@app.delete("/order-items/{item_id}")
async def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Удаление/уменьшение количества позиции в заказе с проверкой на пустой заказ
    db_item = db.query(models.OrderItem)\
                .join(models.Order)\
                .filter(models.OrderItem.id == item_id)\
                .first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    order_id = db_item.order_id
    
    if db_item.quantity > 1:
        db_item.quantity -= 1
        db.commit()
        db.refresh(db_item)
        message = "Quantity decreased"
    else:
        db.delete(db_item)
        db.commit()
        message = "Item removed"
        
        # Проверяем, остались ли еще позиции в заказе
        remaining_items = db.query(models.OrderItem)\
                          .filter(models.OrderItem.order_id == order_id)\
                          .count()
        
        if remaining_items == 0:
            # Если позиций не осталось - удаляем весь заказ
            db.query(models.Order)\
              .filter(models.Order.id == order_id)\
              .delete()
            db.commit()
            message = "Item removed and order deleted as it became empty"
    
    return {"message": message}