# 🛡️ PacingScore - Kids Protection

Video pacing analysis engine for children's content safety.

## 🌟 La Vision
**PacingScore** est le "Yuka" des contenus jeunesse. L'objectif est de protéger la santé cognitive des enfants en offrant aux parents un indicateur clair sur le niveau de stimulation visuelle des dessins animés.

## 🎯 Comment ça marche ?
1. Le système analyse une liste PRÉDÉFINIE de dessins animés connus
2. Il interroge l'API YouTube pour récupérer les métadonnées
3. Il calcule un score de calme basé sur la durée, le titre et la description
4. Il détermine automatiquement la tranche d'âge recommandée
5. Les résultats sont stockés dans Supabase pour le frontend

## 📊 Indicateurs
- **Indice de Calme (%)** : Plus le score est élevé, plus le rythme est serein
- **Âge Recommandé** : 0+, 3+, 6+, 10+, 14+
- **Exemples** :
  - Cocomelon : 28% (très stimulant)
  - Babar : 95% (très calme)

## 🚀 Fonctionnalités
- [x] Analyse automatique de dessins animés connus
- [x] Détection d'âge recommandé
- [x] Dashboard Kids-Friendly
- [x] Recherche par âge et score

## 🛠️ Stack Technique
- Backend : Spring Boot 3 + YouTube Data API v3
- Frontend : Angular 18
- Database : Supabase

## 📦 Installation
1. `git clone ...`
2. Créer un fichier `.env` avec vos clés Supabase
3. `cd frontend && npm install`
4. `npm start` pour le frontend
5. `./mvnw spring-boot:run` pour le backend

## 🔐 Sécurité
- Les clés API doivent être dans un fichier `.env` local (jamais commité)
- Seule la clé publique peut être dans `environment.ts`