package com.timelysync.service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import com.timelysync.model.Cause;
import com.timelysync.model.Consequence;
import com.timelysync.model.ImpactSimulation;
import com.timelysync.model.PostAnalysis;
import com.timelysync.model.PredictionHistory;
import com.timelysync.model.RiskAnalysis;
import com.timelysync.model.Task;
import com.timelysync.repository.PredictionHistoryRepository;

/**
 * Thin REST client to the Python (FastAPI) machine-learning microservice
 * that owns every predictive feature in the product (failure risk,
 * smart-intake NLP classification, impact simulation, post-completion root
 * cause analysis). Every prediction is trained by real scikit-learn models
 * (see ai-service/), never hand-written if/else heuristics.
 *
 * If the ML service is temporarily unreachable, we degrade gracefully with
 * a clearly-labelled conservative fallback rather than crashing the request
 * - this is a resilience requirement for a production system that must not
 * go down just because a downstream dependency is briefly unavailable.
 */
@Service
public class AiClientService {

    private static final Logger logger = LoggerFactory.getLogger(AiClientService.class);
    private static final String FALLBACK_MODEL_VERSION = "fallback-v1";

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private PredictionHistoryRepository predictionHistoryRepository;

    @Value("${timelysync.ai.serviceUrl:http://localhost:8000}")
    private String aiServiceUrl;

    @Value("${timelysync.ai.internalApiKey:}")
    private String internalApiKey;

    private HttpHeaders headers() {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        if (internalApiKey != null && !internalApiKey.isBlank()) {
            headers.set("X-Internal-Api-Key", internalApiKey);
        }
        return headers;
    }

    @SuppressWarnings("unchecked")
    public RiskAnalysis predictFailureRisk(Task task, double userCompletionRate, double userOnTimeRate) {
        Map<String, Object> input = buildTaskFeatures(task, userCompletionRate, userOnTimeRate);
        try {
            Map<String, Object> response = post("/predict/failure", input);
            logPrediction(task, "failure", input, response);

            int probability = ((Number) response.getOrDefault("probability", 0)).intValue();
            String riskLevel = (String) response.getOrDefault("riskLevel", deriveRiskLevel(probability));
            List<String> riskFactors = (List<String>) response.getOrDefault("riskFactors", List.of());
            String modelVersion = (String) response.getOrDefault("modelVersion", "unknown");

            return new RiskAnalysis(probability, riskLevel, riskFactors, modelVersion);
        } catch (RestClientException ex) {
            logger.warn("AI service unavailable for failure prediction, using fallback: {}", ex.getMessage());
            return fallbackRiskAnalysis(task);
        }
    }

    @SuppressWarnings("unchecked")
    public ImpactSimulation predictImpact(Task task) {
        Map<String, Object> input = buildTaskFeatures(task, 0.7, 0.6);
        try {
            Map<String, Object> response = post("/predict/impact", input);
            logPrediction(task, "impact", input, response);

            String severityLevel = (String) response.getOrDefault("severityLevel", "MEDIUM");
            String modelVersion = (String) response.getOrDefault("modelVersion", "unknown");
            List<Map<String, Object>> rawConsequences = (List<Map<String, Object>>) response.getOrDefault("consequences", List.of());
            List<Consequence> consequences = new ArrayList<>();
            for (Map<String, Object> c : rawConsequences) {
                consequences.add(new Consequence((String) c.get("description"), ((Number) c.get("probabilityPercent")).intValue()));
            }
            return new ImpactSimulation(severityLevel, task.getCategory(), consequences, modelVersion);
        } catch (RestClientException ex) {
            logger.warn("AI service unavailable for impact prediction, using fallback: {}", ex.getMessage());
            return fallbackImpact(task);
        }
    }

