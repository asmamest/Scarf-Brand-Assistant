from typing import Optional, Dict
from sqlalchemy.orm import Session
from src.core.agent_base import BaseAgent
from src.core.mcp import MCPMessage
from src.core.models import Order, OrderItem, Customer
from src.core.database import get_db

class TransactionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.db: Optional[Session] = None
        
    async def initialize(self):
        """Initialise la connexion à la base de données"""
        self.db = next(get_db())
        
    async def process(self, message: MCPMessage) -> MCPMessage:
        """Gère les transactions et les commandes"""
        action = message.content.get("action")
        
        handlers = {
            "create_order": self._create_order,
            "update_order_status": self._update_order_status,
            "process_payment": self._process_payment,
            "get_order_status": self._get_order_status
        }
        
        handler = handlers.get(action)
        if not handler:
            return MCPMessage(
                message_type="error",
                content={"error": f"Unknown action: {action}"}
            )
            
        try:
            result = await handler(message.content)
            return MCPMessage(
                message_type="transaction_response",
                content=result,
                metadata=message.metadata
            )
        except Exception as e:
            return MCPMessage(
                message_type="error",
                content={"error": str(e)}
            )
            
    async def _create_order(self, content: Dict) -> Dict:
        """Crée une nouvelle commande"""
        customer_id = content.get("customer_id")
        items = content.get("items", [])
        
        if not customer_id or not items:
            raise ValueError("Customer ID and items required")
            
        # Créer la commande
        order = Order(
            customer_id=customer_id,
            status="pending",
            total_amount=0
        )
        self.db.add(order)
        
        # Ajouter les articles
        total_amount = 0
        for item in items:
            order_item = OrderItem(
                order=order,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price_at_time=item["price"]
            )
            total_amount += item["price"] * item["quantity"]
            self.db.add(order_item)
            
        order.total_amount = total_amount
        self.db.commit()
        
        return {
            "order_id": order.id,
            "total_amount": total_amount,
            "status": "pending"
        }
        
    async def _update_order_status(self, content: Dict) -> Dict:
        """Met à jour le statut d'une commande"""
        order_id = content.get("order_id")
        new_status = content.get("status")
        
        if None in (order_id, new_status):
            raise ValueError("Order ID and status required")
            
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
            
        order.status = new_status
        self.db.commit()
        
        return {
            "order_id": order_id,
            "status": new_status
        }
        
    async def _process_payment(self, content: Dict) -> Dict:
        """Traite le paiement d'une commande"""
        order_id = content.get("order_id")
        payment_method = content.get("payment_method")
        
        if None in (order_id, payment_method):
            raise ValueError("Order ID and payment method required")
            
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
            
        # TODO: Intégrer avec un système de paiement réel
        # Simulation de paiement réussi
        order.payment_status = "paid"
        order.status = "confirmed"
        self.db.commit()
        
        return {
            "order_id": order_id,
            "status": "confirmed",
            "payment_status": "paid"
        }
        
    async def _get_order_status(self, content: Dict) -> Dict:
        """Récupère le statut d'une commande"""
        order_id = content.get("order_id")
        
        if not order_id:
            raise ValueError("Order ID required")
            
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
            
        return {
            "order_id": order_id,
            "status": order.status,
            "payment_status": order.payment_status,
            "total_amount": order.total_amount,
            "created_at": order.created_at.isoformat()
        }