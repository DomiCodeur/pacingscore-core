# 🛡️ PacingScore - Kids Protection

## 🌟 La Vision
**PacingScore** est le "Yuka" des contenus jeunesse. L'objectif est de protéger la santé cognitive des enfants en offrant aux parents un indicateur clair sur le niveau de stimulation visuelle des dessins animés.

## 📊 Indicateurs
- **Indice de Calme (%)** : Plus le score est élevé, plus le rythme est serein
- **Âge Recommandé** : 0+, 3+, 6+, 10+, 14+
- **Cuts Per Minute** : Analyse technique de la vitesse de montage

## 🚀 Fonctionnalités
- [x] Moteur de recherche de shows
- [x] Analyse FFmpeg
- [x] Dashboard Kids-Friendly

## 🛠️ Stack Technique
- Backend : Spring Boot 3
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