import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

settings = Settings()