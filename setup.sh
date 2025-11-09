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

# Téléchargement des modèles de base
if [ ! -f "$MODELS_DIR/mistral-7b-instruct-v0.2.Q4_K_M.gguf" ]; then
    echo "Téléchargement de Mistral 7B..."
    wget -P $MODELS_DIR https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
fi

# Modèles pour Virtual Try-On
if [ ! -d "$MODELS_DIR/virtual-try-on" ]; then
    echo "Téléchargement des modèles Virtual Try-On..."
    mkdir -p $MODELS_DIR/virtual-try-on
    wget -P $MODELS_DIR/virtual-try-on https://github.com/openai/clip-pytorch/releases/download/v1.0/clip-vit-base-patch32.pt
    wget -P $MODELS_DIR/virtual-try-on https://github.com/facebookresearch/pytorch3d/releases/download/v0.7.5/pytorch3d-0.7.5.zip
fi

# Modèles pour l'analyse des tendances
if [ ! -d "$MODELS_DIR/trend-analysis" ]; then
    echo "Configuration des modèles d'analyse des tendances..."
    mkdir -p $MODELS_DIR/trend-analysis
    # Les modèles seront téléchargés automatiquement par scikit-learn
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