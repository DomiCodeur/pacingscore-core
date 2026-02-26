package com.pacingscore.service;

import com.pacingscore.core.VideoAnalyzer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class AnalysisService {
    
    @Autowired
    private VideoAnalyzer videoAnalyzer;
    
    @Autowired
    private StorageService storageService;
    
    public double analyzeVideo(String videoPath) {
        return videoAnalyzer.analyzePacing(videoPath);
    }
    
    public void processVideo(String videoUrl) {
        // 1. Download video to temp storage
        String localPath = storageService.downloadVideo(videoUrl);
        
        // 2. Analyze video
        double pacingScore = analyzeVideo(localPath);
        
        // 3. Store results in Supabase
        storageService.saveAnalysis(videoUrl, pacingScore);
        
        // 4. Cleanup
        storageService.cleanup(localPath);
    }
}