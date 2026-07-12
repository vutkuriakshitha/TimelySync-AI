import api from "./api";

const accountService = {
  getLinkedAccounts: () => api.get("/accounts"),

  switchAccount: (accountId) => api.post("/accounts/switch", { accountId }),
};

export default accountService;
