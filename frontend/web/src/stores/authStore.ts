import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { jarvisAPI } from '@/lib/api';

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  status: string;
  tenant_id: string;
  last_login_at?: string;
  created_at?: string;
  roles?: Array<{
    id: string;
    name: string;
    permissions: string[];
  }>;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      login: (token: string, user: User) => {
        jarvisAPI.setToken(token);
        set({
          token,
          user,
          isAuthenticated: true,
        });
      },

      logout: async () => {
        try {
          await jarvisAPI.logout();
        } catch (error) {
          console.error('Logout error:', error);
        }
        jarvisAPI.setToken('');
        set({
          token: null,
          user: null,
          isAuthenticated: false,
        });
      },

      updateUser: (updates: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({ user: { ...user, ...updates } });
        }
      },
    }),
    {
      name: 'jarvis-auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Initialize token from store on startup
if (typeof window !== 'undefined') {
  const state = useAuthStore.getState();
  if (state.token) {
    jarvisAPI.setToken(state.token);
  }
}
