import api from "./api";

const dashboardService = {
  getSummary: () => api.get("/dashboard/summary"),
};

export default dashboardService;
