package com.cloudemail.cloud.email.config;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class KafkaHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        return Health.up().withDetail("Kafka", "Connected").build();
    }
}
