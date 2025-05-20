import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'));

  // Функция для обновления токена
  const refreshAccessToken = useCallback(async () => {
    try {
      const response = await axios.post('http://localhost:8000/refresh-token', {
        refresh_token: localStorage.getItem('refresh_token') // Берем актуальный токен
      });
      
      const { access_token, refresh_token } = response.data;
      // Обновляем и состояние, и localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      return access_token;
    } catch (err) {
      console.error("Refresh token error:", err);
      logout();
      throw err;
    }
  }, []); // Убрана зависимость от refreshToken

  // Настройка интерцепторов axios
  useEffect(() => {
    const requestInterceptor = axios.interceptors.request.use(config => {
      const token = localStorage.getItem('access_token'); // Всегда берем актуальный токен
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    const responseInterceptor = axios.interceptors.response.use(
      response => response,
      async error => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && 
            !originalRequest._retry && 
            !originalRequest.url.includes('/refresh-token')) {
          originalRequest._retry = true;
          
          try {
            const newAccessToken = await refreshAccessToken();
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return axios(originalRequest);
          } catch (refreshError) {
            logout();
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, [refreshAccessToken]);

  // Проверка авторизации при загрузке
  useEffect(() => {
    const verifyAuth = async () => {
      if (accessToken) {
        try {
          const response = await axios.get('http://localhost:8000/users/me/', {
            headers: {
              Authorization: `Bearer ${accessToken}`
            }
          });
          setUser(response.data);
        } catch (err) {
          if (err.response?.status === 401 && refreshToken) {
            try {
              await refreshAccessToken();
              const newResponse = await axios.get('http://localhost:8000/users/me/', {
                headers: {
                  Authorization: `Bearer ${accessToken}`
                }
              });
              setUser(newResponse.data);
            } catch (refreshErr) {
              logout();
            }
          } else {
            logout();
          }
        }
      }
      setLoading(false);
    };

    verifyAuth();
  }, [accessToken, refreshToken, refreshAccessToken]);

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:8000/token', {
        username,
        password,
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      setAccessToken(response.data.access_token);
      setRefreshToken(response.data.refresh_token);
      
      const userResponse = await axios.get('http://localhost:8000/users/me/', {
        headers: {
          Authorization: `Bearer ${response.data.access_token}`
        }
      });
      
      setUser(userResponse.data);
      setError(null);
      return true;
    } catch (err) {
      setError('Invalid username or password');
      return false;
    }
  };

  const register = async (username, password, email, fullName) => {
    try {
      await axios.post('http://localhost:8000/register', {
        username,
        password,
        email,
        full_name: fullName
      });
      
      return await login(username, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      error, 
      login, 
      register, 
      logout 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);