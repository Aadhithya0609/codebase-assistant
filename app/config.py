from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")
REDIS_URL = os.getenv("REDIS_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_ENV = os.getenv("APP_ENV", "development")
