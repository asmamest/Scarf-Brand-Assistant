from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import datetime
from langchain.agents import AgentExecutor
from langgraph.graph import StateGraph
from src.core.config import settings
from src.core.mcp import MCPBroker, MCPMessage
import structlog

logger = structlog.get_logger()

class BaseAgent(ABC):
    def __init__(self):
        self.mcp_broker = MCPBroker()
        self.state = {}
        self.max_retries = 3
        self.retry_count = 0
        
    @abstractmethod
    async def initialize(self):
        """Initialise l'agent avec ses ressources nécessaires"""
        pass
        
    @abstractmethod
    async def process(self, message: MCPMessage) -> MCPMessage:
        """Traite un message et retourne une réponse"""
        pass
        
    async def handle_error(self, error: Exception, context: Dict[str, Any]):
        """Gère les erreurs dans le workflow"""
        logger.error(
            "agent_error",
            agent_type=self.__class__.__name__,
            error=str(error),
            context=context
        )
        
        # Incrémenter le compteur de tentatives
        self.retry_count += 1
        
        if self.retry_count < self.max_retries:
            # Tentative de récupération
            try:
                # Réinitialiser l'agent si nécessaire
                await self.initialize()
                # Réessayer le traitement
                return await self.process(context.get("original_message"))
            except Exception as retry_error:
                logger.error(
                    "retry_failed",
                    agent_type=self.__class__.__name__,
                    error=str(retry_error)
                )
                
        # Si toutes les tentatives ont échoué ou erreur irrécupérable
        error_response = MCPMessage(
            message_type="error",
            content={
                "error": str(error),
                "agent": self.__class__.__name__,
                "recoverable": False
            },
            metadata={
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "retry_count": self.retry_count
            }
        )
        
        # Réinitialiser le compteur
        self.retry_count = 0
        
        return error_response
        
    def _validate_message(self, message: MCPMessage) -> bool:
        """Valide le format et le contenu d'un message"""
        required_fields = ["message_type", "content"]
        return all(hasattr(message, field) for field in required_fields)
        
    def _create_response(
        self, 
        message_type: str, 
        content: Dict[str, Any], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> MCPMessage:
        """Crée une réponse formatée"""
        return MCPMessage(
            message_type=message_type,
            content=content,
            metadata={
                **(metadata or {}),
                "agent": self.__class__.__name__,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        )

class AgentOrchestrator:
    def __init__(self):
        self.mcp_broker = MCPBroker()
        self.workflow = StateGraph()
        
    def register_agent(self, agent: BaseAgent, channels: List[str]):
        """Enregistre un agent avec ses canaux d'écoute"""
        pubsub = self.mcp_broker.subscribe(channels)
        # Setup agent dans le workflow LangGraph
        
    def start(self):
        """Démarre l'orchestrateur"""
        self.workflow.run()
        
    async def handle_error(self, error: Exception, context: Dict[str, Any]):
        """Gère les erreurs dans le workflow"""
        pass