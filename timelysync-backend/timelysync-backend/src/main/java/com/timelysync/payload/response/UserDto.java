package com.timelysync.payload.response;

import java.time.LocalDateTime;
import java.util.List;

import com.timelysync.model.User;

public class UserDto {
    private String id;
    private String username;
    private String email;
    private String name;
    private String bio;
    private String avatar;
    private String accountType;
    private Integer streakDays;
    private Integer level;
    private Integer xpPoints;
    private List<String> roles;
    private LocalDateTime createdAt;

    public static UserDto fromUser(User user) {
        UserDto dto = new UserDto();
        dto.id = user.getId();
        dto.username = user.getUsername();
        dto.email = user.getEmail();
        dto.name = user.getName();
        dto.bio = user.getBio();
        dto.avatar = user.getAvatar();
        dto.accountType = user.getAccountType();
        dto.streakDays = user.getStreakDays();
        dto.level = user.getLevel();
        dto.xpPoints = user.getXpPoints();
        dto.roles = user.getRoles();
        dto.createdAt = user.getCreatedAt();
        return dto;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }

    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }

    public String getAccountType() { return accountType; }
    public void setAccountType(String accountType) { this.accountType = accountType; }

    public Integer getStreakDays() { return streakDays; }
    public void setStreakDays(Integer streakDays) { this.streakDays = streakDays; }

    public Integer getLevel() { return level; }
    public void setLevel(Integer level) { this.level = level; }

    public Integer getXpPoints() { return xpPoints; }
    public void setXpPoints(Integer xpPoints) { this.xpPoints = xpPoints; }

    public List<String> getRoles() { return roles; }
    public void setRoles(List<String> roles) { this.roles = roles; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
