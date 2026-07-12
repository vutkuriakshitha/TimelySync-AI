package com.timelysync.model;

public class Cause {
    private String type;
    private Integer percentage;
    private String description;

    public Cause() {}

    public Cause(String type, Integer percentage, String description) {
        this.type = type;
        this.percentage = percentage;
        this.description = description;
    }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public Integer getPercentage() { return percentage; }
    public void setPercentage(Integer percentage) { this.percentage = percentage; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}
