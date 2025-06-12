import os
from hypothesis import given, strategies as st, settings, HealthCheck
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
from database import SessionLocal, engine
import models
from main import app
from jose import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

@pytest.fixture(scope="function")
def db():
    db = SessionLocal()
    try:
        # Очищаем все таблицы перед тестом
        db.query(models.OrderItem).delete()
        db.query(models.Order).delete()
        db.query(models.RefreshToken).delete()
        db.query(models.User).delete()
        db.commit()
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def text_without_null_bytes(min_size=1, max_size=100) -> st.SearchStrategy[str]:
    return st.text(
        min_size=min_size,
        max_size=max_size,
        alphabet=st.characters(
            codec='utf-8',
            exclude_characters=['\x00']
        )
    )

def user_strategy() -> st.SearchStrategy[Dict[str, Any]]:
    email_strategy = st.emails().map(lambda x: f"{uuid.uuid4().hex[:8]}_{x}")
    return st.fixed_dictionaries({
        "username": text_without_null_bytes(min_size=8, max_size=100),
        "password": text_without_null_bytes(min_size=8, max_size=100),
        "email": email_strategy,
        "full_name": text_without_null_bytes(min_size=2, max_size=100)
    })

def order_item_strategy() -> st.SearchStrategy[Dict[str, Any]]:
    return st.fixed_dictionaries({
        "pizza_name": st.sampled_from(["Маргарита", "Пепперони", "Гавайская", "Четыре сыра"]),
        "quantity": st.integers(min_value=1, max_value=10),
        "price": st.integers(min_value=300, max_value=1000)
    })

def order_strategy() -> st.SearchStrategy[Dict[str, Any]]:
    return st.fixed_dictionaries({
        "items": st.lists(order_item_strategy(), min_size=1, max_size=10)
    })

def create_test_user(db: Session) -> models.User:
    test_user = models.User(
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        full_name="Test User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    db.add(test_user)
    db.commit()
    return test_user

def get_auth_headers(client: TestClient, db: Session) -> Dict[str, str]:
    user = create_test_user(db)
    token_response = client.post("/token", data={
        "username": user.username,
        "password": "secret",
        "grant_type": "password"
    })
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Тесты
@given(user_data=user_strategy())
@settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=500)
def test_fuzz_register(client, user_data: Dict[str, Any]):
    response = client.post("/register", json=user_data)
    assert response.status_code in (200, 400, 422)

@given(
    username=text_without_null_bytes(min_size=2),
    password=text_without_null_bytes(min_size=2)
)
@settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_fuzz_login(client, username: str, password: str, db: Session):
    test_user = create_test_user(db)
    
    response = client.post("/token", data={
        "username": username,
        "password": password,
        "grant_type": "password"
    })
    assert response.status_code in (200, 401)

@given(token=st.text(min_size=10).filter(lambda x: '\x00' not in x))
@settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_fuzz_refresh_token(client, token: str, db: Session):
    test_user = create_test_user(db)
    valid_token = str(uuid.uuid4())

    db_refresh_token = models.RefreshToken(
        user_id=test_user.id,
        token=valid_token,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    db.add(db_refresh_token)
    db.commit()

    response = client.post("/refresh-token", json={"refresh_token": token})
    assert response.status_code in (200, 401)

@given(order_data=order_strategy())
@settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=500)
def test_fuzz_create_order(client, order_data: Dict[str, Any], db: Session):
    headers = get_auth_headers(client, db)
    response = client.post("/orders/", json=order_data, headers=headers)
    assert response.status_code in (200, 400, 422)

def test_fuzz_get_orders(client, db: Session):
    headers = get_auth_headers(client, db)
    
    user = create_test_user(db)
    for _ in range(3):
        order = models.Order(user_id=user.id, order_hash=str(uuid.uuid4()))
        db.add(order)
        db.flush()
        db.add(models.OrderItem(
            order_id=order.id,
            pizza_name="Маргарита",
            quantity=1,
            price=350
        ))
    db.commit()
    
    response = client.get("/orders/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@given(item_id=st.integers())
@settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=500)
def test_fuzz_delete_order_item(client, item_id: int, db: Session):
    headers = get_auth_headers(client, db)
    
    user = create_test_user(db)
    order = models.Order(user_id=user.id, order_hash=str(uuid.uuid4()))
    db.add(order)
    db.flush()
    db_item = models.OrderItem(
        order_id=order.id,
        pizza_name="Маргарита",
        quantity=2,
        price=350
    )
    db.add(db_item)
    db.commit()
    
    response = client.delete(f"/order-items/{item_id}", headers=headers)
    assert response.status_code in (200, 404)

def test_fuzz_get_current_user(client, db: Session):
    headers = get_auth_headers(client, db)
    response = client.get("/users/me/", headers=headers)
    assert response.status_code == 200
    assert "username" in response.json()

def test_fuzz_get_menu(client):
    response = client.get("/menu")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

