package com.timelysync.payload.response;

import java.util.List;

public class UserStatsDto {
    private Integer streak;
    private List<AchievementDto> achievements;
    private Integer level;
    private Integer xp;
    private Integer nextLevelXp;
    private Integer coins;

    public UserStatsDto() {}

    public Integer getStreak() { return streak; }
    public void setStreak(Integer streak) { this.streak = streak; }

    public List<AchievementDto> getAchievements() { return achievements; }
    public void setAchievements(List<AchievementDto> achievements) { this.achievements = achievements; }

    public Integer getLevel() { return level; }
    public void setLevel(Integer level) { this.level = level; }

    public Integer getXp() { return xp; }
    public void setXp(Integer xp) { this.xp = xp; }

    public Integer getNextLevelXp() { return nextLevelXp; }
    public void setNextLevelXp(Integer nextLevelXp) { this.nextLevelXp = nextLevelXp; }

    public Integer getCoins() { return coins; }
    public void setCoins(Integer coins) { this.coins = coins; }
}
