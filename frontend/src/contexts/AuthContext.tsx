import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI, LoginCredentials, User } from '../api/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    console.log('[AuthContext] Initializing...');
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    console.log('[AuthContext] Token exists:', !!token);
    console.log('[AuthContext] Stored user exists:', !!storedUser);

    if (token && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        console.log('[AuthContext] Parsed user:', parsedUser);
        setUser(parsedUser);
      } catch (e) {
        console.error('[AuthContext] Failed to parse user:', e);
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }

    setIsLoading(false);
    console.log('[AuthContext] Loading complete');
  }, []);

  const login = async (credentials: LoginCredentials) => {
    console.log('[AuthContext] Login starting...');
    const response = await authAPI.login(credentials);
    console.log('[AuthContext] Login response:', response);
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('user', JSON.stringify(response.user));
    console.log('[AuthContext] Saved to localStorage');
    setUser(response.user);
    console.log('[AuthContext] User state updated');
  };

  const logout = () => {
    authAPI.logout().catch(() => {});
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
