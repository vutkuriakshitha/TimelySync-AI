import api from "./api";

const statsService = {
  getStats: () => api.get("/stats"),
};

export default statsService;
