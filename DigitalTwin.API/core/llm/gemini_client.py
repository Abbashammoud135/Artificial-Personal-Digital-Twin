# from langchain_ollama import ChatOllama

# def get_llm():
#     return ChatOllama(
#         model="llama3",
#         temperature=0.3
#     )

from google import genai
import os

_client = None

def get_gemini_client():
    global _client

    if _client is None:
        _client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    return _client