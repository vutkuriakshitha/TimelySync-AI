package com.timelysync.payload.request;

import jakarta.validation.constraints.NotBlank;

public class SwitchAccountRequest {
    @NotBlank
    private String accountId;

    public String getAccountId() { return accountId; }
    public void setAccountId(String accountId) { this.accountId = accountId; }
}
