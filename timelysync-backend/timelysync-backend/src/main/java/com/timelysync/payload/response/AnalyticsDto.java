package com.timelysync.payload.response;

import java.util.List;
import java.util.Map;

public class AnalyticsDto {
    private double complianceScore;
    private long completedTasks;
    private long overdueTasks;
    private long activeTasks;
    private List<Map<String, Object>> weeklyCompletion;
    private List<Map<String, Object>> categoryBreakdown;
    private List<Map<String, Object>> categoryPerformance;

    public double getComplianceScore() { return complianceScore; }
    public void setComplianceScore(double complianceScore) { this.complianceScore = complianceScore; }

    public long getCompletedTasks() { return completedTasks; }
    public void setCompletedTasks(long completedTasks) { this.completedTasks = completedTasks; }

    public long getOverdueTasks() { return overdueTasks; }
    public void setOverdueTasks(long overdueTasks) { this.overdueTasks = overdueTasks; }

    public long getActiveTasks() { return activeTasks; }
    public void setActiveTasks(long activeTasks) { this.activeTasks = activeTasks; }

    public List<Map<String, Object>> getWeeklyCompletion() { return weeklyCompletion; }
    public void setWeeklyCompletion(List<Map<String, Object>> weeklyCompletion) { this.weeklyCompletion = weeklyCompletion; }

    public List<Map<String, Object>> getCategoryBreakdown() { return categoryBreakdown; }
    public void setCategoryBreakdown(List<Map<String, Object>> categoryBreakdown) { this.categoryBreakdown = categoryBreakdown; }

    public List<Map<String, Object>> getCategoryPerformance() { return categoryPerformance; }
    public void setCategoryPerformance(List<Map<String, Object>> categoryPerformance) { this.categoryPerformance = categoryPerformance; }
}
