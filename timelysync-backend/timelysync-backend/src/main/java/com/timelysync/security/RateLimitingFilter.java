package com.timelysync.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Lightweight in-memory sliding-window rate limiter that protects the
 * authentication endpoints (login/register/forgot-password) from brute
 * force / credential stuffing. This is process-local, which is adequate
 * for a single instance; for a horizontally scaled deployment this should
 * be backed by a shared store such as Redis (see README / future work).
 */
@Component
public class RateLimitingFilter extends OncePerRequestFilter {

    @Value("${timelysync.app.rateLimit.maxRequests:10}")
    private int maxRequests;

    @Value("${timelysync.app.rateLimit.windowMs:60000}")
    private long windowMs;

    private static class Bucket {
        AtomicInteger count = new AtomicInteger(0);
        volatile long windowStart = System.currentTimeMillis();
    }

    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getServletPath();
        return !(path.startsWith("/api/auth/login")
                || path.startsWith("/api/auth/register")
                || path.startsWith("/api/auth/forgot-password")
                || path.startsWith("/api/auth/reset-password"));
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String clientKey = resolveClientKey(request);
        Bucket bucket = buckets.computeIfAbsent(clientKey, k -> new Bucket());

        long now = System.currentTimeMillis();
        synchronized (bucket) {
            if (now - bucket.windowStart > windowMs) {
                bucket.windowStart = now;
                bucket.count.set(0);
            }
        }

        int currentCount = bucket.count.incrementAndGet();
        if (currentCount > maxRequests) {
            response.setStatus(429);
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            Map<String, Object> body = new LinkedHashMap<>();
            body.put("timestamp", Instant.now().toString());
            body.put("status", 429);
            body.put("error", "Too Many Requests");
            body.put("message", "Too many attempts. Please try again later.");
            new ObjectMapper().writeValue(response.getOutputStream(), body);
            return;
        }

        filterChain.doFilter(request, response);
    }

    private String resolveClientKey(HttpServletRequest request) {
        String forwardedFor = request.getHeader("X-Forwarded-For");
        if (forwardedFor != null && !forwardedFor.isBlank()) {
            return forwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
