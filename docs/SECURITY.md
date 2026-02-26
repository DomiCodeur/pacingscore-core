# 🔐 Sécurité - Politique de Gestion des Secrets

## ⚠️ Incident Récent

Un commit a exposé des clés API sensibles (YouTube, Supabase, TMDB). Ces clés ont été **renouvelées** et le fichier a été **retiré de l'historique Git**.

## 🚨 Règles de Sécurité

### 1. JAMAIS commiter des secrets

```bash
# ❌ INTERDIT
# application.properties avec clés API
# .env avec des clés
# fichiers avec "api_key", "secret", "token", "credential"

# ✅ AUTORISÉ
# .env.example (sans clés réelles)
# application.properties.example (sans clés)
# Configuration en variables d'environnement
```

### 2. Configuration requise

Pour exécuter le projet, **créer** un fichier `application.properties` local :

```properties
# application.properties
# (À créer localement, pas à commit)

# Supabase Configuration
supabase.url=https://gjkwsrzmaecmtfozkwmw.supabase.co
supabase.key=VOTRE_CLE_SUPABASE_ICI

# TMDB Configuration
tmdb.api.key=VOTRE_CLE_TMDB_ICI
tmdb.api.url=https://api.themoviedb.org/3

# YouTube API Key (à générer)
youtube.apiKey=VOTRE_CLE_YOUTUBE_ICI

# Application Server
server.port=8080
spring.application.name=pacingscore
```

### 3. Variables d'environnement (Production)

```bash
# .env
export SUPABASE_URL=https://gjkwsrzmaecmtfozkwmw.supabase.co
export SUPABASE_KEY=VOTRE_CLE_SUPABASE
export TMDB_API_KEY=VOTRE_CLE_TMDB
export YOUTUBE_API_KEY=VOTRE_CLE_YOUTUBE
```

## 🔄 Procédure de Renouvellement

### YouTube API Key
1. Aller sur https://console.cloud.google.com/
2. Sélectionner le projet
3. APIs & Services → Credentials
4. Générer une nouvelle clé API
5. Restreindre l'usage (IPs autorisées)
6. **Désactiver l'ancienne clé immédiatement**

### TMDB API Key
1. Aller sur https://www.themoviedb.org/settings/api
2. Générer une nouvelle clé
3. Mettre à jour le fichier local

### Supabase Key
1. Aller sur https://supabase.com/
2. Project Settings → API
3. Générer une nouvelle clé
4. Mettre à jour le fichier local

## 🛡️ Bonnes Pratiques

### Local
```bash
# .gitignore
.env
application.properties
*credentials*
*secret*
*key*
```

### GitHub
- Activer "Secret scanning" (déjà activé)
- Activer "Push protection" si possible
- Revue de code avant tout merge

### Déploiement
- Utiliser GitHub Secrets
- Variables d'environnement du serveur
- Services comme AWS Secrets Manager

## 📋 Checklist Sécurité

Avant tout commit :
- [ ] Vérifier avec `git diff` si des secrets sont présents
- [ ] Utiliser `git-secrets` ou outils similaires
- [ ] Faire une revue de code
- [ ] Ne jamais commit de fichiers contenant des clés

## 🚨 En cas de fuite

1. **Immédiatement** renouveler toutes les clés exposées
2. Supprimer les commits avec `git filter-branch`
3. Pousser avec force (`git push --force`)
4. Notifier les administrateurs
5. Mettre à jour la documentation

## 🔗 Tools de Sécurité

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Git-Secrets](https://github.com/awslabs/git-secrets)
- [TruffleHog](https://github.com/trufflesecurity/trufflehog)
- [Gitleaks](https://github.com/gitleaks/gitleaks)