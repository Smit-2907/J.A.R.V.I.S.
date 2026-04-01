import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    for m in client.models.list():
        # Check supported methods in the model object if possible
        print(f"MODEL: {m.name}")
        # Metadata check
        # Some versions have .supported_generation_methods
        # print(f"  METHODS: {getattr(m, 'supported_generation_methods', 'Unknown')}")
except Exception as e:
    print(f"Error listing: {e}")
