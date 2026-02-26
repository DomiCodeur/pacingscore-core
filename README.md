# 🛡️ PacingScore - Kids Protection

## 🌟 La Vision
**PacingScore** est le "Yuka" des contenus jeunesse. L'objectif est de protéger la santé cognitive des enfants en offrant aux parents un indicateur clair sur le niveau de stimulation visuelle des dessins animés.

À une époque où certains contenus (CoComelon, clips K-Pop, Skibidi Toilet) saturent l'attention avec un montage frénétique, PacingScore analyse la fréquence des coupures (cuts) pour recommander un âge adapté et préserver la capacité de concentration des plus petits.

## 📊 Indicateurs Clés
*   **Indice de Calme (%)** : Plus le score est élevé, plus le rythme est serein (ex: Babar = 95%). Un score bas indique une sur-stimulation (ex: Cocomelon = 28%).
*   **Âge Recommandé** : Catégories dynamiques (0+, 3+, 6+, 10+, 14+) basées sur la charge cognitive détectée par notre algorithme.
*   **Cuts Per Minute (CPM)** : Analyse technique de la vitesse de montage via FFmpeg.

## 🚀 Fonctionnalités
- [x] **Moteur de Recherche** : Accès instantané à une base de données de 50+ titres de référence.
- [x] **Analyseur FFmpeg** : Capacité technique à scanner n'importe quelle vidéo pour calculer son score.
- [x] **Dashboard Kids-Friendly** : Interface moderne et apaisante pour une navigation rapide.

## 🛠️ Stack Technique
*   **Backend** : Java Spring Boot 3 & FFmpeg.
*   **Frontend** : Angular 18 (Signals, Tailwind CSS, Chart.js).
*   **Database** : Supabase (PostgreSQL) avec API REST.
*   **Data** : Pipeline Python pour le crawling et le seeding de données.

## 🚀 Installation & Lancement
### 1. Prérequis
- Java 17+, Node.js 22 (via Volta recommandé), FFmpeg.

### 2. Backend
```bash
git clone ...
cd pacingscore-core
./mvnw spring-boot:run
```

### 3. Frontend
```bash
cd frontend
npm install
npx ng serve
```
Accès : `http://localhost:4200`
