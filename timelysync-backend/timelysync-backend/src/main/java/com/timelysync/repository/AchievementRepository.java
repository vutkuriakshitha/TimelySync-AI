package com.timelysync.repository;

import com.timelysync.model.Achievement;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface AchievementRepository extends MongoRepository<Achievement, String> {
    List<Achievement> findByUserIdAndUnlockedTrueOrderByUnlockedAtDesc(String userId);
    Optional<Achievement> findByUserIdAndType(String userId, String type);
    long countByUserIdAndUnlockedTrue(String userId);
}
