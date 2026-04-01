import asyncio
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

async def test_connect():
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options={"api_version": "v1beta"}
    )
    # Testing several models
    models_to_try = [
        "models/gemini-2.0-flash-exp",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-001"
    ]
    
    for model in models_to_try:
        try:
            print(f"Trying {model}...")
            async with client.aio.live.connect(model=model, config=types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                system_instruction="Keep it short.",
            )) as session:
                print(f"✅ SUCCESSFULLY connected to {model}!")
                # Just send a small message to be sure
                await session.send_client_content(turns={"parts": [{"text": "Hello"}]}, turn_complete=True)
                async for response in session.receive():
                    if response.server_content:
                        print(f"Received from {model}: {response.server_content}")
                        break
                return
        except Exception as e:
            print(f"❌ Failed to connect to {model}: {e}")

if __name__ == "__main__":
    asyncio.run(test_connect())
