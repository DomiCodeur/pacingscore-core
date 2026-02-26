# Logique d'Analyse PacingScore

## Méthodologie

Le système analyse les dessins animés en 3 étapes :

### 1. Recherche et récupération de métadonnées
- Utilise l'API YouTube Data v3
- Recherche basée sur le titre exact du dessin animé connu
- Récupère : titre, description, durée, vues, note

### 2. Calcul du score de calme

Le score est calculé selon plusieurs critères pondérés :

#### a) Durée (30% du score)
```
Si durée < 5 min  : +20 points (idéal pour tout-petits)
Si durée 5-15 min : +10 points (adaptable)
Si durée > 15 min : -10 points (risque de fatigue)
```

#### b) Titre et mots-clés (40% du score)

**Mots-clés négatifs** (réduisent le score) :
- fast, rapide, super, ultra, extreme
- action, excitement, intense, hyper
- bruit, loud, noisy

**Mots-clés positifs** (augmentent le score) :
- calm, doux, douces, slow, lent
- bedtime, dodo, sleep, relaxing
- paisible, douceur, douce

#### c) Type de contenu (30% du score)

**Catégories d'âge et scores typiques :**
- Bebés (0-2 ans) : score élevé (90+)
- Préscolaire (3-5 ans) : score moyen-élevé (70-90)
- Primaire (6-10 ans) : score moyen (50-70)
- Ado (10-14 ans) : score faible (30-50)

### 3. Détection automatique de l'âge

Le système scanne le titre et la description pour :
- Mots comme "bébé", "baby", "toddler" → 0+
- "préscolaire", "preschool", "3 ans" → 3+
- "enfant", "kids", "6 ans" → 6+
- "primaire", "elementary", "10 ans" → 10+
- "adolescent", "teen", "14 ans" → 14+

## Échelle de score

| Score | Niveau | Description |
|-------|--------|-------------|
| 90-100 | Très calme | Idéal pour tout-petits, rythme lent |
| 70-89  | Calme      | Bon rythme, adapté aux jeunes enfants |
| 50-69  | Modéré     | Rythme normal, à surveiller |
| 30-49  | Stimulant  | Rythme rapide, attention |
| 0-29   | Très stimulant | Rythme intense, peut être trop |

## Exemples concrets

### Babar (score élevé : 95%)
- Durée : ~10 minutes (optimal)
- Mots clés : "calm", "histoire", "douce"
- Type : "princesse", "gentille" → score élevé

### Cocomelon (score bas : 28%)
- Durée : variable (parfois 2-3 min, parfois plus)
- Mots clés : "fun", "dance", "music" → énergique
- Type : "rhymes", "songs" → rythme rapide

## Limites

1. **Approche métadonnées** : Pas d'analyse vidéo réelle (trop cher)
2. **Précision** : Basée sur des heuristiques, pas d'IA ML
3. **Couverture** : Seule une liste limitée de dessins animés
4. **YouTube** : Dépend de la disponibilité des vidéos et de leurs métadonnées

## Améliorations possibles

- [ ] Ajouter l'analyse des commentaires utilisateur
- [ ] Intégrer les ratings Common Sense Media
- [ ] Ajouter l'analyse des miniatures (calme vs excitant)
- [ ] Connexion à des APIs spécialisées enfants (Common Sense, etc.)