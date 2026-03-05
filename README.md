# 🎬 PacingScore Kids (Mollo)

Le "Yuka des Dessins Animés" - Un outil pour analyser le rythme des contenus jeunesse.

## 🚀 Installation Rapide

1. Cloner le projet :
```bash
git clone https://github.com/votre-compte/pacingscore-clean.git
cd pacingscore-clean
```

2. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos API keys
```

3. Lancer avec Docker :
```bash
docker-compose up -d
```

C'est tout ! L'application est accessible sur :
- Frontend : http://localhost:9000
- API Backend : http://localhost:8080
- Analyseur : http://localhost:5000

## 🤖 Fonctionnalités

- **Auto-Update** : Les containers se mettent à jour automatiquement via Watchtower
- **Healthchecks** : Redémarrage automatique en cas de problème
- **Persistance** : Les données sont stockées dans Supabase
- **Images TMDB** : Affiches officielles pour tous les contenus

## 📊 Architecture

- **Frontend** : Angular 16+ (port 9000)
- **Backend** : Spring Boot 3 (port 8080)
- **Analyzer** : Python/OpenCV (port 5000)
- **Database** : Supabase
- **Cache Images** : TMDB + Dailymotion fallback

## 🛠 Maintenance

Les containers redémarrent automatiquement en cas de crash. Pour voir les logs :
```bash
docker-compose logs -f
```

Pour forcer une mise à jour :
```bash
docker-compose pull
docker-compose up -d
```

## 🗃 Base de données

Les données sont dans deux tables Supabase :
- `video_analyses` : Résultats d'analyse (frontend)
- `analysis_results` : Queue d'analyse

## 🔄 Processus d'analyse

1. Les vidéos sont ajoutées à la queue via `populate_clean_v2.py`
2. L'analyseur les traite une par une
3. Les résultats sont affichés sur le frontend

## 🛑 Résolution de problèmes

1. **Aucun contenu affiché** : 
   ```bash
   docker-compose restart backend
   ```

2. **Images manquantes** : 
   ```bash
   docker-compose restart frontend
   ```

3. **Analyseur bloqué** :
   ```bash
   docker-compose restart analyzer
   ```

## 📝 Limitations

- Maximum 3 épisodes par série pour éviter les doublons
- Uniquement du contenu français ou anglais
- Filtrage familial activé sur Dailymotion