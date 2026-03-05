#!/bin/bash

echo "🧹 Nettoyage..."
docker-compose down

echo "🗑 Suppression des conteneurs et volumes..."
docker system prune -f
docker volume prune -f

echo "🚀 Redémarrage des services..."
docker-compose up -d

echo "⏳ Attente des services..."
sleep 10

echo "📥 Population de la base de données..."
cd video-analyzer-service
python populate_clean_v2.py

echo "✨ C'est prêt ! Va sur http://localhost:9000"