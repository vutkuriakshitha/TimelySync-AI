package com.timelysync.payload.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class SmartIntakeRequest {
    @NotBlank(message = "Text is required")
    @Size(max = 50000)
    private String text;

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }
}
