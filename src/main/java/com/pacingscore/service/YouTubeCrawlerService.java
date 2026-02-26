package com.pacingscore.service;

import com.pacingscore.config.YouTubeConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.json.JSONArray;
import org.json.JSONObject;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

@Service
public class YouTubeCrawlerService {
    
    @Autowired
    private YouTubeConfig youtubeConfig;
    
    // AnalysisService a été remplacé par VideoAnalyzerService
    // @Autowired
    // private AnalysisService analysisService;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * Recherche automatiquement des dessins animés sur YouTube
     * et les analyse pour remplir la base de données
     */
    public List<VideoAnalysis> crawlAndAnalyze(String searchTerm) {
        List<VideoAnalysis> results = new ArrayList<>();
        
        // Rechercher des vidéos YouTube
        String searchUrl = buildYouTubeSearchUrl(searchTerm);
        String response = restTemplate.getForObject(searchUrl, String.class);
        JSONObject json = new JSONObject(response);
        
        JSONArray items = json.getJSONArray("items");
        int maxVideos = Math.min(items.length(), 10); // Max 10 vidéos
        
        for (int i = 0; i < maxVideos; i++) {
            JSONObject video = items.getJSONObject(i);
            JSONObject id = video.getJSONObject("id");
            String videoId = id.getString("videoId");
            
            JSONObject snippet = video.getJSONObject("snippet");
            String title = snippet.getString("title");
            String description = snippet.getString("description");
            String thumbnail = snippet.getJSONObject("thumbnails")
                .getJSONObject("high").getString("url");
            
            // Analyser la vidéo
            String videoUrl = "https://www.youtube.com/watch?v=" + videoId;
            double pacingScore = analyzeVideo(videoUrl);
            
            // Extraire l'âge recommandé
            String ageRating = extractAgeRating(title, description);
            
            VideoAnalysis analysis = new VideoAnalysis();
            analysis.setVideoId(videoId);
            analysis.setTitle(title);
            analysis.setDescription(description);
            analysis.setThumbnailUrl(thumbnail);
            analysis.setVideoUrl(videoUrl);
            analysis.setPacingScore(pacingScore);
            analysis.setAgeRating(ageRating);
            
            results.add(analysis);
        }
        
        return results;
    }
    
    private String buildYouTubeSearchUrl(String searchTerm) {
        try {
            String encodedSearch = URLEncoder.encode(searchTerm, StandardCharsets.UTF_8.toString());
            return "https://www.googleapis.com/youtube/v3/search"
                + "?part=snippet"
                + "&q=" + encodedSearch
                + "&type=video"
                + "&videoDuration=short,medium,long"
                + "&maxResults=20"
                + "&key=" + youtubeConfig.getApiKey();
        } catch (Exception e) {
            throw new RuntimeException("Failed to build search URL", e);
        }
    }
    
    private double analyzeVideo(String videoUrl) {
        // Note: On ne peut pas télécharger et analyser directement depuis YouTube
        // On va utiliser une approche méta-analyse basée sur :
        // 1. La durée de la vidéo
        // 2. Le titre et description
        // 3. Les données disponibles via l'API YouTube
        
        // Pour l'instant, retourne un score basé sur des critères simples
        // Dans une version future, on pourrait utiliser yt-dlp ou un service externe
        return analyzeFromMetadata(videoUrl);
    }
    
    private double analyzeFromMetadata(String videoUrl) {
        try {
            // Récupérer les détails vidéo via l'API YouTube
            String apiUrl = "https://www.googleapis.com/youtube/v3/videos"
                + "?part=snippet,contentDetails"
                + "&id=" + videoUrl.substring(videoUrl.indexOf("=") + 1)
                + "&key=" + youtubeConfig.getApiKey();
            
            String response = restTemplate.getForObject(apiUrl, String.class);
            JSONObject json = new JSONObject(response);
            
            JSONArray items = json.getJSONArray("items");
            if (items.length() == 0) {
                return -1;
            }
            
            JSONObject item = items.getJSONObject(0);
            JSONObject contentDetails = item.getJSONObject("contentDetails");
            String duration = contentDetails.getString("duration");
            
            // Convertir PT5M30S en minutes
            int minutes = parseDuration(duration);
            
            // Analyse basée sur la durée et le titre
            double score = analyzeFromTitleAndDuration(item.getJSONObject("snippet"), minutes);
            
            return score;
        } catch (Exception e) {
            e.printStackTrace();
            return -1;
        }
    }
    
