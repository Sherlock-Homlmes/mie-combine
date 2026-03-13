from google import genai
from core.env import env

ai_model = "gemini-flash-latest"
ai_model = "gemini-flash-lite-latest"
ai_lite_model = "gemini-flash-lite-latest"
aclient = genai.Client(api_key=env.GEMINI_AI_API_KEY).aio
