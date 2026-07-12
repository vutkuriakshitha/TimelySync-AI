package com.timelysync.repository;

import com.timelysync.model.PredictionHistory;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PredictionHistoryRepository extends MongoRepository<PredictionHistory, String> {
}
