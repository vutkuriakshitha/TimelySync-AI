import api from "./api";

const aiService = {
  getFailurePredictions: () => api.get("/ai/failure-predictions"),

  smartIntake: (text) => api.post("/ai/smart-intake", { text }),

  extractDeadlines: (text, documentName) =>
    api.post("/ai/deadline-extraction", { text, documentName }),

  extractDocumentDeadlines: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/ai/document-deadlines", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000,
    });
  },
};

export default aiService;
