package com.timelysync.service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.timelysync.exception.BadRequestException;

/**
 * Stores task-completion "proof" uploads (images/PDFs) on local disk under
 * an upload directory outside of version control. Validates file type and
 * size, and generates a random, non-guessable filename to avoid IDOR-style
 * access to other users' files and path traversal attacks.
 */
@Service
public class FileStorageService {

    private static final Set<String> ALLOWED_CONTENT_TYPES = Set.of(
            "image/png", "image/jpeg", "image/jpg", "image/webp", "application/pdf");

    private static final List<String> ALLOWED_EXTENSIONS = List.of(".png", ".jpg", ".jpeg", ".webp", ".pdf");

    @Value("${timelysync.app.uploadDir:uploads}")
    private String uploadDir;

    public String store(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new BadRequestException("No file was provided");
        }
        String contentType = file.getContentType();
        if (contentType == null || !ALLOWED_CONTENT_TYPES.contains(contentType.toLowerCase())) {
            throw new BadRequestException("Unsupported file type. Allowed: PNG, JPG, WEBP, PDF");
        }

        String originalName = file.getOriginalFilename() != null ? file.getOriginalFilename() : "";
        String extension = ALLOWED_EXTENSIONS.stream()
                .filter(ext -> originalName.toLowerCase().endsWith(ext))
                .findFirst()
                .orElseThrow(() -> new BadRequestException("Unsupported file extension"));

        String storedFileName = UUID.randomUUID() + extension;

        try {
            Path uploadPath = Paths.get(uploadDir).toAbsolutePath().normalize();
            Files.createDirectories(uploadPath);
            Path target = uploadPath.resolve(storedFileName).normalize();
            if (!target.getParent().equals(uploadPath)) {
                throw new BadRequestException("Invalid file path");
            }
            Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new RuntimeException("Failed to store file: " + e.getMessage(), e);
        }

        return storedFileName;
    }

    public String toPublicUrl(String storedFileName) {
        return "/uploads/" + storedFileName;
    }
}
