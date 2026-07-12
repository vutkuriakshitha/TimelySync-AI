package com.timelysync.model;

public class Consequence {
    private String description;
    private Integer probabilityPercent;

    public Consequence() {}

    public Consequence(String description, Integer probabilityPercent) {
        this.description = description;
        this.probabilityPercent = probabilityPercent;
    }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public Integer getProbabilityPercent() { return probabilityPercent; }
    public void setProbabilityPercent(Integer probabilityPercent) { this.probabilityPercent = probabilityPercent; }
}
