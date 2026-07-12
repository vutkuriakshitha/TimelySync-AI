package com.timelysync.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "tasks")
public class Task {

    @Id
    private String id;

    @Indexed
    private String userId;

    private String title;
    private String description;

    /** ACTIVE | COMPLETED */
    private String status = "ACTIVE";

    /** ACADEMIC | OPPORTUNITY | PERSONAL_GOAL | EVENT */
    private String category;

    /** HIGH | MEDIUM | LOW */
    private String priority;

    /** HIGH | MEDIUM | LOW - impact if the deadline is missed */
    private String impact;

    /** HIGH | MEDIUM | LOW - effort required */
    private String effort;

    private LocalDateTime dueDate;
    private LocalDateTime createdAt = LocalDateTime.now();
    private LocalDateTime updatedAt = LocalDateTime.now();
    private LocalDateTime completedAt;

    private List<String> tags = new ArrayList<>();
    private String notes;
    private String location;

    private List<Subtask> subtasks = new ArrayList<>();

    private String proofFileName;
    private String proofUrl;

    private RiskAnalysis riskAnalysis;
    private ImpactSimulation impactSimulation;
    private PostAnalysis postAnalysis;

    public Task() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getPriority() { return priority; }
    public void setPriority(String priority) { this.priority = priority; }

    public String getImpact() { return impact; }
    public void setImpact(String impact) { this.impact = impact; }

    public String getEffort() { return effort; }
    public void setEffort(String effort) { this.effort = effort; }

    public LocalDateTime getDueDate() { return dueDate; }
    public void setDueDate(LocalDateTime dueDate) { this.dueDate = dueDate; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public LocalDateTime getCompletedAt() { return completedAt; }
    public void setCompletedAt(LocalDateTime completedAt) { this.completedAt = completedAt; }

    public List<String> getTags() { return tags; }
    public void setTags(List<String> tags) { this.tags = tags; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }

    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }

    public List<Subtask> getSubtasks() { return subtasks; }
    public void setSubtasks(List<Subtask> subtasks) { this.subtasks = subtasks; }

    public String getProofFileName() { return proofFileName; }
    public void setProofFileName(String proofFileName) { this.proofFileName = proofFileName; }

    public String getProofUrl() { return proofUrl; }
    public void setProofUrl(String proofUrl) { this.proofUrl = proofUrl; }

    public RiskAnalysis getRiskAnalysis() { return riskAnalysis; }
    public void setRiskAnalysis(RiskAnalysis riskAnalysis) { this.riskAnalysis = riskAnalysis; }

    public ImpactSimulation getImpactSimulation() { return impactSimulation; }
    public void setImpactSimulation(ImpactSimulation impactSimulation) { this.impactSimulation = impactSimulation; }

    public PostAnalysis getPostAnalysis() { return postAnalysis; }
    public void setPostAnalysis(PostAnalysis postAnalysis) { this.postAnalysis = postAnalysis; }
}
