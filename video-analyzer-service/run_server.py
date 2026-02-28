"""
Script de lancement du serveur Flask pour le débogage
"""
import api
from waitress import serve

print("=" * 60)
print("Lancement du serveur PacingScore")
print("=" * 60)
print(f"URL: http://localhost:5000")
print(f"Interface web: http://localhost:5000")
print("=" * 60)

# Configuration de Flask
app = api.app
CONFIG = api.CONFIG

# Lancement avec Waitress (production)
try:
    serve(
        app,
        host=CONFIG["host"],
        port=CONFIG["port"],
        threads=4,
        channel_timeout=60
    )
except Exception as e:
    print(f"Erreur Waitress: {e}")
    print("Lancement avec Flask en mode debug...")
    app.run(
        host=CONFIG["host"],
        port=CONFIG["port"],
        debug=True,
        use_reloader=False
    )