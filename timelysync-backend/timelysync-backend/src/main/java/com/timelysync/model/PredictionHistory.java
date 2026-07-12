package com.timelysync.model;

import java.time.LocalDateTime;
import java.util.Map;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

/**
 * Audit log of every ML prediction served to a user, persisted so the AI
 * microservice (and future retraining jobs) can evaluate real outcomes
 * against predictions over time.
 */
@Document(collection = "prediction_history")
public class PredictionHistory {

    @Id
    private String id;

    @Indexed
    private String userId;

    private String taskId;

    /** failure | intake | impact | postanalysis */
    private String predictionType;

    private Map<String, Object> inputFeatures;
    private Map<String, Object> output;
    private String modelVersion;
    private LocalDateTime createdAt = LocalDateTime.now();

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getTaskId() { return taskId; }
    public void setTaskId(String taskId) { this.taskId = taskId; }

    public String getPredictionType() { return predictionType; }
    public void setPredictionType(String predictionType) { this.predictionType = predictionType; }

    public Map<String, Object> getInputFeatures() { return inputFeatures; }
    public void setInputFeatures(Map<String, Object> inputFeatures) { this.inputFeatures = inputFeatures; }

    public Map<String, Object> getOutput() { return output; }
    public void setOutput(Map<String, Object> output) { this.output = output; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
