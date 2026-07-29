package com.timelysync.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.EnumerablePropertySource;
import org.springframework.core.env.Environment;
import org.springframework.core.env.PropertySource;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.JavaMailSenderImpl;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

/**
 * Verifies Gmail SMTP env vars are loaded and logs a safe summary at startup.
 */
@Component
public class MailStartupCheck implements ApplicationRunner {

    private static final Logger logger = LoggerFactory.getLogger(MailStartupCheck.class);

    private final Environment environment;
    private final JavaMailSender mailSender; // may be null if MAIL_ENABLED!=true

    public MailStartupCheck(Environment environment,
            org.springframework.beans.factory.ObjectProvider<JavaMailSender> mailSenderProvider) {
        this.environment = environment;
        this.mailSender = mailSenderProvider.getIfAvailable();
    }

    @Override
    public void run(ApplicationArguments args) {
        String mailEnabledRaw = environment.getProperty("MAIL_ENABLED", "");
        String springEnabled = environment.getProperty("timelysync.app.mailEnabled", "");
        String host = environment.getProperty("spring.mail.host", "");
        String port = environment.getProperty("spring.mail.port", "");
        String user = environment.getProperty("spring.mail.username", "");
        String pass = environment.getProperty("spring.mail.password", "");
        String from = environment.getProperty("timelysync.app.mailFrom", "");
        String mailHostEnv = environment.getProperty("MAIL_HOST", "");
        String mailUserEnv = environment.getProperty("MAIL_USERNAME", "");
        String mailPassEnv = environment.getProperty("MAIL_PASSWORD", "");

        logger.info("=== Gmail SMTP env load check ===");
        logger.info("MAIL_ENABLED(raw)='{}' timelysync.app.mailEnabled='{}'", mailEnabledRaw, springEnabled);
        logger.info("MAIL_HOST(env)='{}' spring.mail.host='{}'", mailHostEnv, host);
        logger.info("MAIL_PORT → spring.mail.port='{}'", port);
        logger.info("MAIL_USERNAME(env)='{}' spring.mail.username='{}'", mailUserEnv, user);
        logger.info("MAIL_FROM → timelysync.app.mailFrom='{}'", from);
        logger.info("MAIL_PASSWORD loaded={} length={} (value never logged)",
                StringUtils.hasText(pass) || StringUtils.hasText(mailPassEnv),
                StringUtils.hasText(pass) ? pass.replace(" ", "").length()
                        : (StringUtils.hasText(mailPassEnv) ? mailPassEnv.replace(" ", "").length() : 0));

        if (environment instanceof ConfigurableEnvironment configurable) {
            for (PropertySource<?> ps : configurable.getPropertySources()) {
                if (ps.getName() != null && (ps.getName().toLowerCase().contains("dotenv")
                        || ps.getName().toLowerCase().contains(".env")
                        || ps.getName().contains("application-secrets"))) {
                    logger.info("PropertySource present: {} ({})", ps.getName(), ps.getClass().getSimpleName());
                    if (ps instanceof EnumerablePropertySource<?> eps) {
                        for (String name : eps.getPropertyNames()) {
                            if (name.toUpperCase().contains("MAIL")) {
                                Object val = eps.getProperty(name);
                                if (name.toUpperCase().contains("PASSWORD") || name.toUpperCase().contains("SECRET")) {
                                    logger.info("  {} = <set length={}>", name,
                                            val == null ? 0 : String.valueOf(val).replace(" ", "").length());
                                } else {
                                    logger.info("  {} = {}", name, val);
                                }
                            }
                        }
                    }
                }
            }
        }

        if (mailSender instanceof JavaMailSenderImpl impl) {
            logger.info("JavaMailSender bean: host={} port={} username={} passwordSet={}",
                    impl.getHost(), impl.getPort(), impl.getUsername(),
                    StringUtils.hasText(impl.getPassword()));
        } else if (mailSender == null) {
            logger.warn("JavaMailSender bean NOT created (MAIL_ENABLED must be true)");
        } else {
            logger.info("JavaMailSender bean type={}", mailSender.getClass().getName());
        }
        logger.info("=== end Gmail SMTP env load check ===");
    }
}
