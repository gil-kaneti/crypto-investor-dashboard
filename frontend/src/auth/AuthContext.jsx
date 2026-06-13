import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { clearToken, getToken, setToken } from "./token";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [tokenState, setTokenState] = useState(() => getToken());
  const [user, setUser] = useState(null);
  const [isCheckingUser, setIsCheckingUser] = useState(Boolean(tokenState));

  const logout = useCallback(() => {
    clearToken();
    setTokenState(null);
    setUser(null);
  }, []);

  const loadUser = useCallback(async () => {
    if (!getToken()) {
      setIsCheckingUser(false);
      setUser(null);
      return null;
    }

    setIsCheckingUser(true);
    try {
      const currentUser = await api.me();
      setUser(currentUser);
      return currentUser;
    } catch (error) {
      logout();
      return null;
    } finally {
      setIsCheckingUser(false);
    }
  }, [logout]);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    window.addEventListener("auth-token-cleared", logout);
    return () => window.removeEventListener("auth-token-cleared", logout);
  }, [logout]);

  const login = useCallback(
    async (payload) => {
      const response = await api.login(payload);
      setToken(response.access_token);
      setTokenState(response.access_token);
      const currentUser = await loadUser();
      return currentUser;
    },
    [loadUser],
  );

  const value = useMemo(
    () => ({
      user,
      isCheckingUser,
      isAuthenticated: Boolean(tokenState),
      login,
      logout,
      refreshUser: loadUser,
    }),
    [isCheckingUser, loadUser, login, logout, tokenState, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
