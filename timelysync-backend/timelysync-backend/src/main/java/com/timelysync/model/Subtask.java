package com.timelysync.model;

import java.time.LocalDateTime;
import java.util.UUID;

public class Subtask {

    private String id = UUID.randomUUID().toString();
    private String title;
    private boolean completed = false;
    private LocalDateTime dueDate;

    public Subtask() {}

    public Subtask(String title, LocalDateTime dueDate) {
        this.title = title;
        this.dueDate = dueDate;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public boolean isCompleted() { return completed; }
    public void setCompleted(boolean completed) { this.completed = completed; }

    public LocalDateTime getDueDate() { return dueDate; }
    public void setDueDate(LocalDateTime dueDate) { this.dueDate = dueDate; }
}
