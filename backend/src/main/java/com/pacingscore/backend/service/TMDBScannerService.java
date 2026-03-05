package com.pacingscore.backend.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.json.JSONArray;
import org.json.JSONObject;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.pacingscore.backend.service.TMDBService.ShowInfo;

@Service
public class TMDBScannerService {
    
    @Value("${tmdb.api.key}")
    private String tmdbApiKey;
    
    @Autowired
    private SupabaseService supabaseService;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * Scanne tous les dessins animés pour enfants sur TMDB
     * et les analyse pour calculer un score de calme
     */
    public ScanResult scanChildrenAnimations() {
        ScanResult result = new ScanResult();
        
        // Pages à scanner
        int maxPages = 5;
        
        for (int page = 1; page <= maxPages; page++) {
            try {
                System.out.println("Scanning page " + page + "/" + maxPages);
                
                // Découverte par genre Animation + Family
                String discoveryUrl = "https://api.themoviedb.org/3/discover/tv"
                    + "?api_key=" + tmdbApiKey
                    + "&language=fr-FR"
                    + "&with_genres=16,10751"  // Animation + Family
                    + "&sort_by=popularity.desc"
                    + "&page=" + page;
                
                String response = restTemplate.getForObject(discoveryUrl, String.class);
                JSONObject json = new JSONObject(response);
                JSONArray results = json.getJSONArray("results");
                
                System.out.println("Page " + page + " returned " + results.length() + " shows");
                
                for (int i = 0; i < results.length(); i++) {
                    JSONObject showJson = results.getJSONObject(i);
                    int showId = showJson.getInt("id");
                    String title = showJson.getString("name");
                    System.out.println("Processing: " + title + " (ID:" + showId + ")");
                    
                    // Vérifier si déjà analysé
                    if (showAlreadyAnalyzed(showId)) {
                        System.out.println(" => Already exists, skipping");
                        result.alreadyAnalyzed++;
                        continue;
                    }
                    
                    // Récupérer les détails complets
                    ShowInfo show = getShowDetails(showId, showJson);
                    
                    if (show != null) {
                        // Déterminer l'âge
                        String age = determineAgeRating(show);
                        show.setAgeRating(age);
                        
                        // FILTRE : ignorer les séries 14+ et 18+ (pas pour enfants)
                        if ("14+".equals(age) || "18+".equals(age)) {
                            System.out.println(" => Skipping (age " + age + ")");
                            result.skippedAge++;
                            continue;
                        }
                        
                        // Calculer le score
                        double score = calculatePacingScore(show);
                        show.setPacingScore(score);
                        
                        // Sauvegarder
                        saveToDatabase(show);
                        result.analyzed++;
                        result.processedShows.add(show);
                        
                        System.out.println("✓ Analyzed & saved: " + show.getTitle() + " (score:" + score + "%, age:" + age + ")");
                    } else {
                        System.err.println("✗ Failed to get details for ID " + showId);
                        result.failed++;
                    }
                    
                    // Pause API
                    Thread.sleep(200);
                }
                
            } catch (Exception e) {
                System.err.println("Erreur page " + page + ": " + e.getMessage());
                e.printStackTrace();
                result.errors++;
            }
        }
        
        return result;
    }
    
    private boolean showAlreadyAnalyzed(int tmdbId) {
        return supabaseService.showExists(tmdbId);
    }
    
