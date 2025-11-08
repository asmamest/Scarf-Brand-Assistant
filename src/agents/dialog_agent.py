import json
from typing import Optional, Dict, Any
from langchain.prompts import PromptTemplate
from src.core.agent_base import BaseAgent
from src.core.mcp import MCPMessage
from src.core.config import settings, ModelProvider

class DialogAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.llm = None
        self.conversation_history = {}
        
    async def initialize(self):
        """Initialise le modèle de langage selon la configuration"""
        if settings.MODEL_PROVIDER == ModelProvider.OPENROUTER:
            from langchain_openrouter import ChatOpenRouter
            self.llm = ChatOpenRouter(
                api_key=settings.OPENROUTER_API_KEY,
                model="google/gemini-2.5-pro"
            )
        elif settings.MODEL_PROVIDER == ModelProvider.LOCAL:
            from langchain_community.llms import LlamaCpp
            self.llm = LlamaCpp(
                model_path="./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                temperature=0.7,
                max_tokens=2000,
                context_window=8192,
                gpu_layers=0  # Augmenter pour utiliser le GPU
            )
        else:  # OpenAI par défaut
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(temperature=0.7)
            
    async def process(self, message: MCPMessage) -> MCPMessage:
        """Traite un message client et génère une réponse appropriée"""
        customer_id = message.metadata.get("customer_id")
        if not customer_id:
            return self._error_response("Customer ID required")
            
        # Récupérer l'historique de conversation
        history = self.conversation_history.get(customer_id, [])
        
        # Préparer le prompt avec le contexte
        prompt = self._prepare_prompt(message.content, history)
        
        try:
            # Générer la réponse
            response = await self.llm.apredict(prompt)
            
            # Mettre à jour l'historique
            history.append({
                "role": "user",
                "content": message.content.get("text", "")
            })
            history.append({
                "role": "assistant",
                "content": response
            })
            self.conversation_history[customer_id] = history[-10:]  # Garder les 10 derniers messages
            
            return MCPMessage(
                message_type="dialog_response",
                content={"response": response},
                metadata={"customer_id": customer_id}
            )
            
        except Exception as e:
            return self._error_response(str(e))
            
    def _prepare_prompt(self, content: Dict[str, Any], history: list) -> str:
        """Prépare le prompt avec le contexte de la conversation"""
        # Template de base pour les interactions
        base_template = """Vous êtes un assistant commercial spécialisé dans les foulards.
Context de la conversation :
{context}

Message du client : {message}

Répondez de manière professionnelle, empathique et concise.
"""
        
        # Construire le contexte à partir de l'historique
        context = "\n".join([
            f"{'Client' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in history[-5:]  # Utiliser les 5 derniers messages
        ])
        
        return PromptTemplate(
            template=base_template,
            input_variables=["context", "message"]
        ).format(
            context=context,
            message=content.get("text", "")
        )
        
    def _error_response(self, error: str) -> MCPMessage:
        """Crée un message d'erreur"""
        return MCPMessage(
            message_type="error",
            content={"error": error}
        )