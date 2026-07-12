package com.timelysync.repository;

import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;
import com.timelysync.model.User;

public interface UserRepository extends MongoRepository<User, String> {

    Optional<User> findByUsername(String username);

    Optional<User> findByEmail(String email);

    Boolean existsByUsername(String username);

    Boolean existsByEmail(String email);

    Optional<User> findByPasswordResetTokenHash(String passwordResetTokenHash);
}
