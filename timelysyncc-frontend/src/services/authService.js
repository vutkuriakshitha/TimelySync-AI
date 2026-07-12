import api from "./api";

const authService = {
  register: (name, email, password) =>
    api.post("/auth/register", { name, email, password }),

  login: (email, password) => api.post("/auth/login", { email, password }),

  getCurrentUser: () => api.get("/auth/me"),

  updateProfile: (updates) => api.put("/auth/me", updates),

  changePassword: (currentPassword, newPassword) =>
    api.put("/auth/me/password", { currentPassword, newPassword }),

  deleteAccount: () => api.delete("/auth/me"),

  logout: () => api.post("/auth/logout"),

  forgotPassword: (email) => api.post("/auth/forgot-password", { email }),

  resetPassword: (token, newPassword) =>
    api.post("/auth/reset-password", { token, newPassword }),
};

export default authService;
