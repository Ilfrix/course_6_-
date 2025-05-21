import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import CartItem from './CartItem';

const Cart = ({ items, totalPrice, onUpdateQuantity, onRemoveItem, onClose }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [orderSuccess, setOrderSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleCheckout = async () => {
    if (!items.length) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const orderData = {
        items: items.map(item => ({
          pizza_name: item.name,
          quantity: item.quantity,
          price: item.price
        }))
      };

      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('No authentication token found');
      
      const response = await axios.post(`${process.env.REACT_APP_SERVER_IP}:8000/orders/`, orderData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'access-control-allow-credentials':	true,
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 200) {
        setOrderSuccess(true);
        setTimeout(() => {
          items.forEach(item => onRemoveItem(item.id));
          onClose();
          setOrderSuccess(false);
        }, 2000);
      }
    } catch (error) {
      console.error('Ошибка при оформлении заказа:', error);
      setError(error.response?.data?.detail || error.message || 'Ошибка при оформлении заказа');
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="cart-overlay">
      <div className="cart">
        <div className="cart-header">
          <h2>Ваш заказ</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        {items.length === 0 ? (
          <p className="empty-cart">Корзина пуста</p>
        ) : (
          <>
            <div className="cart-items">
              {items.map(item => (
                <CartItem
                  key={item.id}
                  item={item}
                  onUpdateQuantity={onUpdateQuantity}
                  onRemoveItem={onRemoveItem}
                />
              ))}
            </div>
            <div className="cart-total">
              <span>Итого:</span>
              <span>{totalPrice} ₽</span>
            </div>
            <button 
              className="checkout-button" 
              onClick={handleCheckout}
              disabled={isLoading || items.length === 0}
            >
              {isLoading ? 'Оформляем...' : 'Оформить заказ'}
            </button>
            {orderSuccess && <p className="success-message">Заказ успешно оформлен!</p>}
            {error && <p className="error-message">{error}</p>}
          </>
        )}
      </div>
    </div>
  );
};

export default Cart;
