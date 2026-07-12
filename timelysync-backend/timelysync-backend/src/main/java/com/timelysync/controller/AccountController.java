package com.timelysync.controller;

import java.util.List;

import jakarta.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.timelysync.payload.request.SwitchAccountRequest;
import com.timelysync.payload.response.AccountDto;
import com.timelysync.payload.response.UserDto;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.service.AccountService;

@RestController
@RequestMapping("/api/accounts")
public class AccountController {

    @Autowired
    private AccountService accountService;

    @GetMapping
    public ResponseEntity<List<AccountDto>> getLinkedAccounts(@AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(accountService.getLinkedAccounts(userDetails.getUser()));
    }

    @PostMapping("/switch")
    public ResponseEntity<UserDto> switchAccount(@Valid @RequestBody SwitchAccountRequest request,
                                                  @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(UserDto.fromUser(accountService.switchAccount(userDetails.getUser(), request.getAccountId())));
    }
}
