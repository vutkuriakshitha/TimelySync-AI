package com.timelysync.payload.response;

import java.time.LocalDateTime;

import com.timelysync.model.Notification;

public class NotificationDto {
    private String id;
    private String type;
    private String message;
    private Boolean read;
    private LocalDateTime createdAt;
    private String metadata;

    public static NotificationDto fromNotification(Notification n) {
        NotificationDto dto = new NotificationDto();
        dto.id = n.getId();
        dto.type = n.getType();
        dto.message = n.getMessage();
        dto.read = n.getRead();
        dto.createdAt = n.getCreatedAt();
        dto.metadata = n.getMetadata();
        return dto;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public Boolean getRead() { return read; }
    public void setRead(Boolean read) { this.read = read; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public String getMetadata() { return metadata; }
    public void setMetadata(String metadata) { this.metadata = metadata; }
}
