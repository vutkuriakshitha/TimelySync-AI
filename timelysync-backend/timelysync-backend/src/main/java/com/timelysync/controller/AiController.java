package com.timelysync.controller;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import jakarta.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.timelysync.model.Task;
import com.timelysync.payload.request.DeadlineExtractionRequest;
import com.timelysync.payload.request.SmartIntakeRequest;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.service.AiClientService;
import com.timelysync.service.TaskService;

/**
 * Every prediction here is served by the Python ML microservice
 * (see /ai-service) via AiClientService - real trained models, not
 * hand-written if/else heuristics. This controller only shapes the
 * responses for the frontend and enforces per-user data isolation.
 */
@RestController
@RequestMapping("/api/ai")
public class AiController {

    @Autowired
    private TaskService taskService;

    @Autowired
    private AiClientService aiClientService;

    @GetMapping("/failure-predictions")
    public ResponseEntity<List<Map<String, Object>>> getFailurePredictions(@AuthenticationPrincipal UserDetailsImpl userDetails) {
        List<Task> tasks = taskService.getAllUserTasks(userDetails.getUser());
        List<Map<String, Object>> predictions = new ArrayList<>();

        for (Task task : tasks) {
            if (!"ACTIVE".equalsIgnoreCase(task.getStatus()) || task.getDueDate() == null) continue;
            if (task.getRiskAnalysis() == null) continue;

            Integer probability = task.getRiskAnalysis().getRiskScore();
            if (probability == null || probability < 40) continue;

            Map<String, Object> prediction = new LinkedHashMap<>();
            prediction.put("taskId", task.getId());
            prediction.put("title", task.getTitle());
            prediction.put("probability", probability);
            prediction.put("riskLevel", task.getRiskAnalysis().getRiskLevel());
            prediction.put("riskFactors", task.getRiskAnalysis().getRiskFactors());
            prediction.put("modelVersion", task.getRiskAnalysis().getModelVersion());
            predictions.add(prediction);
        }

        predictions.sort(Comparator.comparingInt((Map<String, Object> m) -> (int) m.get("probability")).reversed());
        return ResponseEntity.ok(predictions);
    }

    @PostMapping("/smart-intake")
    public ResponseEntity<Map<String, Object>> smartTaskIntake(@Valid @RequestBody SmartIntakeRequest request) {
        return ResponseEntity.ok(aiClientService.predictIntake(request.getText()));
    }

    @PostMapping("/deadline-extraction")
    public ResponseEntity<Map<String, Object>> extractDeadlines(@Valid @RequestBody DeadlineExtractionRequest request) {
        return ResponseEntity.ok(aiClientService.extractDeadlines(request.getText(), request.getDocumentName()));
    }

    @PostMapping(value = "/document-deadlines", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Map<String, Object>> extractDocumentDeadlines(
            @RequestPart("file") MultipartFile file) {
        return ResponseEntity.ok(aiClientService.extractDocumentDeadlines(file));
    }
}
