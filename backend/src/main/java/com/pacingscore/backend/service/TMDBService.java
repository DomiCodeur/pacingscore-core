package com.pacingscore.backend.service;

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

@Service
public class TMDBService {
    
    @Value("${tmdb.api.key}")
    private String tmdbApiKey;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * Recherche des séries animées pour enfants sur TMDB
     */
    public List<ShowInfo> searchChildrenCartoons() {
        List<ShowInfo> shows = new ArrayList<>();
        
        // Liste des séries enfants connues à rechercher
        String[] cartoonNames = {
            "baby shark", "cocomelon", "super simple songs", "baby einstein",
            "peppa pig", "bluey", "paw patrol", "dora the explorer",
            "miffy", "totoro", "my little pony", "barbapapa",
            "winnie the pooh", "berenstain bears", "pokémon",
            "astérix et obélix", "tintin", "dinosaur train", "thomas",
            "spidey", "diego", "blue's clues", "mickey mouse"
        };
        
        for (String name : cartoonNames) {
            try {
                List<ShowInfo> results = searchShow(name, "fr-FR");
                if (!results.isEmpty()) {
                    shows.add(results.get(0));
                    Thread.sleep(200);
                }
            } catch (Exception e) {
                System.err.println("Erreur pour " + name + ": " + e.getMessage());
            }
        }
        
        return shows;
    }
    
    /**
     * Recherche un seul dessin animé par titre pour récupérer son image
     * Essaie d'abord en fr-FR, puis en en-US si pas de poster
     */
    public ShowInfo findSingleShowWithFallback(String query) {
        // Essayer d'abord en français
        List<ShowInfo> resultsFr = searchShow(query, "fr-FR");
        ShowInfo showFr = resultsFr.isEmpty() ? null : resultsFr.get(0);
        
        if (showFr != null && showFr.getPosterPath() != null && !showFr.getPosterPath().isEmpty()) {
            return showFr;
        }
        
        // Sinon essayer en anglais
        List<ShowInfo> resultsEn = searchShow(query, "en-US");
        return resultsEn.isEmpty() ? null : resultsEn.get(0);
    }
    
    /**
     * Recherche un seul dessin animé par titre (langue spécifique)
     */
    private List<ShowInfo> searchShow(String query, String lang) {
        String url = "https://api.themoviedb.org/3/search/tv"
            + "?api_key=" + tmdbApiKey
            + "&language=" + lang
            + "&query=" + URLEncoder.encode(query, StandardCharsets.UTF_8);
        
        try {
            String response = restTemplate.getForObject(url, String.class);
            JSONObject json = new JSONObject(response);
            JSONArray results = json.getJSONArray("results");
            
            List<ShowInfo> shows = new ArrayList<>();
            for (int i = 0; i < Math.min(results.length(), 3); i++) {
                JSONObject item = results.getJSONObject(i);
                ShowInfo show = new ShowInfo();
                show.setId(item.getInt("id"));
                show.setTitle(item.getString("name"));
                show.setDescription(item.optString("overview", ""));
                show.setPosterPath(item.optString("poster_path"));
                show.setBackdropPath(item.optString("backdrop_path"));
                show.setFirstAirDate(item.optString("first_air_date"));
                
                // Récupérer les genres
                JSONArray genres = item.optJSONArray("genre_ids");
                if (genres != null) {
                    for (int j = 0; j < genres.length(); j++) {
                        show.getGenres().add(genres.getString(j));
                    }
                }
                
                shows.add(show);
            }
            
            return shows;
        } catch (Exception e) {
            e.printStackTrace();
            return new ArrayList<>();
        }
    }
    
