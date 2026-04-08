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
     * @param force si true, réanalyse même les séries déjà présentes en base
     */
    public ScanResult scanChildrenAnimations(boolean force) {
        return scanChildrenAnimations(force, 1, 5);
    }

    public ScanResult scanChildrenAnimations(boolean force, int maxPages) {
        return scanChildrenAnimations(force, 1, maxPages);
    }

    public ScanResult scanChildrenAnimations(boolean force, int startPage, int maxPages) {
        ScanResult result = new ScanResult();

        for (int page = startPage; page < startPage + maxPages; page++) {
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

                    // Vérifier si déjà analysé (sauf si force=true)
                    if (showAlreadyAnalyzed(showId) && !force) {
                        System.out.println(" => Already exists, skipping");
                        result.alreadyAnalyzed++;
                        continue;
                    }

                    // Récupérer les détails complets
                    ShowInfo show = fetchMediaDetails(showId, "tv", showJson);

                    if (show != null) {
                        // Filtre absolu : seulement genre 16 (Animation)
                        List<String> genres = show.getGenres();
                        if (genres == null || !genres.contains("16")) {
                            System.out.println(" => Skipping (no Animation genre)");
                            result.skippedAge++;
                            continue;
                        }

                        // Blacklist titre
                        String titleLower = show.getTitle() != null ? show.getTitle().toLowerCase() : "";
                        if (titleLower.contains("terrorist") || titleLower.contains("pulse") || titleLower.contains("jennifer") || titleLower.contains("muthers") || titleLower.contains("dead") || titleLower.contains("horror")) {
                            System.out.println(" => Skipping (blacklist title)");
                            result.skippedAge++;
                            continue;
                        }

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

                        // 🛡️ VALIDATION CROISÉE : Pacing vs Âge
                        // Si série classée 0+ ou 3+ mais pacing < 60 (trop rapide), remonter à 6+
                        // Un bébé ne doit pas voir un programme rapide, même si les mots-clés/disney disent "0+"
                        if ((age.equals("0+") || age.equals("3+")) && score < 60) {
                            System.out.println(" =>[Mollo] Pacing too high for age " + age + " (score:" + score + ") → adjusting to 6+");
                            age = "6+";
                            show.setAgeRating(age);
                        }

                        // Créer une tâche d'analyse avec métadonnées complètes (pas d'estimation séparée)
                        supabaseService.createAnalysisTask(show);

                        result.analyzed++;
                        result.processedShows.add(show);

                        System.out.println("✓ Analyzed & queued: " + show.getTitle() + " (score:" + score + "%, age:" + age + ")");
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

    /**
     * Scanne les films d'animation pour enfants sur TMDB
     * Utilise discover/movie avec genres Animation + Family
     * @param force si true, réanalyse même les films déjà présents en base
     */
    public ScanResult scanMovies(boolean force) {
        return scanMovies(force, 5);
    }

    /**
     * Scanne les films d'animation pour enfants sur TMDB (version paramétrable)
     * Utilise discover/movie avec genres Animation + Family
     * @param force si true, réanalyse même les films déjà présents en base
     * @param maxPages nombre de pages à scanner (5 par défaut)
     */
    public ScanResult scanMovies(boolean force, int maxPages) {
        ScanResult result = new ScanResult();

        for (int page = 1; page <= maxPages; page++) {
            try {
                System.out.println("Scanning movies page " + page + "/" + maxPages);

                String discoveryUrl = "https://api.themoviedb.org/3/discover/movie"
                    + "?api_key=" + tmdbApiKey
                    + "&language=fr-FR"
                    + "&with_genres=16,10751"  // Animation + Family
                    + "&sort_by=popularity.desc"
                    + "&page=" + page;

                String response = restTemplate.getForObject(discoveryUrl, String.class);
                if (response == null) break;

                JSONObject json = new JSONObject(response);
                JSONArray results = json.getJSONArray("results");

                System.out.println("Movies page " + page + " returned " + results.length() + " films");

                for (int i = 0; i < results.length(); i++) {
                    JSONObject movieJson = results.getJSONObject(i);
                    int movieId = movieJson.getInt("id");
                    String title = movieJson.getString("title");
                    System.out.println("Processing movie: " + title + " (ID:" + movieId + ")");

                    // Vérifier si déjà analysé (sauf si force=true)
                    if (showAlreadyAnalyzed(movieId) && !force) {
                        System.out.println(" => Already exists, skipping");
                        result.alreadyAnalyzed++;
                        continue;
                    }

                    // Récupérer les détails complets avec mediaType="movie"
                    ShowInfo show = fetchMediaDetails(movieId, "movie", movieJson);

                    if (show != null) {
                        // Filtre absolu : seulement genre 16 (Animation)
                        List<String> genres = show.getGenres();
                        if (genres == null || !genres.contains("16")) {
                            System.out.println(" => Skipping (no Animation genre)");
                            result.skippedAge++;
                            continue;
                        }

                        // Blacklist titre
                        String titleLower = show.getTitle() != null ? show.getTitle().toLowerCase() : "";
                        if (titleLower.contains("terrorist") || titleLower.contains("pulse") || titleLower.contains("jennifer") || titleLower.contains("muthers") || titleLower.contains("dead") || titleLower.contains("horror")) {
                            System.out.println(" => Skipping (blacklist title)");
                            result.skippedAge++;
                            continue;
                        }

                        // Déterminer l'âge (adapté pour les films)
                        String age = determineAgeRating(show);
                        show.setAgeRating(age);

                        // FILTRE : ignorer les films 14+ et 18+ (pas pour enfants)
                        if ("14+".equals(age) || "18+".equals(age)) {
                            System.out.println(" => Skipping (age " + age + ")");
                            result.skippedAge++;
                            continue;
                        }

                        // Calculer le score
                        double score = calculatePacingScore(show);
                        show.setPacingScore(score);

                        // Validation croisée (adaptée éventuellement pour films)
                        if ((age.equals("0+") || age.equals("3+")) && score < 60) {
                            System.out.println(" =>[Mollo] Pacing too high for age " + age + " (score:" + score + ") → adjusting to 6+");
                            age = "6+";
                            show.setAgeRating(age);
                        }

                        // Créer une tâche d'analyse avec métadonnées complètes (pas d'estimation séparée)
                        supabaseService.createAnalysisTask(show);
                        
                        result.analyzed++;
                        result.processedShows.add(show);
                        
                        System.out.println("✓ Analyzed & queued: " + show.getTitle() + " (score:" + score + "%, age:" + age + ")");
                    } else {
                        System.err.println("✗ Failed to get details for movie ID " + movieId);
                        result.failed++;
                    }

                    Thread.sleep(200);
                }

                if (results.length() == 0) break;

            } catch (Exception e) {
                System.err.println("Erreur page movies " + page + ": " + e.getMessage());
                e.printStackTrace();
                result.errors++;
            }
        }

        return result;
    }

    /**
     * Lance un import massif de 50 pages pour TV et films.
     * Retourne un résumé textuel des résultats.
     */
    /**
     * Lance un import massif diversifié (Séries Enfants, Films d'animation, et Médias plus âgés)
     */
    public String performMassiveImport() {
        // 1. Séries Enfants (0-6 ans) - pages 1 à 200
        scanChildrenAnimations(false, 200); 
        
        // 2. Films d'animation (Grand public) - pages 1 à 200
        scanMovies(false, 200);

        // 3. Séries d'animation variées (pré-ados/ados) - pages 1 à 150
        // On fait deux variantes : genre=16 (Animation pure) et genre=16+10759 (Animation+Action)
        try {
            for (int page = 1; page <= 150; page++) {
                scanGenreSpecific("tv", "16", page); // Animation seule
                scanGenreSpecific("tv", "16,10759", page); // Animation + Action/Adventure
            }
        } catch (Exception e) {
            System.err.println("Erreur scan séries variées: " + e.getMessage());
        }

        return "Import massif d'animation lancé ! Seuls les genres Animation (et Famille pour jeunes enfants) sont importés. Consultez les logs.";
    }

    /**
     * Scan spécifique par combinaison de genres (pour élargir la variété d'âges)
     */
    private void scanGenreSpecific(String type, String genres, int page) throws Exception {
        try {
            String discoveryUrl = "https://api.themoviedb.org/3/discover/" + type
                + "?api_key=" + tmdbApiKey
                + "&language=fr-FR"
                + "&with_genres=" + genres
                + "&sort_by=popularity.desc"
                + "&page=" + page;

            String response = restTemplate.getForObject(discoveryUrl, String.class);
            JSONObject json = new JSONObject(response);
            JSONArray results = json.getJSONArray("results");

            for (int i = 0; i < results.length(); i++) {
                JSONObject itemJson = results.getJSONObject(i);
                int id = itemJson.getInt("id");
                
                if (showAlreadyAnalyzed(id)) continue;
                
                ShowInfo show = fetchMediaDetails(id, type, itemJson);
                if (show != null) {
                    // Filtre absolu : seulement genre 16 (Animation)
                    List<String> showGenres = show.getGenres();
                    if (showGenres == null || !showGenres.contains("16")) {
                        System.out.println(" => Skipping (no Animation genre)");
                        continue;
                    }

                    // Blacklist titre
                    String titleLower = show.getTitle() != null ? show.getTitle().toLowerCase() : "";
                    if (titleLower.contains("terrorist") || titleLower.contains("pulse") || titleLower.contains("jennifer") || titleLower.contains("muthers") || titleLower.contains("dead") || titleLower.contains("horror")) {
                        System.out.println(" => Skipping (blacklist title)");
                        continue;
                    }

                    // Déterminer l'âge
                    String age = determineAgeRating(show);
                    show.setAgeRating(age);

                    // Validation croisée
                    if ((age.equals("0+") || age.equals("3+")) && show.getPacingScore() < 60) {
                        System.out.println(" =>[Mollo] Pacing too high for age " + age + " (score:" + show.getPacingScore() + ") → adjusting to 6+");
                        age = "6+";
                        show.setAgeRating(age);
                    }

                    // Sauvegarde via tâche d'analyse
                    supabaseService.createAnalysisTask(show);
                    System.out.println("✓ Analyzed & queued: " + show.getTitle() + " (score:" + show.getPacingScore() + "%, age:" + age + ")");
                }
                Thread.sleep(200);
            }
        } catch (Exception e) {
            System.err.println("Erreur scan genre " + genres + " page " + page + ": " + e.getMessage());
        }
    }

    private boolean showAlreadyAnalyzed(int tmdbId) {
        return supabaseService.showExists(tmdbId);
    }

    private ShowInfo fetchMediaDetails(int showId, String mediaType, JSONObject basicInfo) {
        try {
            System.out.println("[DEBUG] Fetching " + mediaType + " details for ID: " + showId);
            String endpoint = "https://api.themoviedb.org/3/" + mediaType + "/" + showId
                + "?api_key=" + tmdbApiKey
                + "&language=fr-FR";

            String response = restTemplate.getForObject(endpoint, String.class);
            if (response == null) {
                System.err.println("[ERROR] Null response from TMDB for ID " + showId);
                return null;
            }

            JSONObject json = new JSONObject(response);
            ShowInfo show = new ShowInfo();
            show.setId(showId);
            show.setMediaType(mediaType);

            // Title field differs: TV uses "name", Movie uses "title"
            String titleField = mediaType.equals("movie") ? "title" : "name";
            String title = json.optString(titleField, "");
            show.setTitle(title);

            // FILTRE : ignorer les titres non-latins (chinois, russe, arabe, etc.)
            if (title != null && !title.matches(".*[a-zA-Z].*")) {
                System.out.println(" => Skipping non-latin title: " + title);
                return null;
            }

            show.setDescription(json.optString("overview", ""));
            show.setPosterPath(json.optString("poster_path"));
            show.setBackdropPath(json.optString("backdrop_path"));

            // Date field: TV uses "first_air_date", Movie uses "release_date"
            String dateField = mediaType.equals("movie") ? "release_date" : "first_air_date";
            show.setFirstAirDate(json.optString(dateField));

            // Episode/season count: TV only
            if ("tv".equals(mediaType)) {
                if (json.has("number_of_episodes") && !json.isNull("number_of_episodes")) {
                    show.setEpisodeCount(json.getInt("number_of_episodes"));
                }
                if (json.has("number_of_seasons") && !json.isNull("number_of_seasons")) {
                    show.setSeasonCount(json.getInt("number_of_seasons"));
                }
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

            // Networks / Production companies: TV uses "networks", Movie uses "production_companies"
            String networkField = mediaType.equals("movie") ? "production_companies" : "networks";
            if (json.has(networkField)) {
                JSONArray networks = json.getJSONArray(networkField);
                if (networks.length() > 0) {
                    String networkName = networks.getJSONObject(0).getString("name").toLowerCase();
                    show.setNetwork(networkName);
                }
            }

            // Récupérer les mots-clés
            try {
                String keywordUrl = "https://api.themoviedb.org/3/" + mediaType + "/" + showId + "/keywords"
                    + "?api_key=" + tmdbApiKey;
                String kwResponse = restTemplate.getForObject(keywordUrl, String.class);
                if (kwResponse != null) {
                    JSONObject kwJson = new JSONObject(kwResponse);
                    JSONArray keywords;
                    if (kwJson.has("keywords")) {
                        keywords = kwJson.getJSONArray("keywords");
                    } else if (kwJson.has("results")) {
                        keywords = kwJson.getJSONArray("results");
                    } else {
                        keywords = null;
                    }
                    if (keywords != null) {
                        for (int i = 0; i < keywords.length(); i++) {
                            JSONObject kw = keywords.getJSONObject(i);
                            String keyword = kw.getString("name").toLowerCase();
                            show.getKeywords().add(keyword);
                        }
                    }
                }
            } catch (Exception e) {
                // Pas de keywords
            }

            // Runtime: TV uses "episode_run_time" array, Movie uses "runtime" (in minutes)
            if ("tv".equals(mediaType)) {
                if (json.has("episode_run_time") && json.getJSONArray("episode_run_time").length() > 0) {
                    show.setEpisodeRuntime(json.getJSONArray("episode_run_time").getInt(0));
                }
            } else {
                if (json.has("runtime") && !json.isNull("runtime")) {
                    show.setEpisodeRuntime(json.getInt("runtime"));
                }
            }

            // Certifications: TV only (skip for movie for now)
            if ("tv".equals(mediaType)) {
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
            } else {
                show.setCertifications(new HashMap<>());
            }

            System.out.println("[DEBUG] Fetched: " + show.getTitle() + " | mediaType=" + mediaType + " | genres=" + show.getGenres() + " | runtime=" + show.getEpisodeRuntime());

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
        String titleLower = show.getTitle() != null ? show.getTitle().toLowerCase() : "";
        String descLower = show.getDescription() != null ? show.getDescription().toLowerCase() : "";
        List<String> genreIds = show.getGenres();

        // Si les genres contiennent Horror (27), Thriller (53), Crime (80) → 18+
        if (genreIds != null) {
            if (genreIds.contains("27") || genreIds.contains("53") || genreIds.contains("80")) {
                return "18+";
            }
        }

        // 0. HARD-BLACKLIST : Franchises d'action → pas en dessous de 6+
        // Priorité absolue : si le titre contient un mot d'action, on ne peut pas être 0+ ou 3+
        String[] actionFranchises = {"avengers", "spiderman", "spider-man", "jurassic", "ninja", "beyblade", "star wars", "justice league", "superhero", "batman", "transformers", "power rangers", "lego", " marvel"};
        for (String brand : actionFranchises) {
            if (titleLower.contains(brand)) {
                // C'est une franchise d'action → minimum 6+ (voir 10+ pour les plus intenses)
                if (brand.contains("jurassic") || brand.contains("avengers") || brand.contains("spider")) {
                    return "10+";
                }
                return "6+";
            }
        }

        // 1. Mapping de titres connus (preschool)
        String[] toddlerTitles = {"teletubbies", "petit ours brun", "babar", "dora", "peppa pig", "bluey", "paw patrol", "miffy", "totoro", "caillou", "franklin", "bob le bricoleur", "docteur la peluche", "bubulle guppies", "rainbow ruby"};
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

        // 3. Utilisation des genres IDs (déjà déclaré en tête)
        // 10762 = Kids, 10751 = Family, 16 = Animation
        if (genreIds != null) {
            if (genreIds.contains("10762")) return "3+"; // Kids
            if (genreIds.contains("10751")) return "6+"; // Family
        }

        // 3b. Genres Action/Adventure/SciFi → minimum 6+ (sauf si certification très basse)
        if (genreIds != null && (genreIds.contains("28") || genreIds.contains("12") || genreIds.contains("878"))) {
            // Si on a une certification explicite (ex: TV-Y), on l'respecte
            // Sinon, on assume que c'est au moins 6+
            if (certs == null || certs.isEmpty()) {
                return "6+";
            }
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

    /**
     * Scan "diversifié" sur des pages plus lointaines (ex: 51-100) sans filtre de genre,
     * pour capturer des médias avec des âges plus variés (6+, 10+, 12+, 14+).
     * Les médias 18+ sont exclus pour rester familial large.
     */
    /* DÉSACTIVÉ - scanDiverse supprimé car import non-animé */

    /* DÉSACTIVÉ - scanGeneralPage supprimé car import non-animé */

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