package com.timelysync.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.timelysync.exception.ForbiddenActionException;
import com.timelysync.exception.ResourceNotFoundException;
import com.timelysync.model.Notification;
import com.timelysync.payload.response.NotificationDto;
import com.timelysync.repository.NotificationRepository;

@Service
public class NotificationService {

    @Autowired
    private NotificationRepository notificationRepository;

    public List<NotificationDto> getUserNotifications(String userId) {
        return notificationRepository.findByUserIdOrderByCreatedAtDesc(userId).stream()
                .map(NotificationDto::fromNotification)
                .collect(Collectors.toList());
    }

    public List<NotificationDto> getUnreadNotifications(String userId) {
        return notificationRepository.findByUserIdAndReadFalseOrderByCreatedAtDesc(userId).stream()
                .map(NotificationDto::fromNotification)
                .collect(Collectors.toList());
    }

    public long getUnreadCount(String userId) {
        return notificationRepository.countByUserIdAndReadFalse(userId);
    }

    public void markAsRead(String notificationId, String userId) {
        Notification notification = notificationRepository.findById(notificationId)
                .orElseThrow(() -> new ResourceNotFoundException("Notification not found"));
        if (!notification.getUserId().equals(userId)) {
            throw new ForbiddenActionException("You do not have permission to modify this notification");
        }
        notification.setRead(true);
        notificationRepository.save(notification);
    }

    public void markAllAsRead(String userId) {
        List<Notification> unread = notificationRepository.findByUserIdAndReadFalseOrderByCreatedAtDesc(userId);
        unread.forEach(n -> n.setRead(true));
        notificationRepository.saveAll(unread);
    }

    public void createNotification(String userId, String type, String message) {
        createNotification(userId, type, message, null);
    }

    public void createNotification(String userId, String type, String message, String metadata) {
        Notification notification = new Notification(userId, type, message);
        notification.setMetadata(metadata);
        notificationRepository.save(notification);
    }
}
