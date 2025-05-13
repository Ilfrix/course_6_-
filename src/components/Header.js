import React from 'react';

const Header = ({ cartItems, onCartClick }) => {
  const cartItemsCount = cartItems.reduce((count, item) => count + item.quantity, 0);

  return (
    <header className="header">
      <h1>Пиццерия "SuperPizza"</h1>
      <button className="cart-button" onClick={onCartClick}>
        Корзина ({cartItemsCount})
      </button>
    </header>
  );
};

export default Header;