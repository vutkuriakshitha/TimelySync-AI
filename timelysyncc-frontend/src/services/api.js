import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8080/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
});

// Attach the JWT (if any) to every outgoing request.
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Callback registered by AuthContext so a 401 can trigger a clean logout
// without creating a circular import between api.js and AuthContext.
let onUnauthorized = null;
export const registerUnauthorizedHandler = (handler) => {
  onUnauthorized = handler;
};

const isPublicAuthUrl = (url = "") =>
  url.includes("/auth/login") ||
  url.includes("/auth/register") ||
  url.includes("/auth/forgot-password") ||
  url.includes("/auth/reset-password") ||
  url.includes("/auth/me");

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url || "";

    // Never force-redirect away from public auth flows. /auth/me failures
    // during bootstrap are handled quietly by AuthContext.clearSession.
    if (status === 401 && !isPublicAuthUrl(url)) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (onUnauthorized) onUnauthorized();
    }
    return Promise.reject(error);
  },
);

export default api;
