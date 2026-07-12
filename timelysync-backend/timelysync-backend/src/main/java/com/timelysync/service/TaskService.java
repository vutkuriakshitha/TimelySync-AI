package com.timelysync.service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.regex.Pattern;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.timelysync.exception.BadRequestException;
import com.timelysync.exception.ForbiddenActionException;
import com.timelysync.exception.ResourceNotFoundException;
import com.timelysync.model.Subtask;
import com.timelysync.model.Task;
import com.timelysync.model.User;
import com.timelysync.payload.request.SubtaskRequest;
import com.timelysync.payload.request.TaskRequest;
import com.timelysync.payload.response.PagedResponse;
import com.timelysync.repository.TaskRepository;

@Service
public class TaskService {

    private static final List<String> VALID_CATEGORIES = List.of("ACADEMIC", "OPPORTUNITY", "PERSONAL_GOAL", "EVENT");
    private static final List<String> VALID_LEVELS = List.of("HIGH", "MEDIUM", "LOW");

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private MongoTemplate mongoTemplate;

    @Autowired
    private AiClientService aiClientService;

    @Autowired
    private FileStorageService fileStorageService;

    @Autowired
    private UserStatsService userStatsService;

    @Autowired
    private NotificationService notificationService;

    public PagedResponse<Task> getTasks(User user, String status, String category, String priority,
                                         String search, String sortBy, String sortDir, int page, int size) {
        if (page < 0) page = 0;
        if (size <= 0 || size > 100) size = 20;

        Criteria criteria = Criteria.where("userId").is(user.getId());
        if (status != null && !status.isBlank()) {
            criteria = criteria.and("status").is(status.toUpperCase());
        }
        if (category != null && !category.isBlank()) {
            criteria = criteria.and("category").is(category.toUpperCase());
        }
        if (priority != null && !priority.isBlank()) {
            criteria = criteria.and("priority").is(priority.toUpperCase());
        }
        if (search != null && !search.isBlank()) {
            String safe = Pattern.quote(search.trim());
            criteria = criteria.and("title").regex(safe, "i");
        }

        Query query = new Query(criteria);
        long total = mongoTemplate.count(query, Task.class);

        String sortField = List.of("dueDate", "createdAt", "priority", "title", "updatedAt").contains(sortBy)
                ? sortBy : "dueDate";
        Sort.Direction direction = "asc".equalsIgnoreCase(sortDir) ? Sort.Direction.ASC : Sort.Direction.DESC;

        query.with(PageRequest.of(page, size, Sort.by(direction, sortField)));
        List<Task> tasks = mongoTemplate.find(query, Task.class);

        return new PagedResponse<>(tasks, page, size, total);
    }

    public List<Task> getAllUserTasks(User user) {
        return taskRepository.findByUserId(user.getId());
    }

