import api from "./api";

const analyticsService = {
  getAnalytics: () => api.get("/analytics"),
};

export default analyticsService;
