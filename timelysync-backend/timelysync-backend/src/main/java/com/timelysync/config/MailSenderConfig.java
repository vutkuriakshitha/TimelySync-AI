package com.timelysync.config;

import java.util.Properties;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.JavaMailSenderImpl;
import org.springframework.util.StringUtils;

/**
 * Explicit JavaMailSender so Gmail/Brevo SMTP settings are applied consistently.
 * Incomplete credentials do not fail startup — EmailService degrades to in-app fallback.
 */
@Configuration
public class MailSenderConfig {

    private static final Logger logger = LoggerFactory.getLogger(MailSenderConfig.class);

    @Bean
    @ConditionalOnProperty(name = "timelysync.app.mailEnabled", havingValue = "true")
    public JavaMailSender javaMailSender(
            @Value("${spring.mail.host:}") String host,
            @Value("${spring.mail.port:587}") int port,
            @Value("${spring.mail.username:}") String username,
            @Value("${spring.mail.password:}") String password) {

        if (!StringUtils.hasText(host) || !StringUtils.hasText(username) || !StringUtils.hasText(password)) {
            logger.warn(
                    "MAIL_ENABLED=true but MAIL_HOST / MAIL_USERNAME / MAIL_PASSWORD are incomplete — "
                            + "SMTP disabled; forgot-password will use in-app reset-link fallback");
            return new JavaMailSenderImpl();
        }

        JavaMailSenderImpl sender = new JavaMailSenderImpl();
        sender.setHost(host.trim());
        sender.setPort(port);
        sender.setUsername(username.trim());
        // Gmail app passwords are often copied with spaces — strip them.
        sender.setPassword(password.replace(" ", "").trim());

        Properties props = sender.getJavaMailProperties();
        props.put("mail.transport.protocol", "smtp");
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.starttls.enable", "true");
        props.put("mail.smtp.starttls.required", "true");
        props.put("mail.smtp.ssl.trust", host.trim());
        props.put("mail.smtp.connectiontimeout", "10000");
        props.put("mail.smtp.timeout", "10000");
        props.put("mail.smtp.writetimeout", "10000");
        if (port == 465) {
            props.put("mail.smtp.ssl.enable", "true");
            props.put("mail.smtp.socketFactory.port", "465");
            props.put("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
        }

        return sender;
    }
}
