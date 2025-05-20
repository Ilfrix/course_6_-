import React from 'react';

const CartItem = ({ item, onUpdateQuantity, onRemoveItem }) => {
  return (
    <div className="cart-item">
      <div className="cart-item-info">
        <h4>{item.name}</h4>
        <p>{item.price} ₽</p>
      </div>
      <div className="cart-item-controls">
        <button onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}>-</button>
        <span>{item.quantity}</span>
        <button onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}>+</button>
        <button className="remove-button" onClick={() => onRemoveItem(item.id)}>×</button>
      </div>
    </div>
  );
};

export default CartItem;