package com.timelysync.payload.response;

public class ForgotPasswordResponse {
    private String message;
    private boolean emailDelivered;
    private String resetLink;
    /** Exact SMTP / delivery error when emailDelivered is false and send was attempted. */
    private String deliveryError;

    public ForgotPasswordResponse(String message, boolean emailDelivered, String resetLink) {
        this(message, emailDelivered, resetLink, null);
    }

    public ForgotPasswordResponse(String message, boolean emailDelivered, String resetLink, String deliveryError) {
        this.message = message;
        this.emailDelivered = emailDelivered;
        this.resetLink = resetLink;
        this.deliveryError = deliveryError;
    }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public boolean isEmailDelivered() { return emailDelivered; }
    public void setEmailDelivered(boolean emailDelivered) { this.emailDelivered = emailDelivered; }

    public String getResetLink() { return resetLink; }
    public void setResetLink(String resetLink) { this.resetLink = resetLink; }

    public String getDeliveryError() { return deliveryError; }
    public void setDeliveryError(String deliveryError) { this.deliveryError = deliveryError; }
}
