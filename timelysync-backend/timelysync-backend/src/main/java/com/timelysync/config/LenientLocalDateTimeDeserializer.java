package com.timelysync.config;

import java.io.IOException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeParseException;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;

/**
 * Browsers/JS clients almost always send timestamps as ISO-8601 strings
 * with a timezone offset or a trailing 'Z' (e.g. via `Date.toISOString()`),
 * but the JDK's default LocalDateTime deserializer only accepts offset-less
 * strings and throws a 400/500 otherwise. This deserializer accepts both
 * forms and normalizes everything to UTC so all stored timestamps are
 * consistent regardless of which timezone a given user's browser is in.
 */
public class LenientLocalDateTimeDeserializer extends JsonDeserializer<LocalDateTime> {

    @Override
    public LocalDateTime deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        String value = p.getValueAsString();
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return LocalDateTime.parse(value);
        } catch (DateTimeParseException ignored) {
            // fall through to offset/instant parsing
        }
        try {
            return OffsetDateTime.parse(value).atZoneSameInstant(ZoneOffset.UTC).toLocalDateTime();
        } catch (DateTimeParseException ignored) {
            // fall through to plain instant parsing
        }
        return LocalDateTime.ofInstant(Instant.parse(value), ZoneOffset.UTC);
    }
}
