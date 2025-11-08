# Utiliser Python 3.11 slim comme base
FROM python:3.11-slim as builder

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Image finale
FROM python:3.11-slim

# Copier l'environnement virtuel
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Créer un utilisateur non-root
RUN useradd -m appuser
USER appuser

# Définir le répertoire de travail
WORKDIR /app

# Copier le code source
COPY --chown=appuser:appuser . .

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]