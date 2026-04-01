import asyncio
import os
import traceback
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)

async def test_live():
    model = "models/gemini-3.1-flash-live-preview"
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    try:
        print(f"Connecting to {model}...")
        async with client.aio.live.connect(model=model, config=types.LiveConnectConfig(
            response_modalities=["AUDIO"]
        )) as session:
            print("✅ Successfully connected!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_live())