    private int parseDuration(String duration) {
        // Exemple: PT5M30S ou PT2M ou PT1H30M
        int minutes = 0;
        if (duration.contains("H")) {
            String hoursPart = duration.split("H")[0].split("PT")[1];
            minutes += Integer.parseInt(hoursPart) * 60;
        }
        if (duration.contains("M")) {
            String minutesPart = duration.split("M")[0];
            if (minutesPart.contains("PT")) {
                minutesPart = minutesPart.split("PT")[1];
            } else if (minutesPart.contains("H")) {
                minutesPart = minutesPart.split("H")[1];
            }
            minutes += Integer.parseInt(minutesPart);
        }
        return minutes;
    }
    
    private double analyzeFromTitleAndDuration(JSONObject snippet, int minutes) {
        String title = snippet.getString("title").toLowerCase();
        
        // Critères pour les dessins animés pour enfants
        int score = 50; // Score de base
        
        // Si très court (moins de 5 min) = peut-être mieux
        if (minutes < 5) score += 20;
        else if (minutes > 15) score -= 10; // Long = plus risqué
        
        // Mots-clés négatifs
        String[] negativeKeywords = {
            "fast", "rapide", "quick", "super", "ultra", "extreme",
            "action", "excitement", "intense", "hyper"
        };
        
        for (String keyword : negativeKeywords) {
            if (title.contains(keyword)) {
                score -= 15;
            }
        }
        
        // Mots-clés positifs
        String[] positiveKeywords = {
            "calm", "doux", "douces", "slow", "lent", "lente",
            "bedtime", "dodo", "sleep", "relaxing", "paisible"
        };
        
        for (String keyword : positiveKeywords) {
            if (title.contains(keyword)) {
                score += 15;
            }
        }
        
        // Limite entre 0 et 100
        return Math.max(0, Math.min(100, score));
    }
    
    private String extractAgeRating(String title, String description) {
        // Analyse automatique pour déterminer la tranche d'âge
        String combined = (title + " " + description).toLowerCase();
        
        if (combined.contains("bébé") || combined.contains("baby") || combined.contains("toddler")) {
            return "0+";
        } else if (combined.contains("prèscolaire") || combined.contains("preschool") || combined.contains("3 ans")) {
            return "3+";
        } else if (combined.contains("enfant") || combined.contains("kids") || combined.contains("6 ans")) {
            return "6+";
        } else if (combined.contains("primaire") || combined.contains("elementary") || combined.contains("10 ans")) {
            return "10+";
        } else if (combined.contains("adolescent") || combined.contains("teen") || combined.contains("14 ans")) {
            return "14+";
        }
        
        return "6+"; // Par défaut
    }
    
    // Classe interne pour stocker les résultats
    public static class VideoAnalysis {
        private String videoId;
        private String title;
        private String description;
        private String thumbnailUrl;
        private String videoUrl;
        private double pacingScore;
        private String ageRating;
        
        // Getters and setters
        public String getVideoId() { return videoId; }
        public void setVideoId(String videoId) { this.videoId = videoId; }
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        public String getThumbnailUrl() { return thumbnailUrl; }
        public void setThumbnailUrl(String thumbnailUrl) { this.thumbnailUrl = thumbnailUrl; }
        public String getVideoUrl() { return videoUrl; }
        public void setVideoUrl(String videoUrl) { this.videoUrl = videoUrl; }
        public double getPacingScore() { return pacingScore; }
        public void setPacingScore(double pacingScore) { this.pacingScore = pacingScore; }
        public String getAgeRating() { return ageRating; }
        public void setAgeRating(String ageRating) { this.ageRating = ageRating; }
    }
}