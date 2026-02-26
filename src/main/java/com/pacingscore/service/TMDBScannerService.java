package com.pacingscore.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.json.JSONArray;
import org.json.JSONObject;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

@Service
public class TMDBScannerService {
    
    @Value("${tmdb.api.key}")
    private String tmdbApiKey;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * Scanne tous les dessins animés pour enfants sur TMDB
     * et les analyse pour calculer un score de calme
     */
    public ScanResult scanChildrenAnimations() {
        ScanResult result = new ScanResult();
        
        // TMDB genre IDs
        final int ANIMATION_GENRE = 16;     // Animation
        final int FAMILY_GENRE = 10751;     // Family
        
        // Pages à scanner (on peut limiter pour tester)
        int maxPages = 5; // Scanner 5 pages de 20 résultats = 100 shows
        
        for (int page = 1; page <= maxPages; page++) {
            try {
                System.out.println("Scanning page " + page + "/" + maxPages);
                
                // Recherche par genre Animation + Family
                String discoveryUrl = "https://api.themoviedb.org/3/discover/tv"
                    + "?api_key=" + tmdbApiKey
                    + "&language=fr-FR"
                    + "&with_genres=" + ANIMATION_GENRE + "," + FAMILY_GENRE
                    + "&sort_by=popularity.desc"
                    + "&page=" + page;
                
                String response = restTemplate.getForObject(discoveryUrl, String.class);
                JSONObject json = new JSONObject(response);
                JSONArray results = json.getJSONArray("results");
                
                for (int i = 0; i < results.length(); i++) {
                    JSONObject showJson = results.getJSONObject(i);
                    int showId = showJson.getInt("id");
                    
                    // Vérifier si on a déjà cette série
                    if (showAlreadyAnalyzed(showId)) {
                        result.alreadyAnalyzed++;
                        continue;
                    }
                    
                    // Récupérer les détails
                    ShowInfo show = getShowDetails(showId, showJson);
                    
                    if (show != null) {
                        // Analyser le score
                        show.setPacingScore(calculatePacingScore(show));
                        show.setAgeRating(determineAgeRating(show));
                        
                        // Sauvegarder
                        saveToDatabase(show);
                        result.analyzed++;
                        result.processedShows.add(show);
                        
                        System.out.println("✓ Analyzed: " + show.getTitle() + " (" + show.getPacingScore() + "%)");
                    } else {
                        result.failed++;
                    }
                    
                    // Pause pour ne pas surcharger l'API
                    Thread.sleep(200);
                }
                
            } catch (Exception e) {
                System.err.println("Erreur page " + page + ": " + e.getMessage());
                result.errors++;
            }
        }
        
        return result;
    }
    
    private boolean showAlreadyAnalyzed(int tmdbId) {
        // Vérifie dans la base de données
        // Pour l'instant, retourne false (à implémenter avec Supabase)
        return false;
    }
    
    private ShowInfo getShowDetails(int showId, JSONObject basicInfo) {
        try {
            String url = "https://api.themoviedb.org/3/tv/" + showId
                + "?api_key=" + tmdbApiKey
                + "&language=fr-FR";
            
            String response = restTemplate.getForObject(url, String.class);
            JSONObject json = new JSONObject(response);
            
            ShowInfo show = new ShowInfo();
            show.setId(showId);
            show.setTitle(json.getString("name"));
            show.setDescription(json.optString("overview", ""));
            show.setPosterPath(json.optString("poster_path"));
            show.setBackdropPath(json.optString("backdrop_path"));
            show.setFirstAirDate(json.optString("first_air_date"));
            
            // Récupérer les épisodes pour analyser la durée
            if (json.has("number_of_episodes") && json.has("number_of_seasons")) {
                int episodes = json.getInt("number_of_episodes");
                int seasons = json.getInt("number_of_seasons");
                show.setEpisodeCount(episodes);
                show.setSeasonCount(seasons);
            }
            
            // Récupérer les genres
            if (json.has("genres")) {
                JSONArray genres = json.getJSONArray("genres");
                for (int i = 0; i < genres.length(); i++) {
                    String genre = genres.getJSONObject(i).getString("name").toLowerCase();
                    show.getGenres().add(genre);
                }
            }
            
            // Récupérer les réseaux pour l'âge
            if (json.has("networks")) {
                JSONArray networks = json.getJSONArray("networks");
                if (networks.length() > 0) {
                    String networkName = networks.getJSONObject(0).getString("name").toLowerCase();
                    show.setNetwork(networkName);
                }
            }
            
            // Récupérer les mots-clés pour l'analyse
            String keywordUrl = "https://api.themoviedb.org/3/tv/" + showId + "/keywords"
                + "?api_key=" + tmdbApiKey;
            
            try {
                String kwResponse = restTemplate.getForObject(keywordUrl, String.class);
                JSONObject kwJson = new JSONObject(kwResponse);
                JSONArray keywords = kwJson.getJSONArray("keywords");
                
                for (int i = 0; i < keywords.length(); i++) {
                    String keyword = keywords.getJSONObject(i).getString("name").toLowerCase();
                    show.getKeywords().add(keyword);
                }
            } catch (Exception e) {
                // Ignorer si pas de keywords
            }
            
            return show;
            
        } catch (Exception e) {
            System.err.println("Erreur récupération détails ID " + showId + ": " + e.getMessage());
            return null;
        }
    }
    
