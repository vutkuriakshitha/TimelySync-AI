package com.timelysync.model;

import java.time.LocalDateTime;
import java.util.List;

public class RiskAnalysis {

    private Integer riskScore;
    private String riskLevel;
    private List<String> riskFactors;
    private String modelVersion;
    private LocalDateTime computedAt;

    public RiskAnalysis() {}

    public RiskAnalysis(Integer riskScore, String riskLevel, List<String> riskFactors, String modelVersion) {
        this.riskScore = riskScore;
        this.riskLevel = riskLevel;
        this.riskFactors = riskFactors;
        this.modelVersion = modelVersion;
        this.computedAt = LocalDateTime.now();
    }

    public Integer getRiskScore() { return riskScore; }
    public void setRiskScore(Integer riskScore) { this.riskScore = riskScore; }

    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }

    public List<String> getRiskFactors() { return riskFactors; }
    public void setRiskFactors(List<String> riskFactors) { this.riskFactors = riskFactors; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public LocalDateTime getComputedAt() { return computedAt; }
    public void setComputedAt(LocalDateTime computedAt) { this.computedAt = computedAt; }
}
