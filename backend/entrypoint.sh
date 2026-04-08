#!/bin/sh

# Si le profil docker est actif, on génère application.properties depuis les env vars
if [ "$SPRING_PROFILES_ACTIVE" = "docker" ]; then
  echo "Génération de application.properties pour Docker..."
  cat > /app/application.properties << EOF
supabase.url=${SUPABASE_URL}
supabase.key=${SUPABASE_SERVICE_ROLE_KEY}
tmdb.api.key=${TMDB_API_KEY}
tmdb.api.url=${TMDB_API_URL:-https://api.themoviedb.org/3}
video.analyzer.temp-dir=${VIDEO_ANALYZER_TEMP_DIR:-./temp/videos}
video.analyzer.max-duration=${VIDEO_ANALYZER_MAX_DURATION:-300}
server.port=${SERVER_PORT:-8080}
spring.application.name=pacingscore
EOF
fi

# Exécuter la commande Java
exec java $JAVA_OPTS -jar app.jar
