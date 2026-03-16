from google import genai

from core.env import env

aclient = genai.Client(api_key=env.GEMINI_AI_API_KEY).aio
