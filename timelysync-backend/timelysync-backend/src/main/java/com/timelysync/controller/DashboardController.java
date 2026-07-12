package com.timelysync.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.timelysync.payload.response.DashboardSummaryDto;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.service.DashboardService;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    @Autowired
    private DashboardService dashboardService;

    @GetMapping("/summary")
    public ResponseEntity<DashboardSummaryDto> getDashboardSummary(@AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(dashboardService.getSummary(userDetails.getUser()));
    }
}
