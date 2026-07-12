package com.timelysync.model;

import java.time.LocalDateTime;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "achievements")
public class Achievement {

    @Id
    private String id;

    @Indexed
    private String userId;

    private String title;
    private String description;
    private String type;
    private String icon;
    private String color;
    private Integer xpReward;
    private Boolean unlocked = false;
    private Integer level;
    private LocalDateTime unlockedAt;

    public Achievement() {}

    public Achievement(String userId, String type, String title, String description, String icon, String color, Integer xpReward) {
        this.userId = userId;
        this.type = type;
        this.title = title;
        this.description = description;
        this.icon = icon;
        this.color = color;
        this.xpReward = xpReward;
        this.unlocked = false;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getIcon() { return icon; }
    public void setIcon(String icon) { this.icon = icon; }

    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }

    public Integer getXpReward() { return xpReward; }
    public void setXpReward(Integer xpReward) { this.xpReward = xpReward; }

    public Boolean getUnlocked() { return unlocked; }
    public void setUnlocked(Boolean unlocked) { this.unlocked = unlocked; }

    public Integer getLevel() { return level; }
    public void setLevel(Integer level) { this.level = level; }

    public LocalDateTime getUnlockedAt() { return unlockedAt; }
    public void setUnlockedAt(LocalDateTime unlockedAt) { this.unlockedAt = unlockedAt; }
}
