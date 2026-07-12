package com.timelysync.payload.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class DeadlineExtractionRequest {
    @NotBlank(message = "Document text is required")
    @Size(max = 500000, message = "Text is too long")
    private String text;

    @Size(max = 255)
    private String documentName;

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getDocumentName() { return documentName; }
    public void setDocumentName(String documentName) { this.documentName = documentName; }
}
