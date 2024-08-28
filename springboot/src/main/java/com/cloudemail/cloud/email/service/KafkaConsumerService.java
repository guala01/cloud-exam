package com.cloudemail.cloud.email.service;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class KafkaConsumerService {

    @Autowired
    private RegistrationService registrationService;

    @KafkaListener(topics = "waitinglist-updates", groupId = "your_group_id")
    public void consume(String message) {
        System.out.println("Received message: " + message);
        registrationService.checkRegistrations();
    }
}