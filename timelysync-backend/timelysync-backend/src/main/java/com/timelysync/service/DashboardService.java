package com.timelysync.service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.timelysync.model.Task;
import com.timelysync.model.User;
import com.timelysync.payload.response.DashboardSummaryDto;
import com.timelysync.repository.TaskRepository;

@Service
public class DashboardService {

    @Autowired
    private TaskRepository taskRepository;

    public DashboardSummaryDto getSummary(User user) {
        List<Task> allTasks = taskRepository.findByUserId(user.getId());
        LocalDateTime now = LocalDateTime.now();

        DashboardSummaryDto dto = new DashboardSummaryDto();
        dto.setTotalTasks(allTasks.size());

        List<Task> active = allTasks.stream().filter(t -> "ACTIVE".equals(t.getStatus())).toList();
        List<Task> completed = allTasks.stream().filter(t -> "COMPLETED".equals(t.getStatus())).toList();
        List<Task> overdue = active.stream()
                .filter(t -> t.getDueDate() != null && t.getDueDate().isBefore(now))
                .toList();
        List<Task> highRisk = active.stream()
                .filter(t -> t.getRiskAnalysis() != null && t.getRiskAnalysis().getRiskScore() != null
                        && t.getRiskAnalysis().getRiskScore() >= 70)
                .toList();

        dto.setActiveTasks(active.size());
        dto.setCompletedTasks(completed.size());
        dto.setOverdueTasks(overdue.size());
        dto.setHighRiskTasks(highRisk.size());

        dto.setCompletionRate(allTasks.isEmpty() ? 0 : round((double) completed.size() / allTasks.size() * 100));

        long onTimeCount = completed.stream()
                .filter(t -> t.getPostAnalysis() != null && t.getPostAnalysis().isCompletedOnTime())
                .count();
        dto.setOnTimeRate(completed.isEmpty() ? 0 : round((double) onTimeCount / completed.size() * 100));

        double avgRisk = active.stream()
                .filter(t -> t.getRiskAnalysis() != null && t.getRiskAnalysis().getRiskScore() != null)
                .mapToInt(t -> t.getRiskAnalysis().getRiskScore())
                .average()
                .orElse(0);
        dto.setAvgRiskScore(round(avgRisk));

        List<Map<String, Object>> attentionTasks = active.stream()
                .filter(t -> t.getRiskAnalysis() != null && t.getRiskAnalysis().getRiskScore() != null
                        && t.getRiskAnalysis().getRiskScore() >= 40)
                .sorted(Comparator.comparingInt((Task t) -> t.getRiskAnalysis().getRiskScore()).reversed())
                .limit(5)
                .map(this::taskToAttentionMap)
                .toList();
        dto.setAttentionTasks(attentionTasks);

        dto.setWeeklyTrend(buildWeeklyTrend(allTasks));

        Map<String, Object> cognitiveLoad = new LinkedHashMap<>();
        cognitiveLoad.put("activeCount", active.size());
        cognitiveLoad.put("highPriorityCount", active.stream().filter(t -> "HIGH".equals(t.getPriority())).count());
        cognitiveLoad.put("level", active.size() > 10 ? "HIGH" : active.size() > 5 ? "MEDIUM" : "LOW");
        dto.setCognitiveLoad(cognitiveLoad);

        return dto;
    }

    private List<Map<String, Object>> buildWeeklyTrend(List<Task> allTasks) {
        List<Map<String, Object>> trend = new ArrayList<>();
        LocalDate today = LocalDate.now();
        for (int i = 6; i >= 0; i--) {
            LocalDate day = today.minusDays(i);
            long completedOnDay = allTasks.stream()
                    .filter(t -> t.getCompletedAt() != null && t.getCompletedAt().toLocalDate().equals(day))
                    .count();
            long createdOnDay = allTasks.stream()
                    .filter(t -> t.getCreatedAt() != null && t.getCreatedAt().toLocalDate().equals(day))
                    .count();
            Map<String, Object> entry = new LinkedHashMap<>();
            entry.put("date", day.toString());
            entry.put("completed", completedOnDay);
            entry.put("created", createdOnDay);
            trend.add(entry);
        }
        return trend;
    }

    private Map<String, Object> taskToAttentionMap(Task t) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("taskId", t.getId());
        map.put("title", t.getTitle());
        map.put("dueDate", t.getDueDate());
        map.put("riskScore", t.getRiskAnalysis().getRiskScore());
        map.put("riskLevel", t.getRiskAnalysis().getRiskLevel());
        map.put("riskFactors", t.getRiskAnalysis().getRiskFactors());
        return map;
    }

    private double round(double value) {
        return Math.round(value * 10.0) / 10.0;
    }
}
