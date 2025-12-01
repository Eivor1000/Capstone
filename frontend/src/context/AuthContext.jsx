import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(null);

  // Load token from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');

    if (token && userData) {
      setAccessToken(token);
      setUser(JSON.parse(userData));
    }
    setLoading(false);
  }, []);

  // Login function
  const login = async (credentials) => {
    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (data.success) {
        const { access_token, refresh_token } = data.tokens;
        const userData = data.user;

        // Store tokens and user data
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('user_data', JSON.stringify(userData));

        setAccessToken(access_token);
        setUser(userData);

        return { success: true, user: userData };
      } else {
        return { success: false, error: data.error || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (data.success) {
        // Auto-login after registration
        return await login({
          username: userData.username,
          password: userData.password,
        });
      } else {
        return { success: false, error: data.error || 'Registration failed' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    setAccessToken(null);
    setUser(null);
  };

  // Update user profile
  const updateProfile = async (updates) => {
    try {
      const response = await fetch('http://localhost:5000/api/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(updates),
      });

      const data = await response.json();

      if (data.success) {
        const updatedUser = data.user;
        localStorage.setItem('user_data', JSON.stringify(updatedUser));
        setUser(updatedUser);
        return { success: true, user: updatedUser };
      } else {
        return { success: false, error: data.error || 'Update failed' };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Change password
  const changePassword = async (oldPassword, newPassword) => {
    try {
      const response = await fetch('http://localhost:5000/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (data.success) {
        return { success: true, message: data.message };
      } else {
        return { success: false, error: data.error || 'Password change failed' };
      }
    } catch (error) {
      console.error('Password change error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Refresh token function
  const refreshToken = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      if (!refresh) return false;

      const response = await fetch('http://localhost:5000/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refresh}`,
        },
      });

      const data = await response.json();

      if (data.success) {
        const newAccessToken = data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        setAccessToken(newAccessToken);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  };

  // API call helper with automatic token refresh
  const apiCall = async (url, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    try {
      let response = await fetch(url, { ...options, headers });

      // If token expired, try to refresh
      if (response.status === 401 && accessToken) {
        const refreshed = await refreshToken();
        if (refreshed) {
          // Retry with new token
          headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
          response = await fetch(url, { ...options, headers });
        } else {
          // Refresh failed, logout user
          logout();
          return null;
        }
      }

      return response;
    } catch (error) {
      console.error('API call error:', error);
      return null;
    }
  };

  const value = {
    user,
    accessToken,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshToken,
    apiCall,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
