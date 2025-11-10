# Fichier: Dockerfile

# 1. Point de départ : une image Python propre
FROM python:3.11-slim


# 2. Dépendances Système : On installe Tesseract-OCR, OpenCV et dépendances pour transformers
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Définir le dossier de travail dans le conteneur
WORKDIR /app

# 4. Copier la liste de courses et l'installer
COPY requirements.txt .

# ÉTAPE 4-Bis: Forcer l'installation de PyTorch et torchvision (version CPU uniquement)
# C'est pour "unstructured" avec hi_res strategy mais nous n'avons pas besoin des 2Go de bibliothèques GPU.
# On ajoute aussi un long timeout au cas où.
RUN pip install --no-cache-dir --timeout=1000 \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

# ÉTAPE 4-Ter: Installer le reste des paquets
RUN pip install --no-cache-dir --timeout=1000 -r requirements.txt

# 5. Copier tout le reste de votre code
COPY . .

# 6. Exposer le port de Streamlit
EXPOSE 8501

# 7. La commande pour démarrer l'app
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
