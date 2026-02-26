FROM python:3.11-slim

# Installer FFmpeg et ses dépendances
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Créer le dossier temporaire
RUN mkdir -p /tmp/videos && chmod 777 /tmp/videos

# Exposer le port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "api.py"]