import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import '../OrdersPage.css';

const OrdersPage = () => {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [removingItems, setRemovingItems] = useState({});

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${process.env.REACT_APP_SERVER_IP}:8000/orders/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrders(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось загрузить заказы');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleRemoveItem = async (itemId, orderId) => {
    try {
      setRemovingItems(prev => ({ ...prev, [itemId]: true }));
      const token = localStorage.getItem('access_token');
      
      await axios.delete(`${process.env.REACT_APP_SERVER_IP}:8000/order-items/${itemId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setOrders(prevOrders => {
        return prevOrders.map(order => {
          if (order.id === orderId) {
            const updatedItems = order.items.map(item => {
              if (item.id === itemId) {
                return { ...item, quantity: item.quantity - 1 };
              }
              return item;
            }).filter(item => item.quantity > 0);

            if (updatedItems.length === 0) return null;
            return { ...order, items: updatedItems };
          }
          return order;
        }).filter(Boolean);
      });

    } catch (err) {
      setError('Не удалось удалить позицию');
      console.error('Error removing item:', err);
      fetchOrders();
    } finally {
      setRemovingItems(prev => ({ ...prev, [itemId]: false }));
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="orders-container">
      <h1>Ваши заказы</h1>
      <p>Вы можете отслеживать свои заказы также в Телеграм по уникальному номеру. @mireapizzabot</p>
      <Link to="/" className="back-link">← Вернуться к меню</Link>
      
      {orders.length === 0 ? (
        <p className="no-orders">Заказов не найдено</p>
      ) : (
        <div className="orders-list">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <h2>Заказ #{order.id}</h2>
                
                <p>Статус: <span className={`status-${order.status}`}>{order.status}</span></p>
                
                <div>
                  <br />
                  <p>Уникальный номер:{order.order_hash}</p>
                </div>
              </div>
              
              <div className="order-items">
                <h3>Позиции:</h3>
                <ul>
                  {order.items.map(item => (
                    <li key={item.id} className={`order-item ${removingItems[item.id] ? 'removing' : ''}`}>
                      <div className="item-info">
                        <span>{item.pizza_name}</span>
                        <span>{item.quantity} × {item.price} ₽ = {item.quantity * item.price} ₽</span>
                      </div>
                      <button 
                        onClick={() => handleRemoveItem(item.id, order.id)}
                        className="remove-item-btn"
                        disabled={removingItems[item.id]}
                      >
                        {removingItems[item.id] ? 'Удаление...' : 'Удалить'}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="order-total">
                Итого: {order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0)} ₽
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrdersPage;
