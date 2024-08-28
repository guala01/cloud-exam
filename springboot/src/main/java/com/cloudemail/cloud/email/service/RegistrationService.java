package com.cloudemail.cloud.email.service;

import com.cloudemail.cloud.email.model.Item;
import com.cloudemail.cloud.email.model.Registration;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class RegistrationService {

    @Autowired
    private S3Service s3Service;

    @Autowired
    private EmailService emailService;

    @Autowired
    private ObjectMapper objectMapper;

    public void checkRegistrations() {
        try {
            String registrationsJson = s3Service.getFileContent("registrations.json");
            String waitinglistJson = s3Service.getFileContent("market_data.json");
    
            Map<String, List<Registration>> registrations = objectMapper.readValue(registrationsJson, new TypeReference<Map<String, List<Registration>>>() {});
            List<Item> waitinglist = objectMapper.readValue(waitinglistJson, new TypeReference<List<Item>>() {});
    
            for (Map.Entry<String, List<Registration>> entry : registrations.entrySet()) {
                List<Registration> userRegistrations = entry.getValue();
    
                for (Registration registration : userRegistrations) {
                    for (Item item : waitinglist) {
                        if (item.getItemId().equals(registration.getItemId()) &&
                            item.getEnhancementLevel().equals(registration.getEnhancementLevel())) {
                            String enhancementText = getEnhancementText(registration.getEnhancementLevel());
                            String message = createEmailMessage(registration.getItemName(), enhancementText, item.getTimestamp());
                            
                            if (registration.getEmail() != null) {
                                emailService.sendEmail(registration.getEmail(), "Item Alert", message);
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    //next week patch might break this ay caramba
    private String getEnhancementText(String enhancementLevel) {
        switch (enhancementLevel) {
            case "1": return "PRI";
            case "2": return "DUO";
            case "3": return "TRI";
            case "4": return "TET";
            case "5": return "PEN";
            default: return "";
        }
    }
    
    private String createEmailMessage(String itemName, String enhancementText, String timestamp) {
        if (enhancementText.isEmpty()) {
            return String.format("The item \"%s\" has been listed at: %s", itemName, timestamp);
        } else {
            return String.format("The item \"%s\" with enhancement level %s has been listed at: %s", itemName, enhancementText, timestamp);
        }
    }
    
}
