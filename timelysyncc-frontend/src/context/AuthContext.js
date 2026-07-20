// src/context/AuthContext.js
import React, { createContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import authService from "../services/authService";
import accountService from "../services/accountService";
import { registerUnauthorizedHandler } from "../services/api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [availableAccounts, setAvailableAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadAvailableAccounts = useCallback(async () => {
    try {
      const response = await accountService.getLinkedAccounts();
      setAvailableAccounts(response.data || []);
    } catch (error) {
      console.error("Error loading linked accounts:", error);
    }
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setAvailableAccounts([]);
  }, []);

  // Validate any stored token against the server on first load, rather than
  // trusting stale localStorage data blindly.
  useEffect(() => {
    const bootstrap = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const response = await authService.getCurrentUser();
        setUser(response.data);
        localStorage.setItem("user", JSON.stringify(response.data));
        loadAvailableAccounts();
      } catch (error) {
        clearSession();
      } finally {
        setLoading(false);
      }
    };
    bootstrap();
  }, [clearSession, loadAvailableAccounts]);

  // Register a global 401 handler so any expired/invalid token anywhere in
  // the app forces a clean logout instead of a silent broken UI.
  useEffect(() => {
    registerUnauthorizedHandler(() => {
      clearSession();
      toast.error("Your session has expired. Please log in again.");
      navigate("/login");
    });
  }, [clearSession, navigate]);

  const login = async (email, password) => {
    try {
      const response = await authService.login(email.trim().toLowerCase(), password);
      const { token, user: userData } = response.data;

      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(userData));
      setUser(userData);

      toast.success(`Welcome back, ${userData.name}!`);
      navigate("/dashboard");
      loadAvailableAccounts();

      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.message ||
        (error.code === "ECONNABORTED"
          ? "Server took too long to respond. Please try again."
          : error.message?.includes("Network")
            ? "Cannot reach the server. Is the backend running?"
            : "Login failed. Please try again.");
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await authService.register(name, email.trim().toLowerCase(), password);
      const { token, user: userData } = response.data;

      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(userData));
      setUser(userData);

      toast.success(`Welcome to TimelySync, ${userData.name}!`);
      navigate("/dashboard");
      loadAvailableAccounts();

      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.message ||
        (error.code === "ECONNABORTED"
          ? "Server took too long to respond. Please try again."
          : error.message?.includes("Network")
            ? "Cannot reach the server. Is the backend running?"
            : "Registration failed. Please try again.");
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      // Stateless JWT - logout is best-effort on the server; always clear locally.
    }
    clearSession();
    toast.success("Logged out successfully");
    navigate("/login");
  };

  const updateUser = async (updates) => {
    try {
      const response = await authService.updateProfile(updates);
      setUser(response.data);
      localStorage.setItem("user", JSON.stringify(response.data));
      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.message || "Failed to update profile";
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      await authService.changePassword(currentPassword, newPassword);
      toast.success("Password updated successfully");
      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.message || "Failed to change password";
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const deleteAccount = async () => {
    try {
      await authService.deleteAccount();
      clearSession();
      toast.success("Account deleted");
      navigate("/login");
      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.message || "Failed to delete account";
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const switchAccount = async (accountId) => {
    try {
      const response = await accountService.switchAccount(accountId);
      setUser(response.data);
      localStorage.setItem("user", JSON.stringify(response.data));
      toast.success("Account switched successfully");
      return { success: true };
    } catch (error) {
      toast.error("Failed to switch account");
      return { success: false };
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        availableAccounts,
        login,
        register,
        logout,
        updateUser,
        changePassword,
        deleteAccount,
        switchAccount,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
