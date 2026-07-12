package com.timelysync.service;

import java.time.LocalDate;
import java.time.temporal.WeekFields;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.timelysync.model.Task;
import com.timelysync.model.User;
import com.timelysync.payload.response.AnalyticsDto;
import com.timelysync.repository.TaskRepository;

/**
 * Computes real, database-driven accountability/analytics metrics for a
 * user (weekly completion trend, category breakdown, category performance,
 * overall compliance score). Replaces the previous fully-hardcoded
 * Accountability page data.
 */
@Service
public class AnalyticsService {

    @Autowired
    private TaskRepository taskRepository;

    public AnalyticsDto getAnalytics(User user) {
        List<Task> allTasks = taskRepository.findByUserId(user.getId());
        AnalyticsDto dto = new AnalyticsDto();

        List<Task> completed = allTasks.stream().filter(t -> "COMPLETED".equals(t.getStatus())).toList();
        List<Task> active = allTasks.stream().filter(t -> "ACTIVE".equals(t.getStatus())).toList();
        List<Task> overdue = active.stream()
                .filter(t -> t.getDueDate() != null && t.getDueDate().isBefore(java.time.LocalDateTime.now()))
                .toList();

        dto.setCompletedTasks(completed.size());
        dto.setActiveTasks(active.size());
        dto.setOverdueTasks(overdue.size());

        long onTime = completed.stream()
                .filter(t -> t.getPostAnalysis() != null && t.getPostAnalysis().isCompletedOnTime())
                .count();
        double compliance = completed.isEmpty() ? 0 : ((double) onTime / completed.size()) * 100;
        dto.setComplianceScore(Math.round(compliance * 10.0) / 10.0);

        dto.setWeeklyCompletion(buildWeeklyCompletion(completed));
        dto.setCategoryBreakdown(buildCategoryBreakdown(allTasks));
        dto.setCategoryPerformance(buildCategoryPerformance(allTasks));

        return dto;
    }

    private List<Map<String, Object>> buildWeeklyCompletion(List<Task> completed) {
        WeekFields weekFields = WeekFields.of(Locale.getDefault());
        LocalDate today = LocalDate.now();

        Map<Integer, Long> countsByWeekOffset = new LinkedHashMap<>();
        for (int i = 5; i >= 0; i--) {
            countsByWeekOffset.put(i, 0L);
        }

        for (Task t : completed) {
            if (t.getCompletedAt() == null) continue;
            LocalDate completedDate = t.getCompletedAt().toLocalDate();
            long weeksAgo = java.time.temporal.ChronoUnit.WEEKS.between(
                    completedDate.with(weekFields.dayOfWeek(), 1),
                    today.with(weekFields.dayOfWeek(), 1));
            if (weeksAgo >= 0 && weeksAgo <= 5) {
                int key = (int) weeksAgo;
                countsByWeekOffset.merge(key, 1L, Long::sum);
            }
        }

        return countsByWeekOffset.entrySet().stream()
                .sorted((a, b) -> b.getKey().compareTo(a.getKey()))
                .map(e -> {
                    Map<String, Object> m = new LinkedHashMap<>();
                    m.put("weekLabel", e.getKey() == 0 ? "This week" : e.getKey() + " week(s) ago");
                    m.put("completed", e.getValue());
                    return m;
                })
                .collect(Collectors.toList());
    }

    private List<Map<String, Object>> buildCategoryBreakdown(List<Task> tasks) {
        Map<String, Long> counts = tasks.stream()
                .collect(Collectors.groupingBy(
                        t -> t.getCategory() != null ? t.getCategory() : "UNCATEGORIZED",
                        Collectors.counting()));
        long total = tasks.size();

        return counts.entrySet().stream()
                .map(e -> {
                    Map<String, Object> m = new LinkedHashMap<>();
                    m.put("category", e.getKey());
                    m.put("count", e.getValue());
                    m.put("percentage", total == 0 ? 0 : Math.round((double) e.getValue() / total * 1000.0) / 10.0);
                    return m;
                })
                .collect(Collectors.toList());
    }

    private List<Map<String, Object>> buildCategoryPerformance(List<Task> tasks) {
        Map<String, List<Task>> byCategory = tasks.stream()
                .collect(Collectors.groupingBy(t -> t.getCategory() != null ? t.getCategory() : "UNCATEGORIZED"));

        return byCategory.entrySet().stream()
                .map(e -> {
                    List<Task> categoryTasks = e.getValue();
                    long completedCount = categoryTasks.stream().filter(t -> "COMPLETED".equals(t.getStatus())).count();
                    long onTimeCount = categoryTasks.stream()
                            .filter(t -> t.getPostAnalysis() != null && t.getPostAnalysis().isCompletedOnTime())
                            .count();
                    Map<String, Object> m = new LinkedHashMap<>();
                    m.put("category", e.getKey());
                    m.put("totalTasks", categoryTasks.size());
                    m.put("completionRate", categoryTasks.isEmpty() ? 0
                            : Math.round((double) completedCount / categoryTasks.size() * 1000.0) / 10.0);
                    m.put("onTimeRate", completedCount == 0 ? 0
                            : Math.round((double) onTimeCount / completedCount * 1000.0) / 10.0);
                    return m;
                })
                .collect(Collectors.toList());
    }
}
