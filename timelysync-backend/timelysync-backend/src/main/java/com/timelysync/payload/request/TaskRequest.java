package com.timelysync.payload.request;

import java.time.LocalDateTime;
import java.util.List;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Task create/update payload. Deliberately does NOT expose userId, id,
 * riskAnalysis, impactSimulation or postAnalysis - those are server
 * controlled to prevent mass-assignment / IDOR vulnerabilities.
 */
public class TaskRequest {

    @NotBlank(message = "Title is required")
    @Size(max = 200)
    private String title;

    @Size(max = 2000)
    private String description;

    @NotBlank(message = "Category is required")
    private String category;

    private String priority = "MEDIUM";
    private String impact = "MEDIUM";
    private String effort = "MEDIUM";

    private LocalDateTime dueDate;
    private List<String> tags;

    @Size(max = 2000)
    private String notes;

    @Size(max = 300)
    private String location;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

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

    public List<String> getTags() { return tags; }
    public void setTags(List<String> tags) { this.tags = tags; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }

    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
}
