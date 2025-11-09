from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
import structlog
from src.core.mcp import MCPMessage
from src.agents.vision_agent import VisionAgent
from src.agents.dialog_agent import DialogAgent
from src.agents.inventory_agent import InventoryAgent
from src.agents.transaction_agent import TransactionAgent
from src.agents.virtual_try_on_agent import VirtualTryOnAgent
from src.agents.style_advisor_agent import StyleAdvisorAgent
from src.agents.trend_analyzer_agent import TrendAnalyzerAgent

logger = structlog.get_logger()

class WorkflowManager:
    def __init__(self):
        self.workflow = StateGraph()
        self.agents = {}
        self.state = {
            "conversation_history": [],
            "context": {},
            "current_agent": None,
            "results": {},
            "errors": []
        }
        
    def setup_workflow(self):
        """Configure le workflow avec tous les agents"""
        # Initialiser les agents
        self.agents = {
            "vision": VisionAgent(),
            "dialog": DialogAgent(),
            "inventory": InventoryAgent(),
            "transaction": TransactionAgent(),
            "virtual_try_on": VirtualTryOnAgent(),
            "style_advisor": StyleAdvisorAgent(),
            "trend_analyzer": TrendAnalyzerAgent()
        }
        
        # Définir les nœuds du workflow
        for name, agent in self.agents.items():
            self.workflow.add_node(name, self._create_agent_node(agent))
            
        # Configurer les transitions
        self._setup_transitions()
        
        # Compiler le workflow
        return self.workflow.compile()
        
    def _create_agent_node(self, agent: Any):
        """Crée un nœud de workflow pour un agent"""
        async def node_function(state: Dict[str, Any]):
            try:
                # Mettre à jour le contexte
                state["current_agent"] = agent.__class__.__name__
                
                # Traiter le message
                response = await agent.process(state["message"])
                
                # Stocker le résultat
                state["results"][agent.__class__.__name__] = response
                
                # Déterminer le prochain agent
                next_agent = self._determine_next_step(state, response)
                return next_agent if next_agent else END
                
            except Exception as e:
                # Gérer l'erreur
                error_state = await agent.handle_error(e, state)
                state["errors"].append(error_state)
                
                # Déterminer la récupération
                return self._handle_error_transition(state, agent.__class__.__name__)
                
        return node_function
        
    def _determine_next_step(self, state: Dict[str, Any], response: MCPMessage) -> str:
        """Détermine le prochain agent basé sur l'état actuel et la réponse"""
        current_agent = state["current_agent"]
        
        # Logique de transition basée sur l'agent actuel
        transitions = {
            "VisionAgent": {
                "success": "DialogAgent",  # Après analyse d'image, passer au dialogue
                "error": "DialogAgent"     # En cas d'erreur, demander description
            },
            "DialogAgent": {
                "product_query": "InventoryAgent",
                "purchase_intent": "TransactionAgent",
                "general": None  # Fin de la conversation
            },
            "InventoryAgent": {
                "available": "TransactionAgent",
                "not_available": "DialogAgent",
                "error": "DialogAgent"
            },
            "TransactionAgent": {
                "success": None,  # Fin de la transaction
                "error": "DialogAgent"
            }
        }
        
        # Déterminer le type de transition
        result_type = self._analyze_response(response)
        return transitions.get(current_agent, {}).get(result_type)
        
    def _analyze_response(self, response: MCPMessage) -> str:
        """Analyse la réponse pour déterminer le type de résultat"""
        if response.message_type == "error":
            return "error"
            
        content = response.content
        if "purchase_intent" in content:
            return "purchase_intent"
        elif "product_query" in content:
            return "product_query"
        elif "availability" in content:
            return "available" if content["availability"] else "not_available"
        elif "transaction_status" in content:
            return "success" if content["transaction_status"] == "completed" else "error"
            
        return "general"
        
    def _handle_error_transition(self, state: Dict[str, Any], failed_agent: str) -> str:
        """Détermine la transition en cas d'erreur"""
        # Vérifier le nombre de tentatives
        retry_count = state.get("retry_count", {}).get(failed_agent, 0)
        
        if retry_count < 3:
            # Mettre à jour le compteur de tentatives
            if "retry_count" not in state:
                state["retry_count"] = {}
            state["retry_count"][failed_agent] = retry_count + 1
            
            # Réessayer avec le même agent
            return failed_agent
            
        # Transition de fallback
        fallbacks = {
            "VisionAgent": "DialogAgent",
            "DialogAgent": "InventoryAgent",
            "InventoryAgent": "DialogAgent",
            "TransactionAgent": "DialogAgent"
        }
        
        return fallbacks.get(failed_agent, "DialogAgent")
        
    def _setup_transitions(self):
        """Configure les transitions entre les agents"""
        # Définir le point d'entrée (dialogue par défaut)
        self.workflow.set_entry_point("dialog")
        
        # Ajouter les transitions conditionnelles
        for agent_name in self.agents:
            self.workflow.add_edge(agent_name, self._determine_next_step)
            
        # Ajouter des transitions de récupération d'erreur
        for agent_name in self.agents:
            self.workflow.add_edge(
                f"{agent_name}_error",
                lambda state, agent=agent_name: self._handle_error_transition(state, agent)
            )