package com.timelysync.service;

import jakarta.mail.AuthenticationFailedException;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.MailAuthenticationException;
import org.springframework.mail.MailException;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.JavaMailSenderImpl;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

/**
 * Gmail SMTP delivery for welcome + password-reset emails.
 * Credentials come only from environment / .env (via Spring properties).
 */
@Service
public class EmailService {

    private static final Logger logger = LoggerFactory.getLogger(EmailService.class);

    @Autowired(required = false)
    private JavaMailSender mailSender;

    @Value("${spring.mail.host:}")
    private String mailHost;

    @Value("${spring.mail.port:587}")
    private int mailPort;

    @Value("${spring.mail.username:}")
    private String mailUsername;

    @Value("${spring.mail.password:}")
    private String mailPassword;

    @Value("${timelysync.app.mailFrom:}")
    private String mailFrom;

    @Value("${timelysync.app.frontendUrl:http://localhost:3000}")
    private String frontendUrl;

    @Value("${timelysync.app.mailEnabled:false}")
    private boolean mailEnabled;

    public boolean isMailConfigured() {
        boolean senderOk = mailSender instanceof JavaMailSenderImpl impl
                && StringUtils.hasText(impl.getHost())
                && StringUtils.hasText(impl.getUsername())
                && impl.getPassword() != null
                && !impl.getPassword().isBlank();

        boolean propsOk = mailEnabled
                && StringUtils.hasText(mailHost)
                && StringUtils.hasText(mailUsername)
                && StringUtils.hasText(mailPassword);

        logger.debug("isMailConfigured: mailEnabled={} propsOk={} senderOk={} host={} user={} passwordLength={}",
                mailEnabled, propsOk, senderOk, mailHost, mailUsername,
                mailPassword == null ? 0 : mailPassword.replace(" ", "").length());

        return propsOk && mailSender != null && senderOk;
    }

    private String fromAddress() {
        if (StringUtils.hasText(mailFrom)) {
            return mailFrom.trim();
        }
        return mailUsername == null ? "" : mailUsername.trim();
    }

    public String buildPasswordResetLink(String resetToken) {
        return frontendUrl + "/reset-password?token=" + resetToken;
    }

    /**
     * Sends the password-reset email over Gmail SMTP.
     * Does not alter token generation — caller supplies the raw token.
     */
    public MailSendResult sendPasswordResetEmail(String toEmail, String resetToken) {
        String resetLink = buildPasswordResetLink(resetToken);

        if (!isMailConfigured()) {
            String msg = "Gmail SMTP is not configured. "
                    + "Set MAIL_ENABLED=true and MAIL_HOST/MAIL_USERNAME/MAIL_PASSWORD in .env";
            logger.error(msg);
            return MailSendResult.fail(msg);
        }

        logger.info("SMTP connect: host={} port={} user={} → to={}",
                mailHost, mailPort, mailUsername, toEmail);

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
            logger.warn("Skipping welcome email to {} — Gmail SMTP not configured", toEmail);
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
        MailSendResult result = send(toEmail, subject, text, html);
        if (!result.success()) {
            logger.error("Welcome email failed for {}: {}", toEmail, result.error());
        }
    }

    private MailSendResult send(String toEmail, String subject, String text, String html) {
        try {
            logger.info("SMTP auth + send starting (subject=\"{}\", from={}, to={})",
                    subject, fromAddress(), toEmail);

            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            helper.setFrom(fromAddress());
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(text, html);
            mailSender.send(message);

            logger.info("SMTP send SUCCESS to {} subject=\"{}\"", toEmail, subject);
            return MailSendResult.ok();
        } catch (MailAuthenticationException | AuthenticationFailedException ex) {
            String detail = flattenMailError(ex);
            logger.error("SMTP AUTHENTICATION FAILED for user={} host={} port={}: {}",
                    mailUsername, mailHost, mailPort, detail);
            return MailSendResult.fail("Gmail SMTP authentication failed: " + detail);
        } catch (MessagingException ex) {
            String detail = flattenMailError(ex);
            logger.error("SMTP MESSAGING ERROR to {}: {}", toEmail, detail);
            return MailSendResult.fail("Gmail SMTP messaging error: " + detail);
        } catch (MailException ex) {
            String detail = flattenMailError(ex);
            logger.error("SMTP MAIL ERROR to {}: {}", toEmail, detail);
            return MailSendResult.fail("Gmail SMTP error: " + detail);
        } catch (Exception ex) {
            logger.error("SMTP UNEXPECTED ERROR to {}: {}", toEmail, ex.toString());
            return MailSendResult.fail("Gmail SMTP unexpected error: " + ex.getMessage());
        }
    }

    /** Walk nested JavaMail exceptions so Google's SMTP reply is visible. */
    static String flattenMailError(Throwable ex) {
        StringBuilder sb = new StringBuilder();
        Throwable current = ex;
        int depth = 0;
        while (current != null && depth < 8) {
            if (sb.length() > 0) {
                sb.append(" | caused by: ");
            }
            String msg = current.getMessage();
            sb.append(current.getClass().getSimpleName());
            if (StringUtils.hasText(msg)) {
                sb.append(": ").append(msg.trim());
            }
            if (current instanceof MessagingException messaging) {
                Exception next = messaging.getNextException();
                if (next != null && next != current.getCause()) {
                    sb.append(" | smtp: ").append(next.getClass().getSimpleName());
                    if (StringUtils.hasText(next.getMessage())) {
                        sb.append(": ").append(next.getMessage().trim());
                    }
                }
            }
            current = current.getCause();
            depth++;
        }
        return sb.toString();
    }

    private static String escapeHtml(String value) {
        return value
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;");
    }
}
