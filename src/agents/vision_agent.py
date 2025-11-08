from typing import Optional
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from src.core.agent_base import BaseAgent
from src.core.mcp import MCPMessage

class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.model = None
        self.processor = None
        
    async def initialize(self):
        """Initialise le modèle de vision"""
        # Utilise Salesforce BLIP-2 par défaut, mais peut être remplacé par d'autres modèles
        self.processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b")
        self.model = AutoModelForVision2Seq.from_pretrained("Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16)
        
        if torch.cuda.is_available():
            self.model = self.model.to("cuda")
            
    async def process(self, message: MCPMessage) -> MCPMessage:
        """Analyse une image et extrait des informations sur le foulard"""
        image_path = message.content.get("image_path")
        if not image_path:
            return MCPMessage(
                message_type="error",
                content={"error": "No image provided"}
            )
            
        try:
            # Charger et prétraiter l'image
            image = Image.open(image_path)
            inputs = self.processor(image, return_tensors="pt")
            
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
            # Générer la description
            outputs = self.model.generate(
                **inputs,
                max_length=50,
                num_beams=5
            )
            
            description = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Extraire les caractéristiques spécifiques au foulard
            features = self._extract_scarf_features(description)
            
            return MCPMessage(
                message_type="vision_analysis",
                content={
                    "description": description,
                    "features": features
                }
            )
            
        except Exception as e:
            return MCPMessage(
                message_type="error",
                content={"error": str(e)}
            )
            
    def _extract_scarf_features(self, description: str) -> dict:
        """Extrait les caractéristiques spécifiques au foulard depuis la description"""
        features = {
            "color": None,
            "pattern": None,
            "material": None,
            "style": None
        }
        
        # Liste des caractéristiques à rechercher
        color_candidates = [
            "rouge", "bleu", "vert", "jaune", "noir", "blanc", "rose", 
            "violet", "marron", "gris", "doré", "argenté", "multicolore"
        ]
        
        pattern_candidates = [
            "fleuri", "rayé", "à pois", "géométrique", "uni", "cachemire",
            "abstrait", "animal", "paisley", "chevron", "ethnique"
        ]
        
        material_candidates = [
            "soie", "coton", "laine", "modal", "cachemire", "polyester",
            "viscose", "lin", "satin", "mousseline"
        ]
        
        style_candidates = [
            "classique", "bohème", "moderne", "vintage", "élégant",
            "casual", "luxe", "minimaliste", "romantique"
        ]
        
        # Extraire les caractéristiques avec zero-shot classification
        for feature_type, candidates in [
            ("color", color_candidates),
            ("pattern", pattern_candidates),
            ("material", material_candidates),
            ("style", style_candidates)
        ]:
            try:
                result = self.feature_extractor(
                    description,
                    candidates,
                    hypothesis_template="Ce foulard est {}."
                )
                # Sélectionner la caractéristique avec le score le plus élevé
                if result["scores"][0] > 0.5:  # Seuil de confiance
                    features[feature_type] = result["labels"][0]
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction de {feature_type}: {str(e)}")
        
        # Recherche de motifs supplémentaires dans le texte
        dimensions_pattern = r"(\d+)\s*[x×]\s*(\d+)\s*(cm|m)"
        match = re.search(dimensions_pattern, description)
        if match:
            features["dimensions"] = f"{match.group(1)}×{match.group(2)}{match.group(3)}"
            
        return features