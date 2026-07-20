package com.timelysync.controller;

import jakarta.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.timelysync.payload.request.ChangePasswordRequest;
import com.timelysync.payload.request.ForgotPasswordRequest;
import com.timelysync.payload.request.LoginRequest;
import com.timelysync.payload.request.ResetPasswordRequest;
import com.timelysync.payload.request.SignupRequest;
import com.timelysync.payload.request.UpdateProfileRequest;
import com.timelysync.payload.response.ForgotPasswordResponse;
import com.timelysync.payload.response.JwtResponse;
import com.timelysync.payload.response.MessageResponse;
import com.timelysync.payload.response.UserDto;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.service.AuthService;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private AuthService authService;

    @PostMapping("/register")
    public ResponseEntity<JwtResponse> register(@Valid @RequestBody SignupRequest request) {
        return new ResponseEntity<>(authService.register(request), HttpStatus.CREATED);
    }

    @PostMapping("/login")
    public ResponseEntity<JwtResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }

    @GetMapping("/me")
    public ResponseEntity<UserDto> getCurrentUser(@AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(UserDto.fromUser(userDetails.getUser()));
    }

    @PutMapping("/me")
    public ResponseEntity<UserDto> updateProfile(@AuthenticationPrincipal UserDetailsImpl userDetails,
                                                  @Valid @RequestBody UpdateProfileRequest request) {
        return ResponseEntity.ok(authService.updateProfile(userDetails.getUser(), request));
    }

    @PutMapping("/me/password")
    public ResponseEntity<MessageResponse> changePassword(@AuthenticationPrincipal UserDetailsImpl userDetails,
                                                            @Valid @RequestBody ChangePasswordRequest request) {
        authService.changePassword(userDetails.getUser(), request);
        return ResponseEntity.ok(new MessageResponse("Password updated successfully"));
    }

    @DeleteMapping("/me")
    public ResponseEntity<MessageResponse> deleteAccount(@AuthenticationPrincipal UserDetailsImpl userDetails) {
        authService.deleteAccount(userDetails.getUser());
        return ResponseEntity.ok(new MessageResponse("Account deleted successfully"));
    }

    @PostMapping("/logout")
    public ResponseEntity<MessageResponse> logout() {
        // Stateless JWT - the client is responsible for discarding the token.
        // No server-side session exists to invalidate.
        return ResponseEntity.ok(new MessageResponse("Logged out successfully"));
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<ForgotPasswordResponse> forgotPassword(@Valid @RequestBody ForgotPasswordRequest request) {
        return ResponseEntity.ok(authService.requestPasswordReset(request.getEmail()));
    }

    @PostMapping("/reset-password")
    public ResponseEntity<MessageResponse> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        authService.resetPassword(request.getToken(), request.getNewPassword());
        return ResponseEntity.ok(new MessageResponse("Password has been reset successfully. You can now log in."));
    }
}