    private ShowInfo getShowDetails(int showId, JSONObject basicInfo) {
        try {
            System.out.println("[DEBUG] Fetching TMDB details for ID: " + showId);
            String url = "https://api.themoviedb.org/3/tv/" + showId
                + "?api_key=" + tmdbApiKey
                + "&language=fr-FR";
            
            String response = restTemplate.getForObject(url, String.class);
            if (response == null) {
                System.err.println("[ERROR] Null response from TMDB for ID " + showId);
                return null;
            }
            
            JSONObject json = new JSONObject(response);
            ShowInfo show = new ShowInfo();
            show.setId(showId);
            String title = json.getString("name");
            show.setTitle(title);
            
            // FILTRE : ignorer les titres non-latins (chinois, russe, arabe, etc.)
            if (title != null && !title.matches(".*[a-zA-Z].*")) {
                System.out.println(" => Skipping non-latin title: " + title);
                return null;
            }
            
            show.setDescription(json.optString("overview", ""));
            show.setPosterPath(json.optString("poster_path"));
            show.setBackdropPath(json.optString("backdrop_path"));
            show.setFirstAirDate(json.optString("first_air_date"));
            
            // Récupérer les épisodes pour analyser la durée
            if (json.has("number_of_episodes") && !json.isNull("number_of_episodes")) {
                show.setEpisodeCount(json.getInt("number_of_episodes"));
            }
            if (json.has("number_of_seasons") && !json.isNull("number_of_seasons")) {
                show.setSeasonCount(json.getInt("number_of_seasons"));
            }
            
            // Récupérer les genres (stocker les IDs)
            if (json.has("genres")) {
                JSONArray genres = json.getJSONArray("genres");
                for (int i = 0; i < genres.length(); i++) {
                    JSONObject genre = genres.getJSONObject(i);
                    // Stocker l'ID du genre (plus fiable que le nom)
                    show.getGenres().add(String.valueOf(genre.getInt("id")));
                }
            }
            
            // Récupérer les réseaux
            if (json.has("networks")) {
                JSONArray networks = json.getJSONArray("networks");
                if (networks.length() > 0) {
                    String networkName = networks.getJSONObject(0).getString("name").toLowerCase();
                    show.setNetwork(networkName);
                }
            }
            
            // Récupérer les mots-clés
            try {
                String keywordUrl = "https://api.themoviedb.org/3/tv/" + showId + "/keywords"
                    + "?api_key=" + tmdbApiKey;
                String kwResponse = restTemplate.getForObject(keywordUrl, String.class);
                if (kwResponse != null) {
                    JSONObject kwJson = new JSONObject(kwResponse);
                    JSONArray keywords = kwJson.getJSONArray("keywords");
                    for (int i = 0; i < keywords.length(); i++) {
                        String keyword = keywords.getJSONObject(i).getString("name").toLowerCase();
                        show.getKeywords().add(keyword);
                    }
                }
            } catch (Exception e) {
                // Pas de keywords
            }
            
            // Récupérer la durée moyenne des épisodes
            if (json.has("episode_run_time") && json.getJSONArray("episode_run_time").length() > 0) {
                show.setEpisodeRuntime(json.getJSONArray("episode_run_time").getInt(0));
            }
            
            // Récupérer les certifications
            try {
                String certUrl = "https://api.themoviedb.org/3/tv/" + showId + "/content_ratings"
                    + "?api_key=" + tmdbApiKey;
                String certResponse = restTemplate.getForObject(certUrl, String.class);
                if (certResponse != null) {
                    JSONObject certJson = new JSONObject(certResponse);
                    JSONArray results = certJson.getJSONArray("results");
                    Map<String, String> certMap = new HashMap<>();
                    for (int i = 0; i < results.length(); i++) {
                        JSONObject c = results.getJSONObject(i);
                        String iso = c.getString("iso_3166_1");
                        String rating = c.getString("rating");
                        certMap.put(iso, rating);
                    }
                    show.setCertifications(certMap);
                }
            } catch (Exception e) {
                // Pas de certifications
            }
            
            System.out.println("[DEBUG] Fetched: " + show.getTitle() + " | genres=" + show.getGenres() + " | runtime=" + show.getEpisodeRuntime());
            
            return show;
            
        } catch (Exception e) {
            System.err.println("Erreur récupération détails ID " + showId + ": " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }
    
    /**
     * Détermine l'âge recommandé en utilisant les certifications, les genres IDs et un mapping de titres.
     */
    private String determineAgeRating(ShowInfo show) {
        // 1. Mapping de titres connus (priorité la plus haute)
        String titleLower = show.getTitle() != null ? show.getTitle().toLowerCase() : "";
        String[] toddlerTitles = {"teletubbies", "petit ours brun", "babar", "dora", "peppa pig", "bluey", "paw patrol", "miffy", "totoro"};
        for (String known : toddlerTitles) {
            if (titleLower.contains(known)) {
                return "0+";
            }
        }
        
        // 2. Priorité aux certifications TMDB
        Map<String, String> certs = show.getCertifications();
        if (certs != null && !certs.isEmpty()) {
            String us = certs.get("US");
            if (us != null) {
                switch (us) {
                    case "TV-Y": return "0+";
                    case "TV-Y7": return "3+";
                    case "TV-G": return "3+";
                    case "TV-PG": return "6+";
                    case "TV-14": return "14+";
                    case "TV-MA": return "18+";
                }
            }
            String fr = certs.get("FR");
            if (fr != null) {
                if (fr.contains("Tout publics") || fr.contains("TP") || fr.contains("G") || fr.contains("0+")) {
                    return "0+";
                }
                if (fr.contains("10+")) return "10+";
                if (fr.contains("12+")) return "12+";
                if (fr.contains("16+")) return "16+";
            }
        }
        
        // 3. Utilisation des genres IDs
        List<String> genreIds = show.getGenres();
        // 10762 = Kids, 10751 = Family, 16 = Animation
        if (genreIds != null) {
            if (genreIds.contains("10762")) return "3+"; // Kids
            if (genreIds.contains("10751")) return "6+"; // Family
        }
        
        // 4. Fallback mots-clés dans titre/description
        String combined = titleLower + " " + show.getDescription().toLowerCase();
        String[] toddlerWords = {"bébé", "baby", "toddler", "tout-petit", "preschool", "maternelle", "nursery", "bébin", "bebeb"};
        for (String w : toddlerWords) {
            if (combined.contains(w)) return "0+";
        }
        
        // 5. Par défaut pour animation longue : 6+
        return "6+";
    }
    
    /**
     * Calcule le score de calme (pacing) basé sur les métadonnées TMDB
     * Score 0-100, plus c'est élevé = plus calme (LENT)
     * Nouvelle logique Mollo : partir de 50, bonus pour preschool/kids, malus pour genres rapides
     */
    private double calculatePacingScore(ShowInfo show) {
        // Nouvelle logique Mollo : partir de 50 (neutre)
        double score = 50;
        
        String title = show.getTitle() != null ? show.getTitle().toLowerCase() : "";
        String desc = show.getDescription() != null ? show.getDescription().toLowerCase() : "";
        List<String> genres = show.getGenres();
        Integer runtime = show.getEpisodeRuntime();
        String ageRating = show.getAgeRating(); // déjà déterminé
        
        // Déterminer is_preschool et is_kids
        boolean isPreschool = "0+".equals(ageRating);
        boolean isKids = isPreschool || "3+".equals(ageRating) || "6+".equals(ageRating)
                         || genres.contains("10762") || genres.contains("10751");
        
        // BONUS de calme
        if (isPreschool) {
            score += 30;
        }
        if (isKids && runtime != null && runtime < 10) {
            score += 15;
        }
        
        // MALUS de vitesse
        // Slapstick : chercher dans keywords ou description
        boolean hasSlapstick = false;
        if (show.getKeywords() != null) {
            for (String kw : show.getKeywords()) {
                String kwLower = kw.toLowerCase();
                if (kwLower.contains("slapstick") || kwLower.contains("absurd humour") || kwLower.contains("cartoon violence")) {
                    hasSlapstick = true;
                    break;
                }
            }
        }
        if (!hasSlapstick) {
            String combined = title + " " + desc;
            if (combined.contains("slapstick") || combined.contains("absurd humour") || combined.contains("cartoon violence") || combined.contains("chase") || combined.contains("fight")) {
                hasSlapstick = true;
            }
        }
        if (hasSlapstick) {
            score -= 40;
        }
        
        // Action (genre ID 28)
        if (genres.contains("28")) {
            score -= 30;
        }
        
        // Comedy (genre ID 35) et pas Kids
        if (genres.contains("35") && !isKids) {
            score -= 20;
        }
        
        // Plafonner à 60 pour Action/Comedy (sans analyse vidéo)
        if (genres.contains("28") || genres.contains("35")) {
            if (score > 60) {
                score = 60;
            }
        }
        
        // Limiter entre 0 et 100
        score = Math.max(0, Math.min(100, score));
        
        return score;
    }
    
    private void saveToDatabase(ShowInfo show) {
        supabaseService.saveShowAnalysis(show);
    }
    
    // Classe interne pour stocker les résultats du scan
    public static class ScanResult {
        public int analyzed = 0;
        public int alreadyAnalyzed = 0;
        public int failed = 0;
        public int errors = 0;
        public int skippedAge = 0; // nouvelles séries skipées car 14+/18+
        public List<ShowInfo> processedShows = new ArrayList<>();
        
        @Override
        public String toString() {
            return "ScanResult{" +
                "analyzed=" + analyzed +
                ", alreadyAnalyzed=" + alreadyAnalyzed +
                ", failed=" + failed +
                ", errors=" + errors +
                ", skippedAge=" + skippedAge +
                ", total=" + processedShows.size() +
                '}';
        }
    }
}