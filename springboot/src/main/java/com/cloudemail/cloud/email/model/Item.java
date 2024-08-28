package com.cloudemail.cloud.email.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Item {
    @JsonProperty("Item ID")
    private String itemId;
    @JsonProperty("Enhancement Level")
    private String enhancementLevel;
    @JsonProperty("Price")
    private String price;
    @JsonProperty("Timestamp")
    private String timestamp;


    public String getItemId() {
        return itemId;
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

    public String getPrice() {
        return price;
    }

    public void setPrice(String price) {
        this.price = price;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}
