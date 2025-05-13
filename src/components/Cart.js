import React from 'react';
import CartItem from './CartItem';

const Cart = ({ items, totalPrice, onUpdateQuantity, onRemoveItem, onClose }) => {
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
            <button className="checkout-button">Оформить заказ</button>
          </>
        )}
      </div>
    </div>
  );
};

export default Cart;