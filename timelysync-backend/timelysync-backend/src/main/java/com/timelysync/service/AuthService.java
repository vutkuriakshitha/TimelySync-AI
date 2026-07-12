package com.timelysync.service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
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
import com.timelysync.payload.response.JwtResponse;
import com.timelysync.payload.response.UserDto;
import com.timelysync.repository.UserRepository;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.security.jwt.JwtUtils;

@Service
public class AuthService {

    private static final int RESET_TOKEN_VALID_MINUTES = 60;

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

    public void requestPasswordReset(String email) {
        userRepository.findByEmail(email.trim().toLowerCase()).ifPresent(user -> {
            String rawToken = generateSecureToken();
            user.setPasswordResetTokenHash(hashToken(rawToken));
            user.setPasswordResetTokenExpiry(LocalDateTime.now().plusMinutes(RESET_TOKEN_VALID_MINUTES));
            userRepository.save(user);
            emailService.sendPasswordResetEmail(user.getEmail(), rawToken);
        });
        // Always behave the same way whether or not the email exists, to avoid
        // leaking which email addresses are registered (user enumeration).
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
