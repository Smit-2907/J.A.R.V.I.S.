import json
from collections import Counter
from datetime import datetime
from jarvis_extension.db import db_store

# Optional imports for sentiment analysis
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None
    print("[Brain] TextBlob not found. Sentiment analysis results will be placeholder.")

class JarvisBrain:
    """
    Intelligence Analyzer Module.
    Extract patterns, errors, and sentiment from logs.
    """
    def __init__(self):
        self.logs = []

    def load_logs(self, limit=1000, session_id=None):
        query = {"session_id": session_id} if session_id else {}
        self.logs = db_store.get_logs(query, limit)
        return len(self.logs)

    def analyze_sentiment(self):
        """Analyze text inputs/outputs via TextBlob."""
        if not TextBlob or not self.logs:
            return 0.0
        
        sentiments = []
        for log in self.logs:
            text = (log.get("data", {}).get("text") or 
                   log.get("data", {}).get("response"))
            
            if text and isinstance(text, str):
                blob = TextBlob(text)
                sentiments.append(blob.sentiment.polarity)
        
        if not sentiments: return 0.5 # Neutral fallback
        avg_sentiment = sum(sentiments) / len(sentiments)
        return round(avg_sentiment, 2)

    def analyze_errors(self):
        """Count and group system errors."""
        error_logs = [l for l in self.logs if l["event_type"] == "ERROR"]
        error_counts = Counter()
        
        for err in error_logs:
            msg = err.get("data", {}).get("message") or "Unknown Error"
            # Simplify error messages for grouping
            key = msg.split(":")[0][:50]
            error_counts[key] += 1
            
        return dict(error_counts.most_common(10))

    def analyze_patterns(self):
        """Find most frequent actions and intents."""
        intent_logs = [l for l in self.logs if l["event_type"] == "INTENT"]
        api_logs = [l for l in self.logs if l["event_type"] == "API_CALL"]
        
        top_intents = Counter()
        top_apis = Counter()
        
        for intent in intent_logs:
            name = intent.get("data", {}).get("intent") or "null"
            top_intents[name] += 1
            
        for api in api_logs:
            service = api.get("data", {}).get("service") or "null"
            top_apis[service] += 1
            
        return {
            "top_intents": dict(top_intents.most_common(5)),
            "top_apis": dict(top_apis.most_common(5))
        }

# Singleton instance
brain = JarvisBrain()
