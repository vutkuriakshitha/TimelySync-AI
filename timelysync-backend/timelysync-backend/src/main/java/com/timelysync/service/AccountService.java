package com.timelysync.service;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.timelysync.exception.ForbiddenActionException;
import com.timelysync.exception.ResourceNotFoundException;
import com.timelysync.model.LinkedAccount;
import com.timelysync.model.User;
import com.timelysync.payload.response.AccountDto;
import com.timelysync.repository.LinkedAccountRepository;
import com.timelysync.repository.UserRepository;

@Service
public class AccountService {

    @Autowired
    private LinkedAccountRepository linkedAccountRepository;

    @Autowired
    private UserRepository userRepository;

    public List<AccountDto> getLinkedAccounts(User user) {
        List<AccountDto> accounts = new ArrayList<>();
        accounts.add(mapToAccountDto(user));

        List<LinkedAccount> linked = linkedAccountRepository.findByPrimaryUserId(user.getId());
        for (LinkedAccount link : linked) {
            userRepository.findById(link.getLinkedUserId()).ifPresent(u -> accounts.add(mapToAccountDto(u)));
        }
        return accounts;
    }

    public User switchAccount(User currentUser, String accountId) {
        boolean isOwnAccount = currentUser.getId().equals(accountId);
        boolean isLinked = linkedAccountRepository.findByPrimaryUserIdAndLinkedUserId(currentUser.getId(), accountId).isPresent();

        if (!isOwnAccount && !isLinked) {
            throw new ForbiddenActionException("You do not have access to that account");
        }
        if (!userRepository.existsById(accountId)) {
            throw new ResourceNotFoundException("Account not found");
        }

        currentUser.setCurrentAccountId(accountId);
        return userRepository.save(currentUser);
    }

    private AccountDto mapToAccountDto(User user) {
        return new AccountDto(user.getId(), user.getName(), user.getEmail(), user.getAvatar(), user.getAccountType());
    }
}
