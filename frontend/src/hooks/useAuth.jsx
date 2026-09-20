import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import * as authService from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('mplads_user');
    return stored ? JSON.parse(stored) : null;
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const signIn = useCallback(async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const { accessToken, user: loggedInUser } = await authService.login(username, password);
      localStorage.setItem('mplads_token', accessToken);
      localStorage.setItem('mplads_user', JSON.stringify(loggedInUser));
      setUser(loggedInUser);
      return loggedInUser;
    } catch (err) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const signOut = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, isAuthenticated: !!user, loading, error, signIn, signOut }),
    [user, loading, error, signIn, signOut]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
