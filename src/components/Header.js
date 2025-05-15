import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const Header = ({ cartItems, onCartClick }) => {
  const { user, logout } = useAuth();
  const cartItemsCount = cartItems.reduce((count, item) => count + item.quantity, 0);

  return (
    <header className="header">
      <h1>Пиццерия "SuperPizza"</h1>
      <div className="header-controls">
        {user ? (
          <>
            <button onClick={logout} className="cart-button">Выйти</button>
            <Link to="/orders" className="cart-button">Мои заказы</Link>
          </>
        ) : (
          <>
            <Link to="/login" className="cart-button">Войти</Link>
            <Link to="/register" className="cart-button">Зарегистрироваться</Link>
          </>
        )}
        <button className="cart-button" onClick={onCartClick}>
          Корзина ({cartItemsCount})
        </button>
      </div>
    </header>
  );
};

export default Header;