import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import time
import uuid
import random
from jarvis_extension.logger import jarvis_logger
from jarvis_extension.brain import brain
from jarvis_extension.insights import print_insights_report
from jarvis_extension.optional_model import success_predictor

def simulate_jarvis_session():
    """
    Simulate typical user interactions with Jarvis.
    Logs each event to MongoDB in the background.
    """
    session_id = f"TEST_SESSION_{str(uuid.uuid4())[:8]}"
    print(f"🎬 Starting Demo Session: {session_id}")
    
    # 1. User Input
    user_inputs = [
        "Open WhatsApp",
        "What's the weather in Tokyo?",
        "Check my flights for tomorrow",
        "Explain how quantum computers work",
        "Set a reminder for 5pm"
    ]
    
    for text in user_inputs:
        print(f"👤 User: {text}")
        jarvis_logger.user_input(session_id, text)
        time.sleep(0.2)
        
        # 2. Logic / Intent / API Simulated Call
        if "weather" in text.lower():
            jarvis_logger.intent(session_id, "GET_WEATHER", city="Tokyo")
            jarvis_logger.api_call(session_id, "WeatherService", endpoint="GET /current")
            jarvis_logger.output(session_id, "The weather in Tokyo is currently 22 degrees and sunny.")
        elif "flights" in text.lower():
            # Force an ERROR simulation
            jarvis_logger.error(session_id, "API Authentication Failed: Invalid Key", service="FlightFinder")
            jarvis_logger.output(session_id, "I'm sorry, I'm having trouble accessing flight data right now.")
            print("❌ Simulated Error Logged")
        else:
            jarvis_logger.output(session_id, f"Understood, processing '{text}' now, sir.")
        
        # 3. Simulate Decision Flow
        jarvis_logger.decision(session_id, f"Routing '{text}' to appropriate tool.", tool="DevAgent")
        
    print("✅ Demo session completed. Waiting for logs to flush...")
    time.sleep(1) # Allow background logger to finish

def run_analysis_demo():
    print("\n🔬 Analyzing Logs...")
    print_insights_report()

if __name__ == "__main__":
    # Test 1: Generate logs
    simulate_jarvis_session()
    
    # Test 2: Run Brain and Insights
    run_analysis_demo()
    
    print("\n🎯 Success Predictor Check:")
    pred = success_predictor.predict_success("Find the cheapest flight")
    print(f"Success Likelihood for 'flights': {round(pred * 100, 2)}%")
