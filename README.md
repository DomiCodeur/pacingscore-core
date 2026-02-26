# 🛡️ PacingScore - Kids Protection

Video pacing analysis engine for children's content safety.

## 🌟 La Vision
**PacingScore** est le "Yuka" des contenus jeunesse. L'objectif est de protéger la santé cognitive des enfants en offrant aux parents un indicateur clair sur le niveau de stimulation visuelle des dessins animés.

**Référence**: Basé sur les données de **The Movie Database (TMDB)** - la plus grande base de données de films et séries au monde. Tous les dessins animés sont récupérés via l'API TMDB pour garantir des informations fiables et complètes.

## 🎯 Comment ça marche ?
1. **Scan TMDB** : Le système scanne automatiquement TOUS les dessins animés pour enfants présents sur TMDB (animation + family genres)
2. **Analyse automatique** : Chaque série est analysée via ses métadonnées (titre, description, réseaux, mots-clés)
3. **Calcul du score** : Le score de calme est basé sur :
   - Les mots-clés dans le titre/description
   - Le réseau de diffusion (Disney, Nickelodeon, etc.)
   - Le nombre d'épisodes
   - La présence de mots comme "calme", "dodo", "bébé"
4. **Détection d'âge** : Analyse automatique pour déterminer la tranche d'âge (0+, 3+, 6+, 10+, 14+)
5. **Stockage Supabase** : Tous les résultats sont sauvegardés dans Supabase
6. **Interface parent** : Recherche Netflix-like pour trouver des séries adaptées à l'âge de l'enfant

**Liste de référence** : Toutes les données proviennent de **TMDB** (themoviedb.org) qui contient déjà une base de données complète des films et séries, incluant les dessins animés pour enfants.

## 📊 Indicateurs
- **Indice de Calme (%)** : Plus le score est élevé, plus le rythme est serein
- **Âge Recommandé** : 0+, 3+, 6+, 10+, 14+
- **Exemples** :
  - Cocomelon : 28% (très stimulant)
  - Babar : 95% (très calme)

## 🚀 Fonctionnalités
- [x] Scan automatique de tous les dessins animés TMDB
- [x] Analyse automatique par série
- [x] Détection d'âge recommandé (0+, 3+, 6+, 10+, 14+)
- [x] Dashboard Kids-Friendly (style Netflix)
- [x] Recherche par âge et score de calme
- [x] Base de données Supabase persistante
- [x] Référence : TMDB (themoviedb.org/u/devrick)

## 🛠️ Stack Technique
- Backend : Spring Boot 3
- Frontend : Angular 18
- Database : Supabase
- API Films/Séries : **The Movie Database (TMDB)**