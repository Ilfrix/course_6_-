import React, { useState } from 'react';
import Header from '../components/Header';
import MenuItem from '../components/MenuItem';
import Cart from '../components/Cart';
import '../styles.css';

const MenuPage = () => {
  const [menuItems] = useState([
    { id: 1, name: 'Маргарита', price: 350, description: 'Томатный соус, моцарелла, базилик' },
    { id: 2, name: 'Пепперони', price: 450, description: 'Томатный соус, моцарелла, пепперони' },
    { id: 3, name: 'Гавайская', price: 400, description: 'Томатный соус, моцарелла, курица, ананас' },
    { id: 4, name: 'Четыре сыра', price: 500, description: 'Сливочный соус, моцарелла, пармезан, дор блю, чеддер' },
  ]);

  const [cartItems, setCartItems] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const addToCart = (item) => {
    setCartItems(prevItems => {
      const existingItem = prevItems.find(cartItem => cartItem.id === item.id);
      if (existingItem) {
        return prevItems.map(cartItem =>
          cartItem.id === item.id
            ? { ...cartItem, quantity: cartItem.quantity + 1 }
            : cartItem
        );
      }
      return [...prevItems, { ...item, quantity: 1 }];
    });
  };

  const removeFromCart = (id) => {
    setCartItems(prevItems => prevItems.filter(item => item.id !== id));
  };

  const updateQuantity = (id, quantity) => {
    if (quantity <= 0) {
      removeFromCart(id);
      return;
    }
    setCartItems(prevItems =>
      prevItems.map(item =>
        item.id === id ? { ...item, quantity } : item
      )
    );
  };

  const totalPrice = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return (
    <div className="app">
      <Header cartItems={cartItems} onCartClick={() => setIsCartOpen(!isCartOpen)} />
      
      <main className="menu">
        <h2>Наше меню</h2>
        <div className="menu-items">
          {menuItems.map(item => (
            <MenuItem key={item.id} item={item} onAddToCart={() => addToCart(item)} />
          ))}
        </div>
      </main>

      {isCartOpen && (
        <Cart
          items={cartItems}
          totalPrice={totalPrice}
          onUpdateQuantity={updateQuantity}
          onRemoveItem={removeFromCart}
          onClose={() => setIsCartOpen(false)}
        />
      )}
    </div>
  );
};

export default MenuPage;