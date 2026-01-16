from langchain_google_genai import ChatGoogleGenerativeAI
import os

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key="AIzaSyAQHLvO_SzgGIkkydtWYtRfYiLgKv7lYO0"
    )
