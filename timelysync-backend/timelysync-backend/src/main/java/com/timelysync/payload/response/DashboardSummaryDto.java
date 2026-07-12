package com.timelysync.payload.response;

import java.util.List;
import java.util.Map;

public class DashboardSummaryDto {
    private long totalTasks;
    private long activeTasks;
    private long completedTasks;
    private long overdueTasks;
    private long highRiskTasks;
    private double completionRate;
    private double onTimeRate;
    private double avgRiskScore;
    private List<Map<String, Object>> attentionTasks;
    private List<Map<String, Object>> weeklyTrend;
    private Map<String, Object> cognitiveLoad;

    public long getTotalTasks() { return totalTasks; }
    public void setTotalTasks(long totalTasks) { this.totalTasks = totalTasks; }

    public long getActiveTasks() { return activeTasks; }
    public void setActiveTasks(long activeTasks) { this.activeTasks = activeTasks; }

    public long getCompletedTasks() { return completedTasks; }
    public void setCompletedTasks(long completedTasks) { this.completedTasks = completedTasks; }

    public long getOverdueTasks() { return overdueTasks; }
    public void setOverdueTasks(long overdueTasks) { this.overdueTasks = overdueTasks; }

    public long getHighRiskTasks() { return highRiskTasks; }
    public void setHighRiskTasks(long highRiskTasks) { this.highRiskTasks = highRiskTasks; }

    public double getCompletionRate() { return completionRate; }
    public void setCompletionRate(double completionRate) { this.completionRate = completionRate; }

    public double getOnTimeRate() { return onTimeRate; }
    public void setOnTimeRate(double onTimeRate) { this.onTimeRate = onTimeRate; }

    public double getAvgRiskScore() { return avgRiskScore; }
    public void setAvgRiskScore(double avgRiskScore) { this.avgRiskScore = avgRiskScore; }

    public List<Map<String, Object>> getAttentionTasks() { return attentionTasks; }
    public void setAttentionTasks(List<Map<String, Object>> attentionTasks) { this.attentionTasks = attentionTasks; }

    public List<Map<String, Object>> getWeeklyTrend() { return weeklyTrend; }
    public void setWeeklyTrend(List<Map<String, Object>> weeklyTrend) { this.weeklyTrend = weeklyTrend; }

    public Map<String, Object> getCognitiveLoad() { return cognitiveLoad; }
    public void setCognitiveLoad(Map<String, Object> cognitiveLoad) { this.cognitiveLoad = cognitiveLoad; }
}
