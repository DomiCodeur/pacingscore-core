# Spécification Technique : Analyse Vidéo Réelle des Cuts de Scène

## Objectif
Détecter automatiquement la fréquence des changements de scène (cuts) dans une vidéo pour évaluer son impact sur les enfants.

## Méthode : Analyse FFmpeg + Algorithmes de Détection

### 1. Méthode Légère (Métadonnées + Analyse locale)

#### Solution A : Utiliser yt-dlp + FFmpeg local
```
yt-dlp --format best [URL] → téléchargement local
ffprobe -v error -show_entries format=duration [fichier] → durée totale
ffmpeg -i [fichier] -vf "select='gt(scene,0.4)',metadata=print:file=-" → détection de scènes
```

**Avantages :**
- Pas d'API tierce coûteuse
- Analyse réelle de la vidéo
- Contrôle total sur le processus

**Inconvénients :**
- Nécessite de télécharger les vidéos (espace disque)
- Temps de traitement
- Légalité à vérifier (DMCA, droits d'auteur)

#### Solution B : API d'analyse vidéo externe (payante mais légale)

**Options disponibles :**

1. **Google Video Intelligence API** (coûte cher)
   - Détecte les scènes automatiquement
   - Peut détecter les changements d'image
   - Coût : ~0.01$/seconde de vidéo

2. **AWS Rekognition Video** (coûte cher)
   - Analyse des scènes
   - Détecte les changements
   - Coût variable

3. **Services spécialisés enfants** (recherche à faire)
   - Common Sense Media API (si disponible)
   - Services d'analyse de contenu enfant

### 2. Approche Hybride (Recommandée)

#### Phase 1 : Détection via médonnées (gratuit)
- Utiliser YouTube Data API pour récupérer les métadonnées
- Analyser les commentaires (sentiment, longueur)
- Scraper les ratings Common Sense Media

#### Phase 2 : Analyse vidéo ciblée (coûte mais ciblé)
- Pour les séries populaires uniquement
- Utiliser yt-dlp + FFmpeg pour analyser les premières minutes
- Calculer la fréquence des cuts sur un échantillon

#### Phase 3 : Enrichissement manuel (crowdsourcing)
- Interface pour les parents de tester et noter
- Système de notation sociale (comme Yuka)
- Validation des scores par les utilisateurs

### 3. Implémentation Technique Concrète

#### Architecture Backend

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Angular                      │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                Spring Boot Backend                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │  TMDB Service (Gratuit)                           │  │
│  │  - Récupère les métadonnées des séries            │  │
│  │  - Identifie les séries enfants                    │  │
│  └───────────────────────────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │  YouTube Service (Gratuit)                         │  │
│  │  - Récupère les URLs des vidéos YouTube            │  │
│  │  - Analyse les métriques de popularité             │  │
│  └───────────────────────────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Video Analyzer (Local/Externe)                    │  │
│  │  - Télécharge les vidéos                           │  │
│  │  - Analyse avec FFmpeg                             │  │
│  │  - Calcule la fréquence des cuts                   │  │
│  └───────────────────────────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Supabase (Stockage)                               │  │
│  │  - Stocke les résultats d'analyse                  │  │
│  │  - Persistance des données                         │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 4. Algorithme FFmpeg pour Détection de Cuts

```bash
# Méthode 1 : Détection basée sur les différences d'image
ffmpeg -i input.mp4 -vf "select='gt(scene,0.4)',metadata=print:file=-" -f null -

# Méthode 2 : Compter les changements de scène
ffmpeg -i input.mp4 -vf "select='gt(scene,0.1)',showinfo" -f null - 2>&1 | grep "pts_time" | wc -l

# Méthode 3 : Extraire les frames clés
ffmpeg -i input.mp4 -vf "select='eq(pict_type,I)',showinfo" -f null - 2>&1
```

### 5. Formule de Calcul du Score de Cuts

```
cuts_per_minute = total_cuts / durée_video (en minutes)

Score de calme = 100 - (cuts_per_minute × facteur_ajustement)

Facteurs d'ajustement :
- Si cuts_per_minute < 2    → Score élevé (très calme)
- Si cuts_per_minute 2-5    → Score moyen (calme)
- Si cuts_per_minute 5-10   → Score bas (stimulant)
- Si cuts_per_minute > 10   → Score très bas (très stimulant)
```

### 6. Contraintes et Limitations

#### Légales
- **DMCA** : Téléchargement de vidéos YouTube peut être interdit
- **YouTube TOS** : Interdit de télécharger les vidéos sans autorisation
- **Droits d'auteur** : Contenu protégé

#### Techniques
- **Espace disque** : Nécessite beaucoup d'espace pour stocker les vidéos
- **Temps de traitement** : Analyse vidéo est lente
- **Coût** : Solutions cloud (AWS, Google) sont chères

### 7. Solutions Recommandées

#### Option 1 : API YouTube Data + Analyse médonnées (gratuit)
- **Limite** : Moins précis mais 100% légal
- **Coût** : Gratuit (API YouTube gratuite)
- **Précision** : Estimation basée sur les métriques

#### Option 2 : yt-dlp local + FFmpeg (coût local)
- **Avantage** : Analyse réelle, pas de coûts cloud
- **Risque** : Legalité incertaine
- **Coût** : Coût d'infrastructure local

#### Option 3 : Common Sense Media API (si disponible)
- **Avantage** : Déjà analysé par des experts
- **Coût** : Payant (à vérifier)
- **Précision** : Très élevée

### 8. Proposition de Développement

**Phase 1 (Immédiat) :**
- Utiliser l'approche médonnées (comme actuellement)
- Ajouter le scraping des ratings Common Sense Media
- Interface simple pour les parents

**Phase 2 (Futur) :**
- Développer un service d'analyse vidéo local
- Utiliser yt-dlp + FFmpeg pour les séries populaires
- Système de cache pour éviter de re-télécharger

**Phase 3 (Optimisé) :**
- Implémenter un système de crowdsourcing
- Les parents notent les séries
- La communauté valide les scores

## Conclusion

**L'analyse réelle des vidéos est possible**, mais nécessite une approche progressive :
1. Commencer avec les médonnées (légal et gratuit)
2. Ajouter l'analyse vidéo pour les séries populaires
3. Utiliser le crowdsourcing pour valider les scores
4. Optionnel : Vérifier si Common Sense Media a une API