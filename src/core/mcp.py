import json
import redis
from typing import Any, Dict, Optional
from src.core.config import settings

class MCPMessage:
    def __init__(
        self,
        message_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        ttl: int = 3600
    ):
        self.message_type = message_type
        self.content = content
        self.metadata = metadata or {}
        self.ttl = ttl

    def to_json(self) -> str:
        return json.dumps({
            "message_type": self.message_type,
            "content": self.content,
            "metadata": self.metadata,
            "ttl": self.ttl
        })

    @classmethod
    def from_json(cls, json_str: str) -> "MCPMessage":
        data = json.loads(json_str)
        return cls(
            message_type=data["message_type"],
            content=data["content"],
            metadata=data["metadata"],
            ttl=data["ttl"]
        )

class MCPBroker:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        
    def publish(self, channel: str, message: MCPMessage):
        """Publie un message MCP sur un canal"""
        self.redis_client.publish(channel, message.to_json())
        
    def subscribe(self, channels: list[str]):
        """S'abonne à des canaux MCP"""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(*channels)
        return pubsub
        
    def get_message(self, pubsub):
        """Récupère le prochain message des canaux souscrits"""
        message = pubsub.get_message()
        if message and message["type"] == "message":
            return MCPMessage.from_json(message["data"].decode())
        return None

# Exemple d'utilisation:
"""
broker = MCPBroker()

# Publication
message = MCPMessage(
    message_type="product_query",
    content={"image_url": "...", "query": "prix de ce foulard"},
    metadata={"user_id": "123", "timestamp": "..."}
)
broker.publish("vision_agent", message)

# Souscription
pubsub = broker.subscribe(["vision_agent_response"])
while True:
    message = broker.get_message(pubsub)
    if message:
        print(f"Reçu: {message.content}")
"""