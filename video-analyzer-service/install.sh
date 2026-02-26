#!/bin/bash

# Script d'installation pour PacingScore Video Analyzer Service
# Compatible Ubuntu/Debian

set -e

echo "=========================================="
echo "PacingScore Video Analyzer - Installation"
echo "=========================================="
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé. Installation..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

echo "✅ Python 3: $(python3 --version)"

# Vérifier FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg non trouvé. Installation..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
fi

echo "✅ FFmpeg: $(ffmpeg -version 2>&1 | head -n1)"

# Vérifier yt-dlp
if ! command -v yt-dlp &> /dev/null; then
    echo "❌ yt-dlp non trouvé. Installation..."
    sudo python3 -m pip install yt-dlp
fi

echo "✅ yt-dlp: $(yt-dlp --version)"

# Créer l'environnement virtuel
echo ""
echo "📁 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
echo "📦 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer le dossier temporaire
mkdir -p temp/videos
chmod 755 temp/videos

echo ""
echo "=========================================="
echo "✅ Installation terminée avec succès !"
echo "=========================================="
echo ""
echo "Pour démarrer le service :"
echo "  source venv/bin/activate"
echo "  python api.py"
echo ""
echo "Le service sera accessible sur :"
echo "  http://localhost:5000"
echo ""
echo "Pour analyser une vidéo :"
echo "  curl -X POST http://localhost:5000/analyze \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"video_url\": \"https://www.youtube.com/watch?v=...\"}'"
echo ""