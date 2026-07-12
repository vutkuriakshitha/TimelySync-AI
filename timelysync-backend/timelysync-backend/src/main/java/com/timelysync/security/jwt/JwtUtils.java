package com.timelysync.security.jwt;

import com.timelysync.security.UserDetailsImpl;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Component
public class JwtUtils {
    private static final Logger logger = LoggerFactory.getLogger(JwtUtils.class);
    private static final String INSECURE_DEFAULT = "local-dev-only-insecure-secret-change-me-32chars";

    @Value("${timelysync.app.jwtSecret}")
    private String jwtSecret;

    @Value("${timelysync.app.jwtExpirationMs}")
    private long jwtExpirationMs;

    @PostConstruct
    public void validateSecret() {
        if (jwtSecret == null || jwtSecret.length() < 32) {
            throw new IllegalStateException(
                    "JWT_SECRET must be set and at least 32 characters long. Refusing to start.");
        }
        if (INSECURE_DEFAULT.equals(jwtSecret)) {
            logger.warn("*** SECURITY WARNING: using the default insecure JWT_SECRET. "
                    + "Set the JWT_SECRET environment variable before deploying to production. ***");
        }
    }

    private SecretKey key() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
    }

    public String generateJwtToken(Authentication authentication) {
        UserDetailsImpl userPrincipal = (UserDetailsImpl) authentication.getPrincipal();
        return generateTokenFromEmail(userPrincipal.getUsername());
    }

    public String generateTokenFromEmail(String email) {
        return Jwts.builder()
                .subject(email)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + jwtExpirationMs))
                .signWith(key())
                .compact();
    }

    public long getExpirationMs() {
        return jwtExpirationMs;
    }

    public String getEmailFromJwtToken(String token) {
        return Jwts.parser().verifyWith(key()).build()
                .parseSignedClaims(token).getPayload().getSubject();
    }

    public boolean validateJwtToken(String authToken) {
        try {
            Jwts.parser().verifyWith(key()).build().parseSignedClaims(authToken);
            return true;
        } catch (SecurityException e) {
            logger.warn("Invalid JWT signature: {}", e.getMessage());
        } catch (MalformedJwtException e) {
            logger.warn("Invalid JWT token: {}", e.getMessage());
        } catch (ExpiredJwtException e) {
            logger.info("JWT token is expired: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            logger.warn("JWT token is unsupported: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            logger.warn("JWT claims string is empty: {}", e.getMessage());
        }
        return false;
    }
}
