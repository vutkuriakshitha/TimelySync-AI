package com.timelysync.repository;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.timelysync.model.Task;

public interface TaskRepository extends MongoRepository<Task, String> {

    List<Task> findByUserId(String userId);

    List<Task> findByUserIdAndStatus(String userId, String status);

    List<Task> findByUserIdAndStatusAndDueDateBefore(String userId, String status, LocalDateTime dueDate);

    long countByUserId(String userId);

    long countByUserIdAndStatus(String userId, String status);

    void deleteByUserId(String userId);
}
