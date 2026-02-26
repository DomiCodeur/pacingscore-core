package com.pacingscore.core;

import org.springframework.stereotype.Component;
import java.util.concurrent.TimeUnit;
import java.io.BufferedReader;
import java.io.InputStreamReader;

@Component
public class VideoAnalyzer {
    
    public double analyzePacing(String videoPath) {
        try {
            // Commande FFmpeg pour analyser les cuts
            String[] command = {
                "ffmpeg",
                "-i", videoPath,
                "-vf", "select='gt(scene,0.4)',metadata=print:file=-",
                "-f", "null",
                "-"
            };
            
            Process process = Runtime.getRuntime().exec(command);
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
            
            int sceneChanges = 0;
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.contains("scene_score")) {
                    sceneChanges++;
                }
            }
            
            process.waitFor(30, TimeUnit.SECONDS);
            
            // Durée de la vidéo en minutes (à implémenter)
            double durationInMinutes = getDurationInMinutes(videoPath);
            
            // Calcul du score
            double cutsPerMinute = sceneChanges / durationInMinutes;
            return calculatePacingScore(cutsPerMinute);
            
        } catch (Exception e) {
            e.printStackTrace();
            return -1;
        }
    }
    
    private double getDurationInMinutes(String videoPath) {
        try {
            String[] command = {
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                videoPath
            };
            
            Process process = Runtime.getRuntime().exec(command);
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            
            String duration = reader.readLine();
            process.waitFor(10, TimeUnit.SECONDS);
            
            return Double.parseDouble(duration) / 60.0;
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }
    
    private double calculatePacingScore(double cutsPerMinute) {
        // Score inversé : moins de cuts = meilleur score
        if (cutsPerMinute <= 2) return 95;  // Très calme
        if (cutsPerMinute <= 5) return 85;  // Calme
        if (cutsPerMinute <= 10) return 70; // Modéré
        if (cutsPerMinute <= 15) return 50; // Stimulant
        if (cutsPerMinute <= 20) return 30; // Très stimulant
        return 15; // Extrêmement stimulant
    }
}