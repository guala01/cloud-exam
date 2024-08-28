package com.cloudemail.cloud.email.service;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.S3Object;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

@Service
public class S3Service {

    private static final Logger logger = LoggerFactory.getLogger(S3Service.class);

    @Value("${scaleway.bucket.name}")
    private String bucketName;

    @Autowired
    private AmazonS3 amazonS3;

    public String getFileContent(String key) {
        logger.info("Attempting to retrieve file: {} from bucket: {}", key, bucketName);
        try {
            S3Object s3Object = amazonS3.getObject(bucketName, key);
            logger.info("Successfully retrieved S3 object for key: {}", key);
            String content = new BufferedReader(new InputStreamReader(s3Object.getObjectContent()))
                    .lines().collect(Collectors.joining("\n"));
            logger.info("File content retrieved successfully for key: {}", key);
            return content;
        } catch (Exception e) {
            logger.error("Error retrieving file content for key: {}. Error: {}", key, e.getMessage());
            throw e;
        }
    }
}
