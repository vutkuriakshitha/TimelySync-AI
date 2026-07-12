package com.timelysync.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.timelysync.payload.response.UserStatsDto;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.service.UserStatsService;

@RestController
@RequestMapping("/api/stats")
public class UserStatsController {

    @Autowired
    private UserStatsService userStatsService;

    @GetMapping
    public ResponseEntity<UserStatsDto> getStats(@AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(userStatsService.getUserStats(userDetails.getUser()));
    }
}
