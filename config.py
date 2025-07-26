import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_sh8D5uIqaOgY@ep-lingering-leaf-a80llfi7-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require")
DB_HOST = os.getenv("DB_HOST", "ep-lingering-leaf-a80llfi7-pooler.eastus2.azure.neon.tech")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "neondb")
DB_USER = os.getenv("DB_USER", "neondb_owner")
DB_PASSWORD = os.getenv("DB_PASSWORD", "npg_sh8D5uIqaOgY")
