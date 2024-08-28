package com.cloudemail.cloud.email.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Registration {
    @JsonProperty("item_id")
    private String itemId;
    @JsonProperty("enhancement_level")
    private String enhancementLevel;
    @JsonProperty("item_name")
    private String itemName;
    @JsonProperty("email")
    private String email;

    public String getItemId() {
        return itemId;
    }
    // Add getter and setter for email
    public String getEmail() {
        return email;
    }
    public void setEmail(String email) {
        this.email = email;
    }
    public void setItemId(String itemId) {
        this.itemId = itemId;
    }

    public String getEnhancementLevel() {
        return enhancementLevel;
    }

    public void setEnhancementLevel(String enhancementLevel) {
        this.enhancementLevel = enhancementLevel;
    }

    public String getItemName() {
        return itemName;
    }

    public void setItemName(String itemName) {
        this.itemName = itemName;
    }
}
