import React, { createContext, useContext, useState, useEffect } from 'react';
import { refreshAccessToken, authenticatedFetch } from '../services/apiClient';

const AuthContext = createContext(null);

const TOKEN_KEY = 'sf_access_token';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || '');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    restoreSession();
  }, []);

  useEffect(() => {
    const handleExpired = () => {
      clearSession();
    };
    window.addEventListener('sf_session_expired', handleExpired);
    return () => window.removeEventListener('sf_session_expired', handleExpired);
  }, []);

  const restoreSession = async () => {
    let activeToken = token || localStorage.getItem(TOKEN_KEY) || '';

    // Case C: Access token missing in localStorage -> attempt silent refresh using HttpOnly cookie
    if (!activeToken) {
      try {
        const refreshedToken = await refreshAccessToken();
        if (refreshedToken) {
          activeToken = refreshedToken;
          setToken(refreshedToken);
        }
      } catch (e) {
        setUser(null);
        setLoading(false);
        return;
      }
    }

    if (!activeToken) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const resp = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${activeToken}` },
        credentials: 'include',
      });

      if (resp.ok) {
        const data = await resp.json();
        if (data.success && data.user) {
          setUser(data.user);
        } else {
          clearSession();
        }
      } else if (resp.status === 401) {
        // Case B: Access token expired -> attempt automatic token refresh
        try {
          const newToken = await refreshAccessToken();
          if (newToken) {
            setToken(newToken);
            const retryResp = await fetch('/api/auth/me', {
              headers: { Authorization: `Bearer ${newToken}` },
              credentials: 'include',
            });
            if (retryResp.ok) {
              const retryData = await retryResp.json();
              if (retryData.success && retryData.user) {
                setUser(retryData.user);
                return;
              }
            }
          }
        } catch (e) {
          // Case D: Refresh failed
        }
        clearSession();
      } else {
        clearSession();
      }
    } catch (err) {
      console.warn('Failed to restore authentication session:', err);
      clearSession();
    } finally {
      setLoading(false);
    }
  };

  const clearSession = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken('');
    setUser(null);
  };

  const login = async (username, password) => {
    try {
      const resp = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });

      const data = await resp.json();
      if (!resp.ok) {
        return { success: false, error: data.detail || 'Invalid username or password.' };
      }

      localStorage.setItem(TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return { success: true, user: data.user };
    } catch (err) {
      return { success: false, error: `Authentication service unavailable: ${err.message}` };
    }
  };

  const register = async (username, email, password) => {
    try {
      const resp = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, email, password }),
      });

      const data = await resp.json();
      if (!resp.ok) {
        return { success: false, error: data.detail || 'Registration failed.' };
      }

      localStorage.setItem(TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return { success: true, user: data.user };
    } catch (err) {
      return { success: false, error: `Registration service unavailable: ${err.message}` };
    }
  };

  const logout = async () => {
    try {
      const activeToken = token || localStorage.getItem(TOKEN_KEY) || '';
      if (activeToken) {
        await authenticatedFetch('/api/auth/logout', { method: 'POST' });
      }
    } catch (err) {
      console.warn('Server logout request failed:', err);
    } finally {
      clearSession();
    }
  };

  const logoutAll = async () => {
    try {
      const activeToken = token || localStorage.getItem(TOKEN_KEY) || '';
      if (activeToken) {
        await authenticatedFetch('/api/auth/logout-all', { method: 'POST' });
      }
    } catch (err) {
      console.warn('Server logout-all request failed:', err);
    } finally {
      clearSession();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        logoutAll,
        restoreSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