    public Task getTaskById(String id, User user) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Task not found"));
        assertOwnership(task, user);
        return task;
    }

    public Task createTask(TaskRequest request, User user) {
        validateRequest(request);

        Task task = new Task();
        task.setUserId(user.getId());
        task.setTitle(request.getTitle().trim());
        task.setDescription(request.getDescription());
        task.setCategory(request.getCategory().toUpperCase());
        task.setPriority(normalizeLevel(request.getPriority()));
        task.setImpact(normalizeLevel(request.getImpact()));
        task.setEffort(normalizeLevel(request.getEffort()));
        task.setDueDate(request.getDueDate());
        task.setTags(request.getTags() != null ? request.getTags() : List.of());
        task.setNotes(request.getNotes());
        task.setLocation(request.getLocation());
        task.setStatus("ACTIVE");
        task.setCreatedAt(LocalDateTime.now());
        task.setUpdatedAt(LocalDateTime.now());

        Task saved = taskRepository.save(task);
        computeAndAttachRisk(saved, user);
        return saved;
    }

    public Task updateTask(String id, TaskRequest request, User user) {
        validateRequest(request);
        Task task = getTaskById(id, user);

        task.setTitle(request.getTitle().trim());
        task.setDescription(request.getDescription());
        task.setCategory(request.getCategory().toUpperCase());
        task.setPriority(normalizeLevel(request.getPriority()));
        task.setImpact(normalizeLevel(request.getImpact()));
        task.setEffort(normalizeLevel(request.getEffort()));
        task.setDueDate(request.getDueDate());
        task.setTags(request.getTags() != null ? request.getTags() : task.getTags());
        task.setNotes(request.getNotes());
        task.setLocation(request.getLocation());
        task.setUpdatedAt(LocalDateTime.now());

        Task saved = taskRepository.save(task);
        if ("ACTIVE".equals(saved.getStatus())) {
            computeAndAttachRisk(saved, user);
        }
        return saved;
    }

    public void deleteTask(String id, User user) {
        Task task = getTaskById(id, user);
        taskRepository.delete(task);
    }

    public Task completeTask(String id, User user, MultipartFile proofFile) {
        Task task = getTaskById(id, user);
        if ("COMPLETED".equals(task.getStatus())) {
            throw new BadRequestException("Task is already completed");
        }

        LocalDateTime now = LocalDateTime.now();
        boolean onTime = task.getDueDate() == null || !now.isAfter(task.getDueDate());
        long daysLate = 0;
        if (!onTime) {
            daysLate = ChronoUnit.DAYS.between(task.getDueDate(), now);
            if (daysLate < 1) daysLate = 1;
        }

        task.setStatus("COMPLETED");
        task.setCompletedAt(now);
        task.setUpdatedAt(now);

        if (proofFile != null && !proofFile.isEmpty()) {
            String storedName = fileStorageService.store(proofFile);
            task.setProofFileName(proofFile.getOriginalFilename());
            task.setProofUrl(fileStorageService.toPublicUrl(storedName));
        }

        task.setPostAnalysis(aiClientService.predictPostAnalysis(task, onTime, daysLate));

        Task saved = taskRepository.save(task);

        aiClientService.sendOutcomeFeedback(saved, onTime, daysLate);
        userStatsService.recordTaskCompletion(user, onTime);
        notificationService.createNotification(user.getId(), "task_completed",
                "Task \"" + saved.getTitle() + "\" marked as completed" + (onTime ? " on time!" : "."));

        return saved;
    }

    public Task addSubtask(String taskId, SubtaskRequest request, User user) {
        Task task = getTaskById(taskId, user);
        Subtask subtask = new Subtask(request.getTitle().trim(), request.getDueDate());
        task.getSubtasks().add(subtask);
        task.setUpdatedAt(LocalDateTime.now());
        return taskRepository.save(task);
    }

    public Task toggleSubtask(String taskId, String subtaskId, User user) {
        Task task = getTaskById(taskId, user);
        Subtask subtask = task.getSubtasks().stream()
                .filter(s -> s.getId().equals(subtaskId))
                .findFirst()
                .orElseThrow(() -> new ResourceNotFoundException("Subtask not found"));
        subtask.setCompleted(!subtask.isCompleted());
        task.setUpdatedAt(LocalDateTime.now());
        return taskRepository.save(task);
    }

    public Task deleteSubtask(String taskId, String subtaskId, User user) {
        Task task = getTaskById(taskId, user);
        boolean removed = task.getSubtasks().removeIf(s -> s.getId().equals(subtaskId));
        if (!removed) {
            throw new ResourceNotFoundException("Subtask not found");
        }
        task.setUpdatedAt(LocalDateTime.now());
        return taskRepository.save(task);
    }

    public java.util.Map<String, Object> simulateImpact(String taskId, String scenario, User user) {
        Task task = getTaskById(taskId, user);
        var impact = aiClientService.predictImpact(task);
        java.util.Map<String, Object> result = new java.util.LinkedHashMap<>();
        result.put("taskId", task.getId());
        result.put("title", task.getTitle());
        result.put("scenario", scenario);
        result.put("severityLevel", impact.getSeverityLevel());
        result.put("category", impact.getCategory());
        result.put("consequences", impact.getConsequences());
        result.put("modelVersion", impact.getModelVersion());
        return result;
    }

    public void computeAndAttachRisk(Task task, User user) {
        double completionRate = getUserCompletionRate(user);
        double onTimeRate = getUserOnTimeRate(user);
        task.setRiskAnalysis(aiClientService.predictFailureRisk(task, completionRate, onTimeRate));
        taskRepository.save(task);
    }

    public double getUserCompletionRate(User user) {
        long total = taskRepository.countByUserId(user.getId());
        if (total == 0) return 0.7;
        long completed = taskRepository.countByUserIdAndStatus(user.getId(), "COMPLETED");
        return (double) completed / total;
    }

    public double getUserOnTimeRate(User user) {
        List<Task> completed = taskRepository.findByUserIdAndStatus(user.getId(), "COMPLETED");
        if (completed.isEmpty()) return 0.6;
        long onTime = completed.stream()
                .filter(t -> t.getPostAnalysis() != null && t.getPostAnalysis().isCompletedOnTime())
                .count();
        return (double) onTime / completed.size();
    }

    private void assertOwnership(Task task, User user) {
        if (!task.getUserId().equals(user.getId())) {
            throw new ForbiddenActionException("You do not have permission to access this task");
        }
    }

    private void validateRequest(TaskRequest request) {
        if (!VALID_CATEGORIES.contains(request.getCategory().toUpperCase())) {
            throw new BadRequestException("Invalid category. Must be one of: " + VALID_CATEGORIES);
        }
    }

    private String normalizeLevel(String value) {
        if (value == null || !VALID_LEVELS.contains(value.toUpperCase())) {
            return "MEDIUM";
        }
        return value.toUpperCase();
    }
}
