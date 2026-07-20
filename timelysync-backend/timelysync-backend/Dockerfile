# Multi-stage build for free Render / Railway deploys
FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:21-jre-jammy
WORKDIR /app
COPY --from=build /app/target/timelysync-backend-1.0.0.jar app.jar
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75.0"
EXPOSE 8080
# Render sets PORT; Spring already reads server.port=${PORT:8080}
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
