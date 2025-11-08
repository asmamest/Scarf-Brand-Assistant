import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.core.config import settings
from src.core.database import get_db, init_db
from src.core.mcp import MCPBroker
from src.agents.vision_agent import VisionAgent
from src.agents.dialog_agent import DialogAgent
from src.agents.inventory_agent import InventoryAgent
from src.agents.transaction_agent import TransactionAgent
from src.core.agent_base import AgentOrchestrator

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Scarf Brand Assistant")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des agents
vision_agent = VisionAgent()
dialog_agent = DialogAgent()
inventory_agent = InventoryAgent()
transaction_agent = TransactionAgent()
orchestrator = AgentOrchestrator()
mcp_broker = MCPBroker()

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    # Initialiser la base de données
    init_db()
    
    # Initialiser les agents
    await vision_agent.initialize()
    await dialog_agent.initialize()
    await inventory_agent.initialize()
    await transaction_agent.initialize()
    
    # Enregistrer les agents dans l'orchestrateur
    orchestrator.register_agent(vision_agent, ["vision_requests"])
    orchestrator.register_agent(dialog_agent, ["dialog_requests"])
    orchestrator.register_agent(inventory_agent, ["inventory_requests"])
    orchestrator.register_agent(transaction_agent, ["transaction_requests"])
    
    # Démarrer l'orchestrateur
    orchestrator.start()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: dict, db: Session = Depends(get_db)):
    """Gère les webhooks WhatsApp"""
    try:
        # Extraire les informations du message
        message = request.get("message", {})
        message_type = message.get("type")
        customer_id = request.get("customer", {}).get("id")
        
        if not customer_id:
            raise HTTPException(status_code=400, detail="Customer ID required")
            
        if message_type == "image":
            # Traiter l'image
            image_url = message["image"]["url"]
            response = await process_image_message(image_url, customer_id)
        elif message_type == "voice":
            # Traiter le message vocal
            voice_url = message["voice"]["url"]
            response = await process_voice_message(voice_url, customer_id)
        elif message_type == "text":
            # Traiter le texte
            text = message["text"]
            response = await process_text_message(text, customer_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported message type")
            
        return {"status": "success", "response": response}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_image_message(image_url: str, customer_id: str):
    """Traite un message contenant une image"""
    # Publier un message pour l'agent de vision
    message = {
        "message_type": "vision_request",
        "content": {"image_url": image_url},
        "metadata": {"customer_id": customer_id}
    }
    mcp_broker.publish("vision_requests", message)
    
    # Attendre et retourner la réponse
    # TODO: Implémenter un mécanisme d'attente asynchrone
    return {"status": "processing"}

async def process_voice_message(voice_url: str, customer_id: str):
    """Traite un message vocal"""
    # TODO: Implémenter le traitement des messages vocaux
    return {"status": "processing"}

async def process_text_message(text: str, customer_id: str):
    """Traite un message texte"""
    message = {
        "message_type": "dialog_request",
        "content": {"text": text},
        "metadata": {"customer_id": customer_id}
    }
    mcp_broker.publish("dialog_requests", message)
    
    # TODO: Implémenter un mécanisme d'attente asynchrone
    return {"status": "processing"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)