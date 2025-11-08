#!/bin/bash

# Variables
export PYTHONPATH=.
MODELS_DIR="./models"

# Création des répertoires nécessaires
mkdir -p $MODELS_DIR
mkdir -p data/media
mkdir -p data/temp

# Installation des dépendances
pip install -r requirements.txt

# Téléchargement des modèles
echo "Téléchargement des modèles..."

# Mistral 7B GGUF
if [ ! -f "$MODELS_DIR/mistral-7b-instruct-v0.2.Q4_K_M.gguf" ]; then
    echo "Téléchargement de Mistral 7B..."
    wget -P $MODELS_DIR https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
fi

# BLIP-2
if [ ! -d "$MODELS_DIR/blip2" ]; then
    echo "Téléchargement de BLIP-2..."
    mkdir -p $MODELS_DIR/blip2
    # Le modèle sera téléchargé automatiquement par HuggingFace
fi

# Sentence Transformers
if [ ! -d "$MODELS_DIR/all-MiniLM-L6-v2" ]; then
    echo "Téléchargement de Sentence Transformers..."
    mkdir -p $MODELS_DIR/all-MiniLM-L6-v2
    # Le modèle sera téléchargé automatiquement par sentence-transformers
fi

# Migration de la base de données
echo "Migration de la base de données..."
alembic upgrade head

echo "Installation terminée !"