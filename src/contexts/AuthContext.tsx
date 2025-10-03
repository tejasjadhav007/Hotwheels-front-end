import { createContext, useContext, useState, ReactNode } from 'react';
import { User } from '../types';
import { mockAdminUser, mockCustomerUser } from '../data/mockData';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  signup: (email: string, password: string, fullName: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string): Promise<boolean> => {
    if (email === 'admin@hotwheels.com' && password === 'Admin@1234') {
      setUser(mockAdminUser);
      return true;
    }

    if (email === 'customer@example.com' && password === 'Customer123') {
      setUser(mockCustomerUser);
      return true;
    }

    return false;
  };

  const logout = () => {
    setUser(null);
  };

  const signup = async (email: string, password: string, fullName: string): Promise<boolean> => {
    const newUser: User = {
      id: `user-${Date.now()}`,
      email,
      fullName,
      role: 'customer',
    };
    setUser(newUser);
    return true;
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, signup }}>
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
