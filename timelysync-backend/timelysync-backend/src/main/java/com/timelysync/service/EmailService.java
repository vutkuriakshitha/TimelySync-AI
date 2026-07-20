package com.timelysync.service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

/**
 * Transactional email (welcome + password reset).
 * {@link #sendPasswordResetEmail} returns whether SMTP accepted the message so
 * AuthService can return an in-app reset link when mail is unavailable.
 */
@Service
public class EmailService {

    private static final Logger logger = LoggerFactory.getLogger(EmailService.class);

    @Autowired(required = false)
    private JavaMailSender mailSender;

    @Value("${spring.mail.host:}")
    private String mailHost;

    @Value("${spring.mail.username:}")
    private String mailUsername;

    @Value("${timelysync.app.mailFrom:}")
    private String mailFrom;

    @Value("${timelysync.app.frontendUrl:http://localhost:3000}")
    private String frontendUrl;

    @Value("${timelysync.app.mailEnabled:false}")
    private boolean mailEnabled;

    @Value("${spring.mail.password:}")
    private String mailPassword;

    public boolean isMailConfigured() {
        return mailEnabled
                && mailSender != null
                && StringUtils.hasText(mailHost)
                && StringUtils.hasText(mailUsername)
                && StringUtils.hasText(mailPassword);
    }

    private String fromAddress() {
        if (StringUtils.hasText(mailFrom)) {
            return mailFrom;
        }
        return mailUsername;
    }

    public String buildPasswordResetLink(String resetToken) {
        return frontendUrl + "/reset-password?token=" + resetToken;
    }

    /**
     * Attempts SMTP delivery. Returns true only when the provider accepted the message.
     * Kept synchronous so forgot-password can fall back immediately on failure.
     */
    public boolean sendPasswordResetEmail(String toEmail, String resetToken) {
        String resetLink = buildPasswordResetLink(resetToken);

        if (!isMailConfigured()) {
            logger.warn("SMTP not configured — AuthService may return in-app reset link for {}", toEmail);
            return false;
        }

        String subject = "Reset your TimelySync password";
        String html = """
                <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;color:#1f2937">
                  <h2 style="color:#2563eb;margin-bottom:8px">Reset your password</h2>
                  <p>We received a request to reset your TimelySync password.</p>
                  <p>This link expires in <strong>1 hour</strong>.</p>
                  <p style="margin:28px 0">
                    <a href="%s"
                       style="background:#2563eb;color:#fff;padding:12px 20px;border-radius:8px;
                              text-decoration:none;font-weight:600;display:inline-block">
                      Reset password
                    </a>
                  </p>
                  <p style="font-size:13px;color:#6b7280">Or paste this link into your browser:<br>
                    <a href="%s" style="color:#2563eb;word-break:break-all">%s</a>
                  </p>
                  <p style="font-size:13px;color:#6b7280">If you did not request this, ignore this email.</p>
                </div>
                """.formatted(resetLink, resetLink, resetLink);

        String text = "Reset your TimelySync password\n\n"
                + "Open this link (expires in 1 hour):\n" + resetLink + "\n";

        return send(toEmail, subject, text, html);
    }

    @Async
    public void sendWelcomeEmail(String toEmail, String name) {
        if (!isMailConfigured()) {
            return;
        }

        String safeName = StringUtils.hasText(name) ? name.trim() : "there";
        String loginUrl = frontendUrl + "/login";
        String subject = "Welcome to TimelySync";
        String html = """
                <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;color:#1f2937">
                  <h2 style="color:#2563eb;margin-bottom:8px">Welcome, %s</h2>
                  <p>Your TimelySync account is ready.</p>
                  <p style="margin:28px 0">
                    <a href="%s"
                       style="background:#2563eb;color:#fff;padding:12px 20px;border-radius:8px;
                              text-decoration:none;font-weight:600;display:inline-block">
                      Sign in
                    </a>
                  </p>
                </div>
                """.formatted(escapeHtml(safeName), loginUrl);

        String text = "Welcome to TimelySync, " + safeName + "!\n\nSign in: " + loginUrl + "\n";
        send(toEmail, subject, text, html);
    }

    private boolean send(String toEmail, String subject, String text, String html) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            helper.setFrom(fromAddress());
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(text, html);
            mailSender.send(message);
            logger.info("Email sent to {} subject=\"{}\"", toEmail, subject);
            return true;
        } catch (MessagingException ex) {
            logger.error("Failed to build email to {}: {}", toEmail, ex.getMessage());
            return false;
        } catch (Exception ex) {
            logger.error("Failed to send email to {}: {}", toEmail, ex.getMessage());
            return false;
        }
    }

    private static String escapeHtml(String value) {
        return value
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;");
    }
}
