package com.timelysync.service;

/**
 * Result of an SMTP send attempt. On failure, {@link #error()} holds the
 * provider's exact message (including nested JavaMail / SMTP replies).
 */
public record MailSendResult(boolean success, String error) {
    public static MailSendResult ok() {
        return new MailSendResult(true, null);
    }

    public static MailSendResult fail(String error) {
        return new MailSendResult(false, error == null ? "Unknown SMTP error" : error);
    }
}
