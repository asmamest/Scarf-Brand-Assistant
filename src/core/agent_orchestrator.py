from typing import Dict, List, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from src.core.mcp import MCPMessage
import structlog

logger = structlog.get_logger()

class AgentOrchestrator:
    def __init__(self):
        self.workflow = StateGraph()
        self.agents = {}
        self.error_handlers = {}
        
    def register_agent(self, agent_name: str, agent: Any, channels: List[str]):
        """Enregistre un agent dans le workflow"""
        self.agents[agent_name] = agent
        
        # Définir le nœud dans le workflow
        def agent_node(state):
            try:
                # Traiter le message avec l'agent
                result = agent.process(state["message"])
                state["results"][agent_name] = result
                # Déterminer le prochain agent
                next_agent = self._determine_next_agent(state)
                return next_agent if next_agent else END
            except Exception as e:
                return self._handle_error(e, state, agent_name)
                
        self.workflow.add_node(agent_name, agent_node)
        
    def _determine_next_agent(self, state: Dict) -> Optional[str]:
        """Détermine le prochain agent basé sur l'état actuel"""
        message = state.get("message", {})
        current_agent = state.get("current_agent")
        
        # Logique de routage basée sur le type de message et le contexte
        routing_map = {
            "image": "vision_agent",
            "text": "dialog_agent",
            "product_query": "inventory_agent",
            "order": "transaction_agent"
        }
        
        # Si c'est une réponse d'agent, déterminer la prochaine étape
        if current_agent == "vision_agent":
            return "dialog_agent"  # Pour enrichir l'analyse visuelle
        elif current_agent == "dialog_agent":
            # Vérifier si une action spécifique est nécessaire
            intent = self._detect_intent(state)
            if intent == "purchase":
                return "inventory_agent"
            elif intent == "product_info":
                return "inventory_agent"
                
        # Par défaut, utiliser le type de message
        message_type = message.get("type", "text")
        return routing_map.get(message_type)
        
    def _detect_intent(self, state: Dict) -> str:
        """Détecte l'intention de l'utilisateur basée sur l'état"""
        # TODO: Implémenter la détection d'intention
        return "default"
        
    def _handle_error(self, error: Exception, state: Dict, agent_name: str) -> str:
        """Gère les erreurs dans le workflow"""
        logger.error(
            "agent_error",
            agent=agent_name,
            error=str(error),
            state=state
        )
        
        # Enregistrer l'erreur dans l'état
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({
            "agent": agent_name,
            "error": str(error),
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        # Stratégies de récupération
        retry_count = state.get("retry_count", {}).get(agent_name, 0)
        if retry_count < 3:  # Maximum 3 tentatives
            # Incrémenter le compteur de tentatives
            if "retry_count" not in state:
                state["retry_count"] = {}
            state["retry_count"][agent_name] = retry_count + 1
            
            # Réessayer avec le même agent
            return agent_name
            
        # Si trop de tentatives, passer au fallback
        return self._get_fallback_agent(agent_name)
        
    def _get_fallback_agent(self, failed_agent: str) -> str:
        """Retourne l'agent de fallback approprié"""
        fallbacks = {
            "vision_agent": "dialog_agent",  # Si l'analyse d'image échoue, demander description
            "dialog_agent": "inventory_agent",  # Si dialogue échoue, chercher produit direct
            "inventory_agent": "dialog_agent",  # Si inventaire échoue, informer utilisateur
            "transaction_agent": "dialog_agent"  # Si transaction échoue, expliquer problème
        }
        return fallbacks.get(failed_agent, "dialog_agent")
        
    def start(self):
        """Démarre l'orchestrateur"""
        # Configurer les transitions entre agents
        self.workflow.set_entry_point("dialog_agent")
        
        # Ajouter les transitions conditionnelles
        for agent_name in self.agents:
            self.workflow.add_edge(agent_name, self._determine_next_agent)
            
        # Compiler le workflow
        self.app = self.workflow.compile()