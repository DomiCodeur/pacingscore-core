package com.pacingscore.service;

import com.pacingscore.config.SupabaseConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

@Service
public class StorageService {
    
    @Autowired
    private SupabaseConfig supabaseConfig;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    public String downloadVideo(String videoUrl) {
        try {
            // Create temp file
            Path tempFile = Files.createTempFile("analysis_", ".mp4");
            
            // Download video
            byte[] videoBytes = restTemplate.getForObject(videoUrl, byte[].class);
            Files.write(tempFile, videoBytes);
            
            return tempFile.toString();
        } catch (Exception e) {
            throw new RuntimeException("Failed to download video", e);
        }
    }
    
    public void saveAnalysis(String videoUrl, double pacingScore) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/video_analyses";
        
        Map<String, Object> analysis = new HashMap<>();
        analysis.put("video_path", videoUrl);
        analysis.put("pacing_score", pacingScore);
        
        restTemplate.postForEntity(endpoint, analysis, String.class);
    }
    
    public void cleanup(String filePath) {
        try {
            new File(filePath).delete();
        } catch (Exception e) {
            // Log but don't throw
            e.printStackTrace();
        }
    }
}