# Configuration settings
import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Use a more portable database path for cloud deployment
    DB_URL = os.getenv("DB_URL", "sqlite:///./app.db")

settings = Settings()
