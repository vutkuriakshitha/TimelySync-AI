package com.timelysync.payload.response;

import java.time.LocalDateTime;

import com.timelysync.model.Achievement;

public class AchievementDto {
    private String id;
    private String title;
    private String description;
    private String type;
    private String icon;
    private String color;
    private Integer xpReward;
    private Boolean unlocked;
    private Integer level;
    private LocalDateTime unlockedAt;

    public static AchievementDto fromAchievement(Achievement a) {
        AchievementDto dto = new AchievementDto();
        dto.id = a.getId();
        dto.title = a.getTitle();
        dto.description = a.getDescription();
        dto.type = a.getType();
        dto.icon = a.getIcon();
        dto.color = a.getColor();
        dto.xpReward = a.getXpReward();
        dto.unlocked = a.getUnlocked();
        dto.level = a.getLevel();
        dto.unlockedAt = a.getUnlockedAt();
        return dto;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

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
