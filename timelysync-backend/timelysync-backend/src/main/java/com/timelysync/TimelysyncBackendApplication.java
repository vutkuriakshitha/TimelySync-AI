package com.timelysync;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class TimelysyncBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(TimelysyncBackendApplication.class, args);
    }
}
