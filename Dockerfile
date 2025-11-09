# Fichier: Dockerfile

# 1. Point de départ : une image Python propre
FROM python:3.10-slim

# 2. Dépendances Système : On installe Tesseract-OCR
# C'est l'équivalent système de "pip install"
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# 3. Définir le dossier de travail dans le conteneur
WORKDIR /app

# 4. Copier la liste de courses et l'installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier tout le reste de votre code
COPY . .

# 6. Exposer le port de Streamlit
EXPOSE 8501

# 7. La commande pour démarrer l'app
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]