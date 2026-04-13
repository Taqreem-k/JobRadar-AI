from google import genai
from app.config import GEMINI_API_KEY

class BaseAgent:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash"