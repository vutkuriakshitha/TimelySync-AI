package com.timelysync.service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.timelysync.exception.BadRequestException;
import com.timelysync.exception.DuplicateResourceException;
import com.timelysync.model.User;
import com.timelysync.payload.request.ChangePasswordRequest;
import com.timelysync.payload.request.LoginRequest;
import com.timelysync.payload.request.SignupRequest;
import com.timelysync.payload.request.UpdateProfileRequest;
import com.timelysync.payload.response.ForgotPasswordResponse;
import com.timelysync.payload.response.JwtResponse;
import com.timelysync.payload.response.UserDto;
import com.timelysync.repository.UserRepository;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.security.jwt.JwtUtils;

@Service
public class AuthService {

    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);
    private static final int RESET_TOKEN_VALID_MINUTES = 60;
    private static final String FORGOT_PASSWORD_MESSAGE =
            "If an account exists with that email, a password reset link has been sent. Check your inbox and spam folder.";

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtUtils jwtUtils;

    @Autowired
    private EmailService emailService;

    /** When SMTP is unavailable, return a one-time reset link in the API response (local/dev). */
    @Value("${timelysync.app.allowInAppResetFallback:true}")
    private boolean allowInAppResetFallback;

    public JwtResponse register(SignupRequest request) {
        String email = request.getEmail().trim().toLowerCase();
        if (userRepository.existsByEmail(email)) {
            throw new DuplicateResourceException("An account with this email already exists");
        }

        User user = new User();
        user.setEmail(email);
        user.setUsername(email);
        user.setName(request.getName().trim());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setRoles(List.of("ROLE_USER"));
        user.setCreatedAt(LocalDateTime.now());
        userRepository.save(user);

        emailService.sendWelcomeEmail(user.getEmail(), user.getName());

        String token = jwtUtils.generateTokenFromEmail(email);
        return new JwtResponse(token, UserDto.fromUser(user));
    }

    public JwtResponse login(LoginRequest request) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getEmail().trim().toLowerCase(), request.getPassword()));

        SecurityContextHolder.getContext().setAuthentication(authentication);
        UserDetailsImpl principal = (UserDetailsImpl) authentication.getPrincipal();
        String token = jwtUtils.generateJwtToken(authentication);

        return new JwtResponse(token, UserDto.fromUser(principal.getUser()));
    }

    public UserDto updateProfile(User user, UpdateProfileRequest request) {
        if (request.getName() != null && !request.getName().isBlank()) {
            user.setName(request.getName().trim());
        }
        if (request.getBio() != null) {
            user.setBio(request.getBio());
        }
        if (request.getAvatar() != null) {
            user.setAvatar(request.getAvatar());
        }
        User saved = userRepository.save(user);
        return UserDto.fromUser(saved);
    }

    public void changePassword(User user, ChangePasswordRequest request) {
        if (!passwordEncoder.matches(request.getCurrentPassword(), user.getPassword())) {
            throw new BadRequestException("Current password is incorrect");
        }
        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
        userRepository.save(user);
    }

    public void deleteAccount(User user) {
        userRepository.delete(user);
    }

    public ForgotPasswordResponse requestPasswordReset(String email) {
        final String normalized = email == null ? "" : email.trim().toLowerCase();
        final String[] rawTokenHolder = { null };

        userRepository.findByEmail(normalized).ifPresent(user -> {
            String rawToken = generateSecureToken();
            user.setPasswordResetTokenHash(hashToken(rawToken));
            user.setPasswordResetTokenExpiry(LocalDateTime.now().plusMinutes(RESET_TOKEN_VALID_MINUTES));
            userRepository.save(user);
            rawTokenHolder[0] = rawToken;
        });

        // Same outer message whether or not the account exists (anti user-enumeration).
        if (rawTokenHolder[0] == null) {
            return new ForgotPasswordResponse(FORGOT_PASSWORD_MESSAGE, false, null);
        }

        String resetLink = emailService.buildPasswordResetLink(rawTokenHolder[0]);

        if (!emailService.isMailConfigured()) {
            return fallbackOrSilent(normalized, resetLink, "SMTP not configured");
        }

        boolean delivered = emailService.sendPasswordResetEmail(normalized, rawTokenHolder[0]);
        if (delivered) {
            return new ForgotPasswordResponse(FORGOT_PASSWORD_MESSAGE, true, null);
        }

        return fallbackOrSilent(normalized, resetLink, "SMTP send failed");
    }

    private ForgotPasswordResponse fallbackOrSilent(String email, String resetLink, String reason) {
        if (allowInAppResetFallback) {
            logger.warn("{} for {} — returning in-app reset link", reason, email);
            return new ForgotPasswordResponse(
                    "We could not send email right now. Use the reset link below (expires in 1 hour).",
                    false,
                    resetLink);
        }

        logger.warn("{} for {} — clearing unused reset token (in-app fallback disabled)", reason, email);
        userRepository.findByEmail(email).ifPresent(user -> {
            user.setPasswordResetTokenHash(null);
            user.setPasswordResetTokenExpiry(null);
            userRepository.save(user);
        });
        return new ForgotPasswordResponse(FORGOT_PASSWORD_MESSAGE, false, null);
    }

    public void resetPassword(String rawToken, String newPassword) {
        String tokenHash = hashToken(rawToken);
        User user = userRepository.findByPasswordResetTokenHash(tokenHash)
                .orElseThrow(() -> new BadRequestException("Invalid or expired reset token"));

        if (user.getPasswordResetTokenExpiry() == null || user.getPasswordResetTokenExpiry().isBefore(LocalDateTime.now())) {
            throw new BadRequestException("Invalid or expired reset token");
        }

        user.setPassword(passwordEncoder.encode(newPassword));
        user.setPasswordResetTokenHash(null);
        user.setPasswordResetTokenExpiry(null);
        userRepository.save(user);
    }

    private String generateSecureToken() {
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[32];
        random.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private String hashToken(String token) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(token.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 not available", e);
        }
    }
}
