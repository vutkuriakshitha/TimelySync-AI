import api from "./api";

const taskService = {
  // Paginated/filterable list - used where server-side pagination matters
  getTasks: (params = {}) => api.get("/tasks", { params }),

  // Full unpaginated list for the current user - used to power client-side
  // dashboards/filters (today/upcoming/overdue/high-risk/etc.)
  getAllTasks: () => api.get("/tasks/all"),

  getTaskById: (taskId) => api.get(`/tasks/${taskId}`),

  createTask: (taskData) => api.post("/tasks", taskData),

  updateTask: (taskId, updates) => api.put(`/tasks/${taskId}`, updates),

  deleteTask: (taskId) => api.delete(`/tasks/${taskId}`),

  completeTask: (taskId, proofFile) => {
    const formData = new FormData();
    if (proofFile) {
      formData.append("proof", proofFile);
    }
    return api.post(`/tasks/${taskId}/complete`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  addSubtask: (taskId, subtask) => api.post(`/tasks/${taskId}/subtasks`, subtask),

  toggleSubtask: (taskId, subtaskId) =>
    api.patch(`/tasks/${taskId}/subtasks/${subtaskId}/toggle`),

  deleteSubtask: (taskId, subtaskId) =>
    api.delete(`/tasks/${taskId}/subtasks/${subtaskId}`),

  getImpactSimulation: (taskId, scenario = "miss") =>
    api.get(`/tasks/${taskId}/impact-simulation`, { params: { scenario } }),
};

export default taskService;
