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
            {/* <span>Welcome, {user.username}</span> */}
            <button onClick={logout} className="cart-button">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" className="cart-button">Login</Link>
            <Link to="/register" className="cart-button">Register</Link>
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