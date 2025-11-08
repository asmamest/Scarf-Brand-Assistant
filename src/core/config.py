from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class ModelProvider(str, Enum):
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    LOCAL = "local"
    
class EmbeddingsProvider(str, Enum):
    SENTENCE_TRANSFORMERS = "sentence-transformers"
    OPENAI = "openai"
    LOCAL = "local"

class VectorStore(str, Enum):
    FAISS = "faiss"
    WEAVIATE = "weaviate"
    CHROMA = "chroma"

class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "scarf-assistant"
    ENVIRONMENT: str = "development"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    WHATSAPP_API_KEY: str
    
    # Model Configuration
    MODEL_PROVIDER: ModelProvider = ModelProvider.LOCAL
    MODEL_NAME: str = "mistral-7b-instruct"
    EMBEDDINGS_PROVIDER: EmbeddingsProvider = EmbeddingsProvider.SENTENCE_TRANSFORMERS
    VECTOR_STORE: VectorStore = VectorStore.FAISS
    
    # Database URLs
    DATABASE_URL: str
    REDIS_URL: str
    VECTOR_STORE_URL: Optional[str] = None
    
    # WhatsApp Configuration
    WHATSAPP_PHONE_NUMBER: str
    WHATSAPP_WEBHOOK_URL: str
    
    # Agent Configuration
    AGENT_MESSAGE_TTL: int = 3600  # 1 hour
    MAX_RETRIES: int = 3
    
    # Storage
    MEDIA_STORAGE_PATH: str = "./data/media"
    TEMP_STORAGE_PATH: str = "./data/temp"
    
    # Security
    ENCRYPTION_KEY: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()