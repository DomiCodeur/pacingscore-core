# Méthodologie d'Analyse : Fréquence des Cuts de Scène

## Problème
Un dessin animé avec beaucoup de "cuts" (changements de scène rapides) est mauvais pour les enfants car :
- Capte l'attention de manière artificielle
- Empêche la concentration
- Crée une surstimulation cognitive

## Solution
Analyser des indicateurs proxies pour estimer la fréquence des cuts :

### 1. Durée moyenne des épisodes (Score élevé si court = mauvais)
```
Si durée < 3 min   : +20 points (cuts fréquents)
Si durée 3-10 min  : +10 points
Si durée > 10 min  : -20 points (cuts rares)
```

### 2. Nombre d'épisodes (Score élevé si élevé = mauvais)
- Plus d'épisodes = potentiellement plus de cuts pour capter l'attention
- Petite série < 50 épisodes = +10 points
- Grande série > 200 épisodes = -10 points

### 3. Popularité / Vues (Score élevé si viral = mauvais)
- Un contenu très populaire a souvent des cuts fréquents pour "engager"
- Faible popularité = +15 points (peut-être plus calme)
- Très populaire = -15 points

### 4. Réseau de diffusion (Score élevé si certaines chaînes = mauvais)
- YouTube Originals / Netflix Kids = cuts fréquents (-10 points)
- Chaînes traditionnelles (Disney) = cuts plus modérés (+0 points)
- Chaînes éducatives = cuts rares (+15 points)

### 5. Mots-clés dans le titre/description (Score élevé si... = mauvais)
**Mots qui suggèrent des cuts fréquents :**
- "Fast", "rapide", "ultra", "hyper"
- "Fun", "funny", "comedy" (peut impliquer plus de changements)
- "Music", "dance" (rythme rapide)

**Mots qui suggèrent des cuts rares :**
- "Calm", "slow", "doux", "douce"
- "Bedtime", "dodo", "sleep", "storytime"
- "Educational", "éducatif", "learning"
- "Adventure" (si calme, peut être positif)

### 6. Genre (Score selon type de contenu)
```
Musique / Dance : -15 points (rythme rapide)
Comédie / Fun : -10 points
Éducatif / Apprendre : +10 points
Histoire / Story : +15 points
```

## Nouvelle Formule

```
score = 100 - [durée] - [popularité] - [type] - [mots-clés]

Où :
- durée = (3 min / durée épisode) * 20
- popularité = (vues / million) * 10
- type = selon genre
- mots-clés = analyse du texte
```

## Exemples Concrets

### Cocomelon (score bas = mauvais)
- Durée : variable, souvent 2-3 min → cuts fréquents
- Musique / Dance → rythme rapide
- Très viral → tendance aux cuts rapides
- **Score estimé : 28%** ✅ (très stimulant)

### Babar (score élevé = bon)
- Durée : ~10 min par épisode → cuts modérés
- Story / Adventure → rythme calme
- Moins viral → plus calme
- **Score estimé : 95%** ✅ (très calme)

## Technologies pour Analyse Réelle (Futur)
- **FFmpeg + IA** : Analyser les frames pour détecter les changements de scène
- **API YouTube** : Analyser la durée, les vues, les commentaires
- **Scraping** : Récupérer les données de Common Sense Media
- **Deep Learning** : Modèle pour prédire la fréquence des cuts

## Limites Actuelles
- Approche basée sur les métadonnées uniquement
- Nécessite des données externes pour améliorer la précision
- Les estimations peuvent être approximatives

## Améliorations Possibles
- [ ] Intégrer les ratings de Common Sense Media
- [ ] Utiliser l'analyse vidéo (si possible via API externe)
- [ ] Ajouter les retours utilisateurs parents
- [ ] Corrélation avec l'âge de l'enfant