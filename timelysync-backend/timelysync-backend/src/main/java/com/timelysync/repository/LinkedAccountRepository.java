package com.timelysync.repository;

import com.timelysync.model.LinkedAccount;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface LinkedAccountRepository extends MongoRepository<LinkedAccount, String> {
    List<LinkedAccount> findByPrimaryUserId(String primaryUserId);
    List<LinkedAccount> findByLinkedUserId(String linkedUserId);
    Optional<LinkedAccount> findByPrimaryUserIdAndLinkedUserId(String primaryUserId, String linkedUserId);
    boolean existsByPrimaryUserIdAndLinkedUserId(String primaryUserId, String linkedUserId);
}
