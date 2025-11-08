from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from src.core.agent_base import BaseAgent
from src.core.mcp import MCPMessage
from src.core.models import Product, Order
from src.core.database import get_db

class InventoryAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.db: Optional[Session] = None
        
    async def initialize(self):
        """Initialise la connexion à la base de données"""
        self.db = next(get_db())
        
    async def process(self, message: MCPMessage) -> MCPMessage:
        """Gère les requêtes liées à l'inventaire"""
        action = message.content.get("action")
        
        handlers = {
            "check_availability": self._check_availability,
            "reserve_product": self._reserve_product,
            "update_stock": self._update_stock,
            "get_similar_products": self._get_similar_products
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
                message_type="inventory_response",
                content=result
            )
        except Exception as e:
            return MCPMessage(
                message_type="error",
                content={"error": str(e)}
            )
            
    async def _check_availability(self, content: Dict) -> Dict:
        """Vérifie la disponibilité d'un produit"""
        product_id = content.get("product_id")
        if not product_id:
            raise ValueError("Product ID required")
            
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
            
        return {
            "product_id": product_id,
            "available": product.stock_quantity > 0,
            "quantity": product.stock_quantity
        }
        
    async def _reserve_product(self, content: Dict) -> Dict:
        """Réserve une quantité de produit pour une commande"""
        product_id = content.get("product_id")
        quantity = content.get("quantity", 1)
        
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
            
        if product.stock_quantity < quantity:
            raise ValueError("Insufficient stock")
            
        # Réserver le stock
        product.stock_quantity -= quantity
        self.db.commit()
        
        return {
            "product_id": product_id,
            "reserved_quantity": quantity,
            "remaining_stock": product.stock_quantity
        }
        
    async def _update_stock(self, content: Dict) -> Dict:
        """Met à jour le stock d'un produit"""
        product_id = content.get("product_id")
        new_quantity = content.get("quantity")
        
        if None in (product_id, new_quantity):
            raise ValueError("Product ID and quantity required")
            
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
            
        product.stock_quantity = new_quantity
        self.db.commit()
        
        return {
            "product_id": product_id,
            "new_quantity": new_quantity
        }
        
    async def _get_similar_products(self, content: Dict) -> Dict:
        """Trouve des produits similaires basés sur l'embedding"""
        product_id = content.get("product_id")
        limit = content.get("limit", 5)
        
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
            
        similar_products = (
            product.similar_products
            .filter(Product.stock_quantity > 0)
            .limit(limit)
            .all()
        )
        
        return {
            "product_id": product_id,
            "similar_products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "stock_quantity": p.stock_quantity
                }
                for p in similar_products
            ]
        }