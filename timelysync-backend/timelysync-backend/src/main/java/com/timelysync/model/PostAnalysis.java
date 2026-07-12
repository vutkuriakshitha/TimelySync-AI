package com.timelysync.model;

import java.util.List;

public class PostAnalysis {
    private boolean completedOnTime;
    private long daysLate;
    private List<Cause> causes;
    private String recommendation;
    private String modelVersion;

    public PostAnalysis() {}

    public PostAnalysis(boolean completedOnTime, long daysLate, List<Cause> causes, String recommendation, String modelVersion) {
        this.completedOnTime = completedOnTime;
        this.daysLate = daysLate;
        this.causes = causes;
        this.recommendation = recommendation;
        this.modelVersion = modelVersion;
    }

    public boolean isCompletedOnTime() { return completedOnTime; }
    public void setCompletedOnTime(boolean completedOnTime) { this.completedOnTime = completedOnTime; }

    public long getDaysLate() { return daysLate; }
    public void setDaysLate(long daysLate) { this.daysLate = daysLate; }

    public List<Cause> getCauses() { return causes; }
    public void setCauses(List<Cause> causes) { this.causes = causes; }

    public String getRecommendation() { return recommendation; }
    public void setRecommendation(String recommendation) { this.recommendation = recommendation; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }
}