    private ShowInfo searchShowById(int id, String lang) {
        String url = "https://api.themoviedb.org/3/tv/" + id
            + "?api_key=" + tmdbApiKey
            + "&language=" + lang;
        
        try {
            String response = restTemplate.getForObject(url, String.class);
            if (response == null) return null;
            
            JSONObject json = new JSONObject(response);
            ShowInfo show = new ShowInfo();
            show.setId(id);
            show.setTitle(json.getString("name"));
            show.setDescription(json.optString("overview", ""));
            show.setPosterPath(json.optString("poster_path"));
            show.setBackdropPath(json.optString("backdrop_path"));
            show.setFirstAirDate(json.optString("first_air_date"));
            
            // Récupérer les genres
            JSONArray genres = json.optJSONArray("genres");
            if (genres != null) {
                for (int i = 0; i < genres.length(); i++) {
                    String genreName = genres.getJSONObject(i).getString("name").toLowerCase();
                    show.getGenres().add(genreName);
                }
            }
            
            // Récupérer les réseaux
            JSONArray networks = json.optJSONArray("networks");
            if (networks != null && networks.length() > 0) {
                String networkName = networks.getJSONObject(0).getString("name").toLowerCase();
                show.setNetwork(networkName);
            }
            
            return show;
            
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
    
    /**
     * Récupère les détails d'une série par son ID depuis TMDB.
     * Essaie fr-FR puis en-US si pas de poster.
     */
    public ShowInfo getShowDetailsById(int id) {
        // Essayer d'abord en français
        ShowInfo show = searchShowById(id, "fr-FR");
        
        // Si pas de poster, essayer en anglais
        if (show != null && (show.getPosterPath() == null || show.getPosterPath().isEmpty())) {
            ShowInfo showEn = searchShowById(id, "en-US");
            if (showEn != null && showEn.getPosterPath() != null && !showEn.getPosterPath().isEmpty()) {
                return showEn;
            }
        }
        
        return show;
    }
    
    /**
     * Classe interne pour représenter une série TV TMDB
     */
    public static class ShowInfo {
        private int id;
        private String title;
        private String description;
        private String posterPath;
        private String backdropPath;
        private String firstAirDate;
        private String ageRating;
        private double pacingScore;
        private int episodeCount;
        private int seasonCount;
        private List<String> genres = new ArrayList<>();
        private String network;
        private List<String> keywords = new ArrayList<>();
        private Map<String, String> certifications = new HashMap<>();
        private Integer episodeRuntime; // en minutes
        private String mediaType; // "movie" ou "tv"

        // Getters and setters
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        public String getPosterPath() { return posterPath; }
        public void setPosterPath(String posterPath) { this.posterPath = posterPath; }
        public String getBackdropPath() { return backdropPath; }
        public void setBackdropPath(String backdropPath) { this.backdropPath = backdropPath; }
        public String getFirstAirDate() { return firstAirDate; }
        public void setFirstAirDate(String firstAirDate) { this.firstAirDate = firstAirDate; }
        public String getAgeRating() { return ageRating; }
        public void setAgeRating(String ageRating) { this.ageRating = ageRating; }
        public double getPacingScore() { return pacingScore; }
        public void setPacingScore(double pacingScore) { this.pacingScore = pacingScore; }
        public int getEpisodeCount() { return episodeCount; }
        public void setEpisodeCount(int episodeCount) { this.episodeCount = episodeCount; }
        public int getSeasonCount() { return seasonCount; }
        public void setSeasonCount(int seasonCount) { this.seasonCount = seasonCount; }
        public List<String> getGenres() { return genres; }
        public void setGenres(List<String> genres) { this.genres = genres; }
        public String getNetwork() { return network; }
        public void setNetwork(String network) { this.network = network; }
        public List<String> getKeywords() { return keywords; }
        public void setKeywords(List<String> keywords) { this.keywords = keywords; }
        public Map<String, String> getCertifications() { return certifications; }
        public void setCertifications(Map<String, String> certifications) { this.certifications = certifications; }
        public Integer getEpisodeRuntime() { return episodeRuntime; }
        public void setEpisodeRuntime(Integer episodeRuntime) { this.episodeRuntime = episodeRuntime; }
        public String getMediaType() { return mediaType; }
        public void setMediaType(String mediaType) { this.mediaType = mediaType; }
    }
}
