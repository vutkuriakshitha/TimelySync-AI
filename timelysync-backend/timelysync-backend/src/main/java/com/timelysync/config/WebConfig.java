package com.timelysync.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${timelysync.app.uploadDir:uploads}")
    private String uploadDir;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:" + uploadDir + "/");
    }

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        // Explicitly use the classic HttpURLConnection-based request factory.
        // The JDK HttpClient-based factory that Spring Boot 3.4 auto-detects
        // by default has been observed to occasionally drop the request body
        // on POST requests to some ASGI servers (e.g. uvicorn) - using the
        // well-established Simple factory avoids that class of bug.
        //
        // Read timeout must be high: document OCR (pdf2image + tesseract) on
        // Render free instances commonly takes 30–120s, not a few seconds.
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(15000);
        factory.setReadTimeout(180000);
        factory.setBufferRequestBody(true);
        return builder.requestFactory(() -> factory).build();
    }
}
