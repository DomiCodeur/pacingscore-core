# 🛡️ PacingScore - Kids Protection

Video pacing analysis engine for children's content safety.

## 🌟 La Vision
**PacingScore** est le "Yuka" des contenus jeunesse. L'objectif est de protéger la santé cognitive des enfants en offrant aux parents un indicateur clair sur le niveau de stimulation visuelle des dessins animés.

**Référence**: Basé sur les données de **The Movie Database (TMDB)** - la plus grande base de données de films et séries au monde. Tous les dessins animés sont récupérés via l'API TMDB pour garantir des informations fiables et complètes.

## 🎯 Comment ça marche ?
1. **TMDB Integration** : Récupération des séries enfants depuis TMDB (the moviedb.org/u/devrick)
2. **Analyse automatique** : Le système analyse les métadonnées pour calculer un score de calme
3. **Détection d'âge** : Analyse des genres et des réseaux pour déterminer la tranche d'âge
4. **Stockage** : Les résultats sont sauvegardés dans Supabase pour le frontend
5. **Recherche** : Interface Netflix-like pour rechercher par âge et score

## 📊 Indicateurs
- **Indice de Calme (%)** : Plus le score est élevé, plus le rythme est serein
- **Âge Recommandé** : 0+, 3+, 6+, 10+, 14+
- **Exemples** :
  - Cocomelon : 28% (très stimulant)
  - Babar : 95% (très calme)

## 🚀 Fonctionnalités
- [x] Intégration TMDB pour base de données complète
- [x] Analyse automatique des séries enfants
- [x] Détection d'âge recommandé
- [x] Dashboard Kids-Friendly (style Netflix)
- [x] Recherche par âge et score de calme
- [x] Base de données Supabase

## 🛠️ Stack Technique
- Backend : Spring Boot 3
- Frontend : Angular 18
- Database : Supabase
- API Films/Séries : **The Movie Database (TMDB)**