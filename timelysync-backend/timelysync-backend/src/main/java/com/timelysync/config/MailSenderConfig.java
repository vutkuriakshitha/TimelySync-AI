package com.timelysync.config;

import java.util.Properties;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.JavaMailSenderImpl;
import org.springframework.util.StringUtils;

/**
 * Builds a Gmail-capable {@link JavaMailSender} from environment / .env values only.
 * Does not hardcode credentials.
 */
@Configuration
public class MailSenderConfig {

    private static final Logger logger = LoggerFactory.getLogger(MailSenderConfig.class);

    @Bean
    @ConditionalOnProperty(name = "timelysync.app.mailEnabled", havingValue = "true")
    public JavaMailSender javaMailSender(Environment env,
            @Value("${spring.mail.host:}") String hostProp,
            @Value("${spring.mail.port:587}") int portProp,
            @Value("${spring.mail.username:}") String userProp,
            @Value("${spring.mail.password:}") String passProp,
            @Value("${MAIL_DEBUG:false}") boolean mailDebug) {

        // Resolve from Spring Environment (includes .env via spring-dotenv) and OS env.
        String host = firstNonBlank(hostProp, env.getProperty("MAIL_HOST"), System.getenv("MAIL_HOST"));
        String username = firstNonBlank(userProp, env.getProperty("MAIL_USERNAME"), System.getenv("MAIL_USERNAME"));
        String password = firstNonBlank(passProp, env.getProperty("MAIL_PASSWORD"), System.getenv("MAIL_PASSWORD"));
        int port = portProp > 0 ? portProp : parsePort(env.getProperty("MAIL_PORT"), 587);

        logger.info("Gmail SMTP bean init: host='{}' port={} user='{}' passwordLength={} passwordLoaded={}",
                host, port, username,
                password == null ? 0 : password.replace(" ", "").length(),
                StringUtils.hasText(password));

        if (!StringUtils.hasText(host) || !StringUtils.hasText(username) || !StringUtils.hasText(password)) {
            throw new IllegalStateException(
                    "MAIL_ENABLED=true but Gmail SMTP credentials are incomplete. "
                            + "Set MAIL_HOST, MAIL_USERNAME, and MAIL_PASSWORD (16-char App Password) in .env");
        }

        // Gmail App Passwords are often copied with spaces — strip them.
        String appPassword = password.replace(" ", "").trim();

        JavaMailSenderImpl sender = new JavaMailSenderImpl();
        sender.setHost(host.trim());
        sender.setPort(port);
        sender.setUsername(username.trim());
        sender.setPassword(appPassword);
        sender.setDefaultEncoding("UTF-8");
        sender.setProtocol("smtp");

        Properties props = sender.getJavaMailProperties();
        props.put("mail.transport.protocol", "smtp");
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.connectiontimeout", "15000");
        props.put("mail.smtp.timeout", "15000");
        props.put("mail.smtp.writetimeout", "15000");
        props.put("mail.debug", String.valueOf(mailDebug));

        if (port == 465) {
            // SSL
            props.put("mail.smtp.ssl.enable", "true");
            props.put("mail.smtp.socketFactory.port", "465");
            props.put("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
            props.put("mail.smtp.ssl.trust", host.trim());
            logger.info("Gmail SMTP mode: SSL on port 465");
        } else {
            // STARTTLS (recommended Gmail port 587)
            props.put("mail.smtp.starttls.enable", "true");
            props.put("mail.smtp.starttls.required", "true");
            props.put("mail.smtp.ssl.trust", host.trim());
            props.put("mail.smtp.ssl.protocols", "TLSv1.2");
            logger.info("Gmail SMTP mode: STARTTLS on port {}", port);
        }

        return sender;
    }

    private static String firstNonBlank(String... values) {
        if (values == null) {
            return "";
        }
        for (String v : values) {
            if (StringUtils.hasText(v)) {
                return v;
            }
        }
        return "";
    }

    private static int parsePort(String raw, int fallback) {
        if (!StringUtils.hasText(raw)) {
            return fallback;
        }
        try {
            return Integer.parseInt(raw.trim());
        } catch (NumberFormatException ex) {
            return fallback;
        }
    }
}
