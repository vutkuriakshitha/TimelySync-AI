package com.timelysync.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

/**
 * Confirms SMTP is wired at startup without logging secrets.
 */
@Component
public class MailStartupCheck implements ApplicationRunner {

    private static final Logger logger = LoggerFactory.getLogger(MailStartupCheck.class);

    @Value("${spring.mail.host:}")
    private String host;

    @Value("${spring.mail.username:}")
    private String username;

    @Value("${spring.mail.password:}")
    private String password;

    @Value("${timelysync.app.mailEnabled:false}")
    private boolean mailEnabled;

    @Value("${timelysync.app.allowInAppResetFallback:true}")
    private boolean allowInAppResetFallback;

    @Override
    public void run(ApplicationArguments args) {
        boolean ready = mailEnabled
                && StringUtils.hasText(host)
                && StringUtils.hasText(username)
                && StringUtils.hasText(password);

        if (ready) {
            logger.info("SMTP ready: host={} user={} passwordLength={}",
                    host, username, password.length());
        } else {
            logger.warn("SMTP NOT ready — forgot-password emails will not send. "
                    + "In-app reset-link fallback is {}. "
                    + "Set MAIL_* in .env (enabled={}, hostSet={}, userSet={}, passwordSet={})",
                    allowInAppResetFallback ? "ON" : "OFF",
                    mailEnabled,
                    StringUtils.hasText(host),
                    StringUtils.hasText(username),
                    StringUtils.hasText(password));
        }
    }
}
