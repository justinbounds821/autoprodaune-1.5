import { useState, useEffect } from 'react';

export interface AdminAuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (password: string) => Promise<boolean>;
  logout: () => void;
}

const ADMIN_PASSWORD = 'admin123'; // In production, this should come from backend
const AUTH_STORAGE_KEY = 'adminAuth';

export const useAdminAuth = (): AdminAuthState => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated on mount
    const checkAuth = () => {
      try {
        const authStatus = localStorage.getItem(AUTH_STORAGE_KEY);
        setIsAuthenticated(authStatus === 'authenticated');
      } catch (error) {
        console.error('Error checking auth status:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (password: string): Promise<boolean> => {
    setIsLoading(true);

    try {
      // Simulate network delay for realistic UX
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (password === ADMIN_PASSWORD) {
        localStorage.setItem(AUTH_STORAGE_KEY, 'authenticated');
        setIsAuthenticated(true);
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    try {
      localStorage.removeItem(AUTH_STORAGE_KEY);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return {
    isAuthenticated,
    isLoading,
    login,
    logout
  };
};

export default useAdminAuth;