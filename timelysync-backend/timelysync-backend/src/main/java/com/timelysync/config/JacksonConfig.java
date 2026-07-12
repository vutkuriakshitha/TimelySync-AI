package com.timelysync.config;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;

import org.springframework.boot.autoconfigure.jackson.Jackson2ObjectMapperBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.module.SimpleModule;

@Configuration
public class JacksonConfig {

    @Bean
    public Jackson2ObjectMapperBuilderCustomizer lenientDateTimeCustomizer() {
        SimpleModule module = new SimpleModule();
        module.addDeserializer(LocalDateTime.class, new LenientLocalDateTimeDeserializer());
        // All LocalDateTime values are normalized to UTC on the way in (see
        // LenientLocalDateTimeDeserializer), so serialize them back out with an
        // explicit 'Z' suffix. Without this, JS `new Date(iso)` would silently
        // reinterpret the timestamp using the browser's local timezone.
        module.addSerializer(LocalDateTime.class, new JsonSerializer<LocalDateTime>() {
            private final DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

            @Override
            public void serialize(LocalDateTime value, JsonGenerator gen, SerializerProvider serializers)
                    throws IOException {
                gen.writeString(value.atOffset(ZoneOffset.UTC).format(formatter) + "Z");
            }
        });
        return builder -> builder.modulesToInstall(modules -> {
            modules.add(module);
        });
    }
}
