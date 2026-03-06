from core.env import env
import google.generativeai as genai

genai.configure(api_key=env.GEMINI_AI_API_KEY)
model_type = "gemini-2.5-flash"
model = genai.GenerativeModel(model_type)
