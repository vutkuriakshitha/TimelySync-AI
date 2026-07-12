package com.timelysync.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.timelysync.payload.response.AnalyticsDto;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.service.AnalyticsService;

@RestController
@RequestMapping("/api/analytics")
public class AnalyticsController {

    @Autowired
    private AnalyticsService analyticsService;

    @GetMapping
    public ResponseEntity<AnalyticsDto> getAnalytics(@AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(analyticsService.getAnalytics(userDetails.getUser()));
    }
}
