package com.timelysync.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.MailException;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

/**
 * Sends transactional emails (currently just password reset). If SMTP
 * credentials are not configured (local/dev environments), this degrades
 * gracefully by logging the email instead of throwing - the app must never
 * crash a request just because outbound email isn't configured yet.
 */
@Service
public class EmailService {

    private static final Logger logger = LoggerFactory.getLogger(EmailService.class);

    @Autowired(required = false)
    private JavaMailSender mailSender;

    @Value("${spring.mail.username:}")
    private String fromAddress;

    @Value("${timelysync.app.frontendUrl:http://localhost:3000}")
    private String frontendUrl;

    private boolean isMailConfigured() {
        return mailSender != null && fromAddress != null && !fromAddress.isBlank();
    }

    @Async
    public void sendPasswordResetEmail(String toEmail, String resetToken) {
        String resetLink = frontendUrl + "/reset-password?token=" + resetToken;

        if (!isMailConfigured()) {
            logger.info("[DEV MODE - SMTP not configured] Password reset link for {}: {}", toEmail, resetLink);
            return;
        }

        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom(fromAddress);
            message.setTo(toEmail);
            message.setSubject("Reset your TimelySync password");
            message.setText("We received a request to reset your TimelySync password.\n\n"
                    + "Click the link below to choose a new password. This link expires in 1 hour.\n\n"
                    + resetLink + "\n\n"
                    + "If you did not request this, you can safely ignore this email.");
            mailSender.send(message);
        } catch (MailException ex) {
            logger.error("Failed to send password reset email to {}: {}", toEmail, ex.getMessage());
        }
    }
}
