package com.timelysync.payload.response;

public class ForgotPasswordResponse {
    private String message;
    private boolean emailDelivered;
    private String resetLink;

    public ForgotPasswordResponse(String message, boolean emailDelivered, String resetLink) {
        this.message = message;
        this.emailDelivered = emailDelivered;
        this.resetLink = resetLink;
    }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public boolean isEmailDelivered() { return emailDelivered; }
    public void setEmailDelivered(boolean emailDelivered) { this.emailDelivered = emailDelivered; }

    public String getResetLink() { return resetLink; }
    public void setResetLink(String resetLink) { this.resetLink = resetLink; }
}
