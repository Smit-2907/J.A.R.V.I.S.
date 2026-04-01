import asyncio
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

async def find_working_model():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # These are likely candidates for March 2026
    candidates = [
        "models/gemini-2.0-flash-exp",
        "models/gemini-2.0-flash",
        "models/gemini-2.5-flash-live",
        "models/gemini-3.1-flash-live-preview-12-2025",
        "models/gemini-1.5-flash",
    ]
    
    for model in candidates:
        try:
            print(f"Testing {model}...")
            async with client.aio.live.connect(model=model, config=types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                system_instruction="Hello."
            )) as session:
                print(f"✅ WORKS! {model} supports bidiGenerateContent")
                # Test if it actually speaks
                await session.send_client_content(turns={"parts": [{"text": "Say hi"}]}, turn_complete=True)
                async for response in session:
                    if response.server_content:
                        print(f"Received feedback from {model}")
                        break
                return model
        except Exception as e:
            msg = str(e)
            if "not found" in msg.lower():
                print(f"❌ {model} not found.")
            elif "403" in msg or "401" in msg:
                print(f"❌ AUTH error: {e}")
                return None
            else:
                print(f"❌ {model} failed with: {e}")
    return None

if __name__ == "__main__":
    asyncio.run(find_working_model())
