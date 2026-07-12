package com.timelysync.model;

import java.util.List;

public class ImpactSimulation {
    private String severityLevel;
    private String category;
    private List<Consequence> consequences;
    private String modelVersion;

    public ImpactSimulation() {}

    public ImpactSimulation(String severityLevel, String category, List<Consequence> consequences, String modelVersion) {
        this.severityLevel = severityLevel;
        this.category = category;
        this.consequences = consequences;
        this.modelVersion = modelVersion;
    }

    public String getSeverityLevel() { return severityLevel; }
    public void setSeverityLevel(String severityLevel) { this.severityLevel = severityLevel; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public List<Consequence> getConsequences() { return consequences; }
    public void setConsequences(List<Consequence> consequences) { this.consequences = consequences; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }
}
