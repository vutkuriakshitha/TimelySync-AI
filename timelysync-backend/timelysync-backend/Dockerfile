# Multi-stage build tuned for Render free tier (512MB RAM)
FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests -Dmaven.test.skip=true package \
    -Dspring-boot.repackage.excludeDevtools=true

FROM eclipse-temurin:21-jre-jammy
WORKDIR /app
COPY --from=build /app/target/timelysync-backend-1.0.0.jar app.jar
# Free instances have ~512MB; keep the heap small so the process is not OOM-killed.
ENV JAVA_OPTS="-XX:MaxRAMPercentage=50.0 -Xms64m -Xmx256m"
EXPOSE 8080
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
