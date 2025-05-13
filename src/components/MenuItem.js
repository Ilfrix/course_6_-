import React from 'react';

const MenuItem = ({ item, onAddToCart }) => {
  return (
    <div className="menu-item">
      <h3>{item.name}</h3>
      <p>{item.description}</p>
      <div className="menu-item-footer">
        <span>{item.price} ₽</span>
        <button onClick={onAddToCart}>Добавить</button>
      </div>
    </div>
  );
};

export default MenuItem;