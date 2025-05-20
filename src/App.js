import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import MenuPage from './pages/MenuPage';
import Login from './pages/Login';
import Register from './pages/Register';
import OrdersPage from './pages/OrdersPage';
import './styles.css';

const App = () => {

  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/" element={<MenuPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/orders" element={<OrdersPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;