import { createContext, useCallback, useContext, useState } from "react";
import { loginUser, registerUser } from "../api/client";

interface AuthState {
  token: string | null;
  email: string | null;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function parseEmail(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return (payload.email as string) ?? null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem("qp_token");
    return { token, email: token ? parseEmail(token) : null };
  });

  const setToken = useCallback((token: string) => {
    localStorage.setItem("qp_token", token);
    setState({ token, email: parseEmail(token) });
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const token = await loginUser(email, password);
      setToken(token);
    },
    [setToken],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const token = await registerUser(email, password);
      setToken(token);
    },
    [setToken],
  );

  const logout = useCallback(() => {
    localStorage.removeItem("qp_token");
    setState({ token: null, email: null });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