    @SuppressWarnings("unchecked")
    public PostAnalysis predictPostAnalysis(Task task, boolean completedOnTime, long daysLate) {
        Map<String, Object> input = buildTaskFeatures(task, 0.7, 0.6);
        input.put("completedOnTime", completedOnTime);
        input.put("daysLate", daysLate);
        try {
            Map<String, Object> response = post("/predict/postanalysis", input);
            logPrediction(task, "postanalysis", input, response);

            String modelVersion = (String) response.getOrDefault("modelVersion", "unknown");
            String recommendation = (String) response.getOrDefault("recommendation", "Keep tracking your progress.");
            List<Map<String, Object>> rawCauses = (List<Map<String, Object>>) response.getOrDefault("causes", List.of());
            List<Cause> causes = new ArrayList<>();
            for (Map<String, Object> c : rawCauses) {
                causes.add(new Cause((String) c.get("type"), ((Number) c.get("percentage")).intValue(), (String) c.get("description")));
            }
            return new PostAnalysis(completedOnTime, daysLate, causes, recommendation, modelVersion);
        } catch (RestClientException ex) {
            logger.warn("AI service unavailable for post-analysis, using fallback: {}", ex.getMessage());
            return fallbackPostAnalysis(completedOnTime, daysLate);
        }
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> predictIntake(String text) {
        Map<String, Object> input = new HashMap<>();
        input.put("text", text);
        try {
            Map<String, Object> response = post("/predict/intake", input);
            PredictionHistory history = new PredictionHistory();
            history.setPredictionType("intake");
            history.setInputFeatures(input);
            history.setOutput(response);
            history.setModelVersion((String) response.getOrDefault("modelVersion", "unknown"));
            predictionHistoryRepository.save(history);
            return response;
        } catch (RestClientException ex) {
            logger.warn("AI service unavailable for smart intake, using fallback: {}", ex.getMessage());
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("title", text.length() > 60 ? text.substring(0, 57) + "..." : text);
            fallback.put("description", text);
            fallback.put("category", "PERSONAL_GOAL");
            fallback.put("priority", "MEDIUM");
            fallback.put("dueDate", null);
            fallback.put("modelVersion", FALLBACK_MODEL_VERSION);
            return fallback;
        }
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> extractDeadlines(String text, String documentName) {
        Map<String, Object> input = new HashMap<>();
        input.put("text", text);
        if (documentName != null && !documentName.isBlank()) {
            input.put("documentName", documentName);
        }
        try {
            Map<String, Object> response = post("/predict/deadline-extraction", input);
            PredictionHistory history = new PredictionHistory();
            history.setPredictionType("deadline_extraction");
            history.setInputFeatures(Map.of("documentName", documentName != null ? documentName : "", "length", text.length()));
            history.setOutput(response);
            history.setModelVersion((String) response.getOrDefault("modelVersion", "unknown"));
            predictionHistoryRepository.save(history);
            return response;
        } catch (RestClientException ex) {
            logger.warn("AI service unavailable for deadline extraction: {}", ex.getMessage());
            throw new com.timelysync.exception.BadRequestException(
                    "Deadline extraction is temporarily unavailable. Please try again later.");
        }
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> extractDocumentDeadlines(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new com.timelysync.exception.BadRequestException("No document was uploaded");
        }
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            if (internalApiKey != null && !internalApiKey.isBlank()) {
                headers.set("X-Internal-Api-Key", internalApiKey);
            }

            ByteArrayResource resource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename() != null ? file.getOriginalFilename() : "document.pdf";
                }
            };

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", resource);

            HttpEntity<MultiValueMap<String, Object>> entity = new HttpEntity<>(body, headers);
            Map<String, Object> response = restTemplate.exchange(
                    aiServiceUrl + "/predict/document-deadlines",
                    HttpMethod.POST,
                    entity,
                    Map.class
            ).getBody();

            if (response == null) {
                throw new RestClientException("Empty response from AI service");
            }

            PredictionHistory history = new PredictionHistory();
            history.setPredictionType("document_deadlines");
            history.setInputFeatures(Map.of("filename", file.getOriginalFilename() != null ? file.getOriginalFilename() : ""));
            history.setOutput(response);
            history.setModelVersion((String) response.getOrDefault("modelVersion", "unknown"));
            predictionHistoryRepository.save(history);
            return response;
        } catch (HttpStatusCodeException ex) {
            String detail = ex.getResponseBodyAsString();
            logger.warn("AI document extraction rejected ({}): {}", ex.getStatusCode(), detail);
            String message = "Could not process this document right now. Ensure it is a readable PDF or image.";
            if (detail != null && detail.contains("\"detail\"")) {
                // FastAPI: {"detail":"..."}
                int start = detail.indexOf("\"detail\"");
                int colon = detail.indexOf(':', start);
                int q1 = detail.indexOf('"', colon + 1);
                int q2 = detail.indexOf('"', q1 + 1);
                if (q1 > 0 && q2 > q1) {
                    message = detail.substring(q1 + 1, q2);
                }
            }
            throw new com.timelysync.exception.BadRequestException(message);
        } catch (RestClientException ex) {
            logger.warn("AI service unavailable for document deadline extraction: {}", ex.getMessage());
            throw new com.timelysync.exception.BadRequestException(
                    "AI service timed out or is unreachable. Wait a minute for it to wake, then try again.");
        } catch (java.io.IOException ex) {
            throw new com.timelysync.exception.BadRequestException("Failed to read uploaded document");
        }
    }

    /** Sends the real outcome of a completed task back to the ML service so it can be used for future retraining. */
    public void sendOutcomeFeedback(Task task, boolean completedOnTime, long daysLate) {
        try {
            Map<String, Object> body = buildTaskFeatures(task, 0.7, 0.6);
            body.put("completedOnTime", completedOnTime);
            body.put("daysLate", daysLate);
            body.put("taskId", task.getId());
            body.put("userId", task.getUserId());
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers());
            restTemplate.exchange(aiServiceUrl + "/feedback/outcome", HttpMethod.POST, entity, Map.class);
        } catch (RestClientException ex) {
            logger.debug("Could not send outcome feedback to AI service: {}", ex.getMessage());
        }
    }

    private Map<String, Object> post(String path, Map<String, Object> body) {
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers());
        @SuppressWarnings("unchecked")
        Map<String, Object> result = restTemplate.exchange(aiServiceUrl + path, HttpMethod.POST, entity, Map.class).getBody();
        if (result == null) {
            throw new RestClientException("Empty response from AI service");
        }
        return result;
    }

    private void logPrediction(Task task, String type, Map<String, Object> input, Map<String, Object> output) {
        PredictionHistory history = new PredictionHistory();
        history.setUserId(task.getUserId());
        history.setTaskId(task.getId());
        history.setPredictionType(type);
        history.setInputFeatures(input);
        history.setOutput(output);
        history.setModelVersion((String) output.getOrDefault("modelVersion", "unknown"));
        predictionHistoryRepository.save(history);
    }

    private Map<String, Object> buildTaskFeatures(Task task, double userCompletionRate, double userOnTimeRate) {
        Map<String, Object> features = new HashMap<>();
        long daysUntilDue = task.getDueDate() != null
                ? ChronoUnit.HOURS.between(LocalDateTime.now(), task.getDueDate())
                : 72;
        features.put("hoursUntilDue", daysUntilDue);
        features.put("priority", nullToDefault(task.getPriority(), "MEDIUM"));
        features.put("category", nullToDefault(task.getCategory(), "PERSONAL_GOAL"));
        features.put("impact", nullToDefault(task.getImpact(), "MEDIUM"));
        features.put("effort", nullToDefault(task.getEffort(), "MEDIUM"));
        features.put("userCompletionRate", userCompletionRate);
        features.put("userOnTimeRate", userOnTimeRate);
        features.put("riskScoreAtCreation", task.getRiskAnalysis() != null ? task.getRiskAnalysis().getRiskScore() : 0);
        return features;
    }

    private String nullToDefault(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private String deriveRiskLevel(int score) {
        if (score >= 70) return "CRITICAL";
        if (score >= 40) return "WARNING";
        return "SAFE";
    }

    private RiskAnalysis fallbackRiskAnalysis(Task task) {
        int score = 30;
        long hours = task.getDueDate() != null ? ChronoUnit.HOURS.between(LocalDateTime.now(), task.getDueDate()) : 999;
        if (hours < 24) score += 40;
        else if (hours < 72) score += 20;
        if ("HIGH".equalsIgnoreCase(task.getPriority())) score += 25;
        else if ("MEDIUM".equalsIgnoreCase(task.getPriority())) score += 10;
        score = Math.min(score, 95);
        return new RiskAnalysis(score, deriveRiskLevel(score), List.of("AI service temporarily unavailable - showing conservative estimate"), FALLBACK_MODEL_VERSION);
    }

    private ImpactSimulation fallbackImpact(Task task) {
        List<Consequence> consequences = new ArrayList<>();
        consequences.add(new Consequence("Deadline missed", 60));
        consequences.add(new Consequence("Progress delayed", 40));
        return new ImpactSimulation("MEDIUM", task.getCategory(), consequences, FALLBACK_MODEL_VERSION);
    }

    private PostAnalysis fallbackPostAnalysis(boolean completedOnTime, long daysLate) {
        List<Cause> causes = new ArrayList<>();
        if (!completedOnTime) {
            causes.add(new Cause("Time Management", 100, "AI service temporarily unavailable - unable to compute a detailed breakdown"));
        }
        String recommendation = completedOnTime
                ? "Great job staying on schedule - keep it up!"
                : "Try breaking similar tasks into smaller steps and starting earlier.";
        return new PostAnalysis(completedOnTime, daysLate, causes, recommendation, FALLBACK_MODEL_VERSION);
    }
}