    private double calculatePacingScore(ShowInfo show) {
        double score = 50; // Score de base
        
        String title = show.getTitle().toLowerCase();
        String desc = show.getDescription().toLowerCase();
        String combined = title + " " + desc;
        
        // Critères négatifs
        if (combined.contains("action") || combined.contains("adventure")) score -= 15;
        if (combined.contains("super") || combined.contains("hero")) score -= 10;
        if (combined.contains("fight") || combined.contains("combat")) score -= 20;
        
        // Critères positifs
        if (combined.contains("calm") || combined.contains("doux") || combined.contains("douce")) score += 15;
        if (combined.contains("bedtime") || combined.contains("dodo") || combined.contains("sleep")) score += 20;
        if (combined.contains("educational") || combined.contains("éducatif")) score += 10;
        if (combined.contains("petit") || combined.contains("baby") || combined.contains("tout-petit")) score += 10;
        
        // Ajustement selon le nombre d'épisodes
        if (show.getEpisodeCount() > 100) {
            score -= 10; // Longue série = potentiellement plus intense
        } else if (show.getEpisodeCount() < 20) {
            score += 10; // Série courte = peut-être plus calme
        }
        
        // Ajustement pour les très jeunes
        if (show.getAgeRating().equals("0+") || show.getAgeRating().equals("3+")) {
            score += 10;
        }
        
        return Math.max(0, Math.min(100, score));
    }
    
    private String determineAgeRating(ShowInfo show) {
        String title = show.getTitle().toLowerCase();
        String desc = show.getDescription().toLowerCase();
        String combined = title + " " + desc;
        
        // Analyse basée sur le titre et description
        if (combined.contains("bébé") || combined.contains("baby") || combined.contains("toddler") || combined.contains("tout-petit")) {
            return "0+";
        } else if (combined.contains("prèscolaire") || combined.contains("preschool") || combined.contains("3 ans")) {
            return "3+";
        } else if (combined.contains("enfant") || combined.contains("kids") || combined.contains("6 ans") || combined.contains("primaire")) {
            return "6+";
        } else if (combined.contains("adolescent") || combined.contains("teen") || combined.contains("14 ans")) {
            return "14+";
        }
        
        // Détection par réseau
        String network = show.getNetwork();
        if (network != null) {
            if (network.contains("disney") || network.contains("nickelodeon")) {
                return "6+";
            } else if (network.contains("cartoon") || network.contains("kid")) {
                return "3+";
            }
        }
        
        // Par défaut
        return "10+";
    }
    
    private void saveToDatabase(ShowInfo show) {
        // Appel Supabase pour sauvegarder
        // (à implémenter avec SupabaseService)
    }
    
    // Classe interne pour stocker les résultats du scan
    public static class ScanResult {
        public int analyzed = 0;
        public int alreadyAnalyzed = 0;
        public int failed = 0;
        public int errors = 0;
        public List<ShowInfo> processedShows = new ArrayList<>();
        
        @Override
        public String toString() {
            return "ScanResult{" +
                "analyzed=" + analyzed +
                ", alreadyAnalyzed=" + alreadyAnalyzed +
                ", failed=" + failed +
                ", errors=" + errors +
                ", total=" + processedShows.size() +
                '}';
        }
    }
}