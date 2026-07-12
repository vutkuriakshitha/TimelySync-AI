package com.timelysync.service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.timelysync.model.Achievement;
import com.timelysync.model.User;
import com.timelysync.payload.response.AchievementDto;
import com.timelysync.payload.response.UserStatsDto;
import com.timelysync.repository.AchievementRepository;
import com.timelysync.repository.TaskRepository;
import com.timelysync.repository.UserRepository;

@Service
public class UserStatsService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AchievementRepository achievementRepository;

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private NotificationService notificationService;

    public UserStatsDto getUserStats(User user) {
        UserStatsDto stats = new UserStatsDto();

        int streak = refreshStreak(user);
        stats.setStreak(streak);

        List<Achievement> unlocked = achievementRepository.findByUserIdAndUnlockedTrueOrderByUnlockedAtDesc(user.getId());
        stats.setAchievements(unlocked.stream().map(AchievementDto::fromAchievement).collect(Collectors.toList()));

        stats.setLevel(user.getLevel());
        stats.setXp(user.getXpPoints());
        stats.setNextLevelXp(calculateNextLevelXp(user.getLevel()));
        stats.setCoins(user.getXpPoints() / 100);

        return stats;
    }

    private int refreshStreak(User user) {
        if (user.getLastActivityDate() == null) {
            return user.getStreakDays() != null ? user.getStreakDays() : 0;
        }
        long daysBetween = ChronoUnit.DAYS.between(user.getLastActivityDate().toLocalDate(), LocalDateTime.now().toLocalDate());
        if (daysBetween >= 2) {
            user.setStreakDays(0);
            userRepository.save(user);
        }
        return user.getStreakDays() != null ? user.getStreakDays() : 0;
    }

    /** Called whenever a user completes a task - updates streak, awards XP, and checks achievements. */
    public void recordTaskCompletion(User user, boolean onTime) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime last = user.getLastActivityDate();

        if (last == null || ChronoUnit.DAYS.between(last.toLocalDate(), now.toLocalDate()) >= 1) {
            long daysBetween = last == null ? 1 : ChronoUnit.DAYS.between(last.toLocalDate(), now.toLocalDate());
            if (daysBetween == 1) {
                user.setStreakDays((user.getStreakDays() != null ? user.getStreakDays() : 0) + 1);
            } else {
                user.setStreakDays(1);
            }
        }
        user.setLastActivityDate(now);

        int xpGain = onTime ? 50 : 20;
        awardXp(user, xpGain);
        userRepository.save(user);

        long completedCount = taskRepository.countByUserIdAndStatus(user.getId(), "COMPLETED");
        checkAndUnlockAchievement(user, "first_task", null);
        if (completedCount >= 10) checkAndUnlockAchievement(user, "task_complete_10", null);
        if (user.getStreakDays() != null && user.getStreakDays() >= 7) checkAndUnlockAchievement(user, "streak_7", null);
        if (onTime) {
            long onTimeCount = taskRepository.findByUserIdAndStatus(user.getId(), "COMPLETED").size();
            if (onTimeCount >= 5) checkAndUnlockAchievement(user, "on_time_5", null);
        }
    }

    private void awardXp(User user, int xp) {
        user.setXpPoints((user.getXpPoints() != null ? user.getXpPoints() : 0) + xp);
        int nextLevelXp = calculateNextLevelXp(user.getLevel());
        if (user.getXpPoints() >= nextLevelXp) {
            user.setLevel(user.getLevel() + 1);
            notificationService.createNotification(user.getId(), "achievement",
                    "Congratulations! You've reached Level " + user.getLevel() + "!");
        }
    }

    private int calculateNextLevelXp(int currentLevel) {
        return currentLevel * 1000;
    }

    public Achievement checkAndUnlockAchievement(User user, String type, String metadata) {
        Achievement existing = achievementRepository.findByUserIdAndType(user.getId(), type).orElse(null);
        if (existing != null && Boolean.TRUE.equals(existing.getUnlocked())) {
            return null;
        }

        Achievement achievement = existing != null ? existing : new Achievement();
        achievement.setUserId(user.getId());
        achievement.setType(type);
        achievement.setUnlocked(true);
        achievement.setUnlockedAt(LocalDateTime.now());

        switch (type) {
            case "first_task" -> {
                achievement.setTitle("First Steps");
                achievement.setDescription("Completed your first task!");
                achievement.setIcon("star");
                achievement.setColor("warning");
                achievement.setXpReward(100);
            }
            case "task_complete_10" -> {
                achievement.setTitle("Task Master");
                achievement.setDescription("Completed 10 tasks!");
                achievement.setIcon("target");
                achievement.setColor("success");
                achievement.setXpReward(500);
            }
            case "streak_7" -> {
                achievement.setTitle("Weekly Warrior");
                achievement.setDescription("Maintained a 7 day streak!");
                achievement.setIcon("zap");
                achievement.setColor("info");
                achievement.setXpReward(300);
            }
            case "on_time_5" -> {
                achievement.setTitle("Punctual Pro");
                achievement.setDescription("Completed 5 tasks on time!");
                achievement.setIcon("clock");
                achievement.setColor("primary");
                achievement.setXpReward(250);
            }
            default -> {
                return null;
            }
        }

        user.setXpPoints(user.getXpPoints() + achievement.getXpReward());
        userRepository.save(user);
        achievementRepository.save(achievement);

        notificationService.createNotification(user.getId(), "achievement",
                "Achievement Unlocked: " + achievement.getTitle() + "! +" + achievement.getXpReward() + " XP");

        return achievement;
    }
}
