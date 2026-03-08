# 🚀 Guide de démarrage - Architecture Mollo

## 📋 État des lieux

### Tables Supabase (doivent exister)

#### `metadata_estimations`
- `tmdb_id` (PK, TEXT)
- `title` (TEXT)
- `estimated_score` (FLOAT)
- `age_rating_guess` (TEXT)
- `metadata` (JSONB)
- `created_at` (TIMESTAMP)

#### `mollo_scores`
- `tmdb_id` (PK, TEXT, FK vers metadata_estimations)
- `real_score` (FLOAT)
- `asl` (FLOAT)  -- Average Shot Length en secondes
- `video_url` (TEXT)
- `scene_details` (JSONB)
- `analyzed_at` (TIMESTAMP)
- `source_type` (TEXT)  -- "episode" ou "trailer" (toujours "episode" dans notre implémentation)
- `video_duration` (FLOAT)  -- durée totale de la vidéo analysée
- `cuts_per_minute` (FLOAT)  -- optionnel, calculé

#### `analysis_tasks`
- `id` (UUID, PK)
- `tmdb_id` (TEXT, UNIQUE)
- `status` (TEXT)  -- "pending", "processing", "completed", "failed"
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `error_message` (TEXT, nullable)

### Backend Java
- Scanner TMDB → `metadata_estimations` + création tâche dans `analysis_tasks`
- API `/api/shows` → retourne `COALESCE(real_score, estimated_score)`

### Worker Python (Docker)
- `worker.py` : boucle infinie qui traite `analysis_tasks`
- Recherche trailer YouTube → yt-dlp
- Analyse vidéo → PySceneDetect + OpenCV
- Sauvegarde dans `mollo_scores`

---

## 🔧 Migration : ajouter les colonnes manquantes

Si ta table `mollo_scores` n'a pas encore les colonnes `source_type` et `video_duration`, exécute :

```sql
ALTER TABLE mollo_scores 
ADD COLUMN IF NOT EXISTS source_type TEXT DEFAULT 'episode',
ADD COLUMN IF NOT EXISTS video_duration FLOAT;

-- Ajouter aussi cuts_per_minute si pas présent
ALTER TABLE mollo_scores 
ADD COLUMN IF NOT EXISTS cuts_per_minute FLOAT;
```

Cela permet au worker de stocker la provenance des données (pour traçabilité) et la durée analysée.

---

## 🏁 Premier démarrage

### 1. Configurer l'environnement

Dans `video-analyzer-service/.env` :
```bash
SUPABASE_URL=https://ton-projet.supabase.co
SUPABASE_ANON_KEY=ton_anon_key
```

### 2. Lancer Docker

```bash
docker-compose up -d
```

Cela démarre :
- `backend` (Spring Boot sur port 8080)
- `analyzer` (worker Python)
- `frontend` (Angular sur port 9000)

### 3. Vérifier que le worker tourne

```bash
docker logs -f mollo-analyzer
```

Tu devrais voir :
```
[INFO] Supabase client initialized
[INFO] 🚀 Démarrage du worker Mollo
```

### 4. Lancer un scan TMDB

```bash
curl -X POST http://localhost:8080/api/analysis/scan-tmdb
```

Le backend va :
1. Récupérer les séries depuis TMDB
2. Créer des entrées dans `metadata_estimations`
3. Créer des tâches dans `analysis_tasks`

Le worker va automatiquement :
1. Voir les nouvelles tâches (`pending`)
2. **Chercher des épisodes/extraits sur Dailymotion** (pas YouTube, pas des trailers !)
3. **Filtrer les vidéos > 3 min** pour éviter les trailers biaisés
4. Télécharger un extrait (2 min max, à partir de la vidéo trouvée)
5. Analyser (ASL, cuts, motion, flashs)
6. Sauvegarder le `real_score` dans `mollo_scores` avec `source_type="episode"`
7. Marquer la tâche `completed`

> **Pourquoi Dailymotion et pas YouTube ?**
> - YouTube bloque souvent les VPS (limites d'IP)
> - Dailymotion est plus permissif
> - On trouve facilement des épisodes complets
> - Pas de risque de se faire bannir la clé API

---

## 📊 Monitoring

### Voir les logs du worker
```bash
docker logs -f mollo-analyzer
```

### Compter les tâches en attente
```sql
SELECT COUNT(*) FROM analysis_tasks WHERE status = 'pending';
```

### Voir les dernières analyses (réelles)
```sql
SELECT tmdb_id, real_score, asl, analyzed_at FROM mollo_scores ORDER BY analyzed_at DESC LIMIT 10;
```

### Voir les estimations (non encore analysées)
```sql
SELECT title, estimated_score FROM metadata_estimations ORDER BY created_at DESC LIMIT 10;
```

---

## 🔧 Problèmes courants

### Le worker ne trouve pas de trailer
→ La tâche passera en `failed`. Consulte les logs Docker.
→ Solutions :
  - Vérifie que le titre dans `metadata_estimations.title` est correct
  - Le worker fait une recherche YouTube, si pas de résultat → échec

### Erreur Supabase dans les logs
→ Vérifie `.env` (SUPABASE_URL, SUPABASE_ANON_KEY)
→ Teste la connexion avec `psql` ou l'interface Supabase

### L'API_backend erreur 500 sur `/api/shows`
→ Vérifie que les tables `mollo_scores` et `metadata_estimations` existent
→ Vérifie que le backend a bien les droits de lecture sur ces tables

---

## 🧪 Test manuel (optionnel)

Si tu veux tester l'API Flask de l'analyzer (maintenant désactivée dans Docker), tu peux :
```bash
# Remplacer le CMD du Dockerfile par "python api.py"
# Puis accéder à http://localhost:5000/health
```

Mais avec l'architecture file d'attente, ce n'est plus nécessaire.

---

## 📈 Ce que tu devrais voir après un scan

| Table | Contenu |
|-------|---------|
| `metadata_estimations` | ~100 lignes (estimations TMDB) |
| `analysis_tasks` | ~100 tâches `pending` puis `completed` |
| `mollo_scores` | ~50-100 lignes (selon succès des recherches YouTube) |
| `video_analyses` | (vide ou garde les anciennes analyses Dailymotion) |

---

## 🎯 Objectif atteint

- ✅ Le scanner TMDB ne書きplus directement dans `video_analyses`
- ✅ Les tâches sont déléguées à un worker asynchrone
- ✅ L'analyse vidéo réelle (yt-dlp + PySceneDetect) est effectuée
- ✅ Le frontend reçoit le score certifié (`real_score`) si disponible

---

**La prochaine étape** : Lance `docker-compose up -d` et watch les logs !