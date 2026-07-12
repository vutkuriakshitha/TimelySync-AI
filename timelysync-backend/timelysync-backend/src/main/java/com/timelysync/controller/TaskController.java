package com.timelysync.controller;

import jakarta.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.timelysync.model.Task;
import com.timelysync.payload.request.SubtaskRequest;
import com.timelysync.payload.request.TaskRequest;
import com.timelysync.payload.response.PagedResponse;
import com.timelysync.security.UserDetailsImpl;
import com.timelysync.service.TaskService;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    @Autowired
    private TaskService taskService;

    @GetMapping
    public ResponseEntity<PagedResponse<Task>> getTasks(
            @AuthenticationPrincipal UserDetailsImpl userDetails,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String priority,
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "dueDate") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(taskService.getTasks(userDetails.getUser(), status, category, priority,
                search, sortBy, sortDir, page, size));
    }

    @GetMapping("/all")
    public ResponseEntity<java.util.List<Task>> getAllTasks(@AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(taskService.getAllUserTasks(userDetails.getUser()));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Task> getTaskById(@PathVariable String id, @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(taskService.getTaskById(id, userDetails.getUser()));
    }

    @PostMapping
    public ResponseEntity<Task> createTask(@Valid @RequestBody TaskRequest request,
                                            @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return new ResponseEntity<>(taskService.createTask(request, userDetails.getUser()), HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Task> updateTask(@PathVariable String id, @Valid @RequestBody TaskRequest request,
                                            @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(taskService.updateTask(id, request, userDetails.getUser()));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable String id, @AuthenticationPrincipal UserDetailsImpl userDetails) {
        taskService.deleteTask(id, userDetails.getUser());
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{id}/complete")
    public ResponseEntity<Task> completeTask(@PathVariable String id,
                                              @RequestPart(required = false) MultipartFile proof,
                                              @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(taskService.completeTask(id, userDetails.getUser(), proof));
    }

    @PostMapping("/{id}/subtasks")
    public ResponseEntity<Task> addSubtask(@PathVariable String id, @Valid @RequestBody SubtaskRequest request,
                                            @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return new ResponseEntity<>(taskService.addSubtask(id, request, userDetails.getUser()), HttpStatus.CREATED);
    }

    @PatchMapping("/{id}/subtasks/{subtaskId}/toggle")
    public ResponseEntity<Task> toggleSubtask(@PathVariable String id, @PathVariable String subtaskId,
                                               @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(taskService.toggleSubtask(id, subtaskId, userDetails.getUser()));
    }

    @DeleteMapping("/{id}/subtasks/{subtaskId}")
    public ResponseEntity<Task> deleteSubtask(@PathVariable String id, @PathVariable String subtaskId,
                                               @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(taskService.deleteSubtask(id, subtaskId, userDetails.getUser()));
    }

    @GetMapping("/{id}/impact-simulation")
    public ResponseEntity<?> simulateImpact(@PathVariable String id,
                                             @RequestParam(defaultValue = "miss") String scenario,
                                             @AuthenticationPrincipal UserDetailsImpl userDetails) {
        return ResponseEntity.ok(taskService.simulateImpact(id, scenario, userDetails.getUser()));
    }
}
