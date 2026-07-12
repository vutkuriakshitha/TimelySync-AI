import api from "./api";

const notificationService = {
  getNotifications: (unreadOnly = false) =>
    api.get("/notifications", { params: { unreadOnly } }),

  getUnreadCount: () => api.get("/notifications/unread-count"),

  markAsRead: (id) => api.patch(`/notifications/${id}/read`),

  markAllAsRead: () => api.patch("/notifications/read-all"),
};

export default notificationService;
