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

import com.pacingscore.service.TMDBService.ShowInfo;

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
    
    /**
     * Calcule le score de calme basé sur la fréquence estimée des cuts de scène
     * PRINCIPE : Moins de cuts = meilleur score
     */
    private double calculatePacingScore(ShowInfo show) {
        double score = 100; // Score maximal (moins de cuts = mieux)
        
        String title = show.getTitle().toLowerCase();
        String desc = show.getDescription().toLowerCase();
        String combined = title + " " + desc;
        
        // ==================== CRITÈRES D'ANALYSE ====================
        
        // 1. DURÉE MOYENNE DES ÉPISODES (critère majeur)
        // Une durée courte signifie des cuts fréquents pour capter l'attention
        if (show.getEpisodeCount() > 0 && show.getSeasonCount() > 0) {
            double estimatedDuration = calculateEstimatedDuration(show);
            
            if (estimatedDuration < 3.0) { // < 3 min
                score -= 40; // Très cuts fréquents (mauvais pour les enfants)
            } else if (estimatedDuration < 5.0) { // 3-5 min
                score -= 20; // Cuts fréquents
            } else if (estimatedDuration < 10.0) { // 5-10 min
                score -= 10; // Cuts modérés
            } else if (estimatedDuration > 15.0) { // > 15 min
                score += 15; // Cuts rares (bon pour les enfants)
            }
        }
        
        // 2. TYPE DE CONTENU (critère majeur)
        // La musique/dance a un rythme rapide avec beaucoup de cuts
        if (combined.contains("music") || combined.contains("musique") || 
            combined.contains("dance") || combined.contains("danse") || 
            combined.contains("song") || combined.contains("chanson")) {
            score -= 25; // Rythme très rapide
        }
        
        // 3. MOTS-CLÉS SUGGÉRANT DES CUTS FRÉQUENTS
        String[] fastCutKeywords = {
            "fast", "rapide", "ultra", "hyper", "super", "explosive",
            "fun", "funny", "comedy", "humor", "comédie",
            "action", "adventure", "aventure", "hero",
            "dance", "music", "musique", "chanson",
            "exciting", "excitant", "thrilling"
        };
        
        for (String keyword : fastCutKeywords) {
            if (combined.contains(keyword)) {
                score -= 15;
            }
        }
        
        // 4. MOTS-CLÉS SUGGÉRANT DES CUTS RARES
        String[] calmCutKeywords = {
            "calm", "slow", "lent", "doux", "douce",
            "bedtime", "dodo", "sleep", "storytime",
            "educational", "éducatif", "apprendre", "learning",
            "story", "histoire", "narrative", "contes",
            "gentil", "gentille", "sweet", "douceur"
        };
        
        for (String keyword : calmCutKeywords) {
            if (combined.contains(keyword)) {
                score += 15;
            }
        }
        
        // 5. GENRE SPÉCIFIQUE (critère majeur)
        for (String genre : show.getGenres()) {
            if (genre.contains("music") || genre.contains("dance")) {
                score -= 20;
            } else if (genre.contains("family") || genre.contains("documentary")) {
                score += 10;
            } else if (genre.contains("comedy")) {
                score -= 10;
            }
        }
        
        // 6. RÉSEAU DE DIFFUSION (YouTube = plus de cuts)
        String network = show.getNetwork();
        if (network != null) {
            if (network.contains("youtube") || network.contains("netflix")) {
                score -= 15; // YouTube/Netflix a tendance aux formats courts avec cuts fréquents
            } else if (network.contains("disney") || network.contains("cartoon")) {
                score -= 5; // Disney a des formats modérés
            } else if (network.contains("educational") || network.contains("learning")) {
                score += 15; // Chaînes éducatives = moins de cuts
            }
        }
        
        // 7. NOMBRE D'ÉPISODES (un gros nombre = tendance aux formats courts)
        int totalEpisodes = show.getEpisodeCount();
        if (totalEpisodes > 300) {
            score -= 20; // Très longue série = tendance aux formats courts et cuts fréquents
        } else if (totalEpisodes > 100) {
            score -= 10;
        } else if (totalEpisodes < 20) {
            score += 10; // Courte série = peut-être plus cohérent
        }
        
        // 8. AJUSTEMENT TRÈS JEUNES (0-3 ans)
        // Les séries pour bébés sont souvent très lentes avec peu de cuts
        if (show.getAgeRating().equals("0+") || show.getAgeRating().equals("3+")) {
            score += 20; // Ciblé pour les tout-petits = souvent plus calme
        }
        
        // 9. AJUSTEMENT YOUTUBE (ajouté pour le projet)
        // Si la série vient de YouTube, on pénalise car souvent des formats courts
        if (title.contains("cocomelon") || title.contains("baby shark") || 
            title.contains("cocomelon") || title.contains("lullaby")) {
            score -= 30; // YouTube kids = très cuts fréquents
        }
        
        // Limiter le score entre 0 et 100
        return Math.max(0, Math.min(100, score));
    }
    
    private double calculateEstimatedDuration(ShowInfo show) {
        // Estimation basée sur le nombre d'épisodes et la durée totale
        // Pour les séries très longues, la durée moyenne par épisode est souvent courte
        int totalEpisodes = show.getEpisodeCount();
        int seasons = show.getSeasonCount();
        
        if (totalEpisodes == 0) return 10.0; // Par défaut 10 min
        
        // Estimation : plus d'épisodes = durée moyenne plus courte
        double estimatedMinutes = 15.0; // Moyenne de base
        
        if (totalEpisodes > 500) estimatedMinutes = 2.0; // Cocomelon style
        else if (totalEpisodes > 200) estimatedMinutes = 5.0;
        else if (totalEpisodes > 100) estimatedMinutes = 8.0;
        else if (totalEpisodes > 50) estimatedMinutes = 10.0;
        else estimatedMinutes = 12.0;
        
        return estimatedMinutes;
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