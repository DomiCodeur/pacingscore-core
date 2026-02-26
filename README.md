# 🛡️ PacingScore - Kids Protection

Video pacing analysis engine for children's content safety - **Analyse réelle des cuts de scène**.

## 🌟 La Vision
**PacingScore** est le "Yuka" des contenus jeunesse. L'objectif est de protéger la santé cognitive des enfants en offrant aux parents un indicateur clair sur le niveau de stimulation visuelle des dessins animés.

**Innovation technique** : Le système utilise **FFmpeg + yt-dlp** pour analyser réellement les vidéos et détecter la fréquence des cuts de scène (changements de scène), pas seulement les médonnées.

**Référence** : Les séries sont récupérées via **TMDB** (themoviedb.org/u/devrick) puis analysées en temps réel.

## 🎯 Méthodologie : Analyse Réelle des Cuts de Scène

### Le Problème
Un dessin animé avec **beaucoup de cuts de scène** (changements de scène rapides) est mauvais pour les enfants car :
- Capte l'attention de manière artificielle
- Empêche la concentration et la réflexion
- Crée une surstimulation cognitive nocive

### La Solution : Analyse Vidéo Réelle

Le système utilise **FFmpeg** pour analyser les vidéos et détecter les changements de scène :

#### 1. **Téléchargement**
```bash
yt-dlp --download-sections "*0:00-5:00" [URL]  # Télécharge les 5 premières minutes
```

#### 2. **Détection des cuts**
```bash
ffmpeg -i video.mp4 -vf "select='gt(scene,0.4)',metadata=print:file=-"
```

L'analyse détecte les changements d'image avec un seuil de 0.4 :
- Seuil bas = plus de détection de petits changements
- Seuil haut = seuls les changements majeurs sont détectés

#### 3. **Calcul du score**

```
cuts_per_minute = total_cuts / durée (en minutes)

Score = 100 - (cuts_per_minute × facteur)

Règles :
- < 2 cuts/min    → 95% (très calme)
- 2-5 cuts/min    → 75% (calme)
- 5-10 cuts/min   → 50% (modéré)
- 10-15 cuts/min  → 30% (stimulant)
- > 20 cuts/min   → 5% (très stimulant)
```

### Exemples Concrets (simulés)

| Dessin animé | Cuts/min | Score | Analyse |
|-------------|----------|-------|---------|
| **Cocomelon** | ~25-30 | **5%** 🔴 | Rythme ultra-rapide, cuts très fréquents |
| **Babar** | ~1-2 | **95%** 🟩 | Rythme calme, cuts rares |
| **Baby Shark** | ~40+ | **2%** 🔴 | Extrêmement rythmé |
| **Totoro** | ~0.5 | **98%** 🟩 | Film très calme, cuts quasi inexistants |

### Technologies

| Outil | Rôle | Installation |
|-------|------|--------------|
| **yt-dlp** | Télécharger les vidéos YouTube | `pip install yt-dlp` |
| **FFmpeg** | Analyser les images et détecter les cuts | `apt install ffmpeg` ou `brew install ffmpeg` |

### Avantages de cette approche

✅ **Précise** : Analyse réelle de la vidéo, pas d'estimation  
✅ **Objective** : Basée sur les changements d'image, pas sur les mots-clés  
✅ **Reproductible** : Méthode standard utilisée par les professionnels  
✅ **Adaptable** : Seuil ajustable selon les besoins  

### Limites

⚠️ **Légalité** : Vérifier les conditions d'utilisation YouTube  
⚠️ **Performance** : Analyse vidéo nécessite du temps et de l'espace  
⚠️ **Coût infrastructure** : Nécessite un serveur capable d'exécuter FFmpeg

## 📊 Indicateurs
- **Indice de Calme (%)** : Plus le score est élevé, plus le rythme est serein
- **Âge Recommandé** : 0+, 3+, 6+, 10+, 14+
- **Exemples** :
  - Cocomelon : 28% (très stimulant)
  - Babar : 95% (très calme)

## 🚀 Fonctionnalités

### Analyse Vidéo Réelle (ASL - Average Shot Length)
- [x] **Analyse des cuts de scène** avec PySceneDetect + FFmpeg
- [x] **Métrique ASL** : Durée moyenne des plans en secondes
- [x] **Scoring objectif** : Basé sur la fréquence réelle des changements de scène
- [x] **Analyse des trailers** : Utilise les bandes-annonces YouTube depuis TMDB
- [x] **Service Python** : Micro-service indépendant pour l'analyse vidéo

### Pipeline Complet
- [x] **Récupération TMDB** : Séries Animation + Family
- [x] **Téléchargement** : yt-dlp télécharge 2 minutes de vidéo
- [x] **Détection** : FFmpeg détecte les scènes avec seuil ajustable
- [x] **Calcul ASL** : `Durée totale / Nombre de scènes`
- [x] **Score** : `100 - (facteur × ASL bas)`
- [x] **Stockage** : Supabase pour persistance

### Interface
- [x] Dashboard Kids-Friendly (style Netflix)
- [x] Recherche par âge et score de calme
- [x] Détection d'âge recommandé (0+, 3+, 6+, 10+, 14+)
- [x] Évaluation détaillée des séries

### Technologies
- [x] **Backend** : Spring Boot 3 + Java 17
- [x] **Analyse vidéo** : Python + PySceneDetect + FFmpeg
- [x] **Téléchargement** : yt-dlp
- [x] **Base de données** : Supabase
- [x] **Frontend** : Angular 18

## 🛠️ Stack Technique

### Architecture Microservices

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Frontend Angular 18                             │
│                    (Interface Netflix + Admin Panel)                     │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Spring Boot Backend                               │
│  ┌──────────────────────────────┬──────────────────────────────────┐   │
│  │  TMDB Service                │  YouTube Service                 │   │
│  │  - Récupère séries enfants   │  - Trouve vidéos YouTube        │   │
│  └──────────────────────────────┴──────────────────────────────────┘   │
│                                        │                                 │
│                                        ▼                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  VideoAnalyzerService (Java) - Alternative locale                │  │
│  │  - yt-dlp + FFmpeg (si outils installés)                        │  │
│  │  - Analyse réelle des cuts                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                        │                                 │
│                                        ▼                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Video Analyzer Service (Python) - RECOMMANDÉ                    │  │
│  │  - API Flask (port 5000)                                        │  │
│  │  - PySceneDetect + FFmpeg                                       │  │
│  │  - Métrique ASL (Average Shot Length)                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Supabase (PostgreSQL)                                │
│                     Stockage des résultats                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Technologies

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Backend** | Spring Boot 3 | Orchestration des services |
| **Analyse vidéo** | Python + PySceneDetect | Détection des cuts de scène |
| **Téléchargement** | yt-dlp | Téléchargement vidéo YouTube |
| **Analyse image** | FFmpeg + OpenCV | Détection des changements de scène |
| **Frontend** | Angular 18 | Interface utilisateur |
| **BDD** | Supabase (PostgreSQL) | Persistance des données |
| **API Films** | TMDB | Base de données des séries |
| **API YouTube** | YouTube Data v3 | Métadonnées des vidéos