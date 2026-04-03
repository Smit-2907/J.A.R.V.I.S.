import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from jarvis_extension.brain import brain

def generate_insights(limit=500):
    """
    Generate actionable improvement insights from Jarvis logs.
    """
    # 1. Load latest logs
    count = brain.load_logs(limit=limit)
    if not count:
        return {
            "summary": "No logs found to analyze.",
            "insights": []
        }

    # 2. Extract analysis
    sentiment = brain.analyze_sentiment()
    errors = brain.analyze_errors()
    patterns = brain.analyze_patterns()

    # 3. Formulate insights
    insights_list = []
    
    # Error insights
    if errors:
        most_frequent_err = list(errors.keys())[0]
        insights_list.append(f"⚠️ High error frequency: '{most_frequent_err}' is failing most often.")
        if errors.get(most_frequent_err, 0) > 5:
            insights_list.append("💡 Suggestion: Improve validation or rate-limiting for the failing module.")

    # Sentiment insights
    if sentiment < 0:
        insights_list.append("📉 User sentiment seems negative overall.")
        insights_list.append("💡 Suggestion: Consider softening Jarvis' response tone or improving error messaging.")
    elif sentiment > 0.6:
        insights_list.append("📈 User sentiment is highly positive.")

    # Usage insights
    top_apis = patterns.get("top_apis", {})
    if top_apis:
        most_used_api = list(top_apis.keys())[0]
        insights_list.append(f"📦 Most utilized service: '{most_used_api}'.")
        insights_list.append(f"💡 Suggestion: Optimize cache/performance for '{most_used_api}'.")

    # 4. Final summary
    summary = {
        "log_count": count,
        "sentiment_score": sentiment,
        "frequent_errors": errors,
        "top_patterns": patterns,
        "insights": insights_list
    }
    
    return summary

def print_insights_report():
    report = generate_insights()
    print("\n" + "="*40)
    print("🤖 JARVIS INTELLIGENCE REPORT")
    print("="*40)
    print(f"Total Logs Analyzed: {report.get('log_count')}")
    print(f"User Sentiment: {report.get('sentiment_score')} (-1.0 to 1.0)")
    
    print("\n--- TOP ERRORS ---")
    for err, count in report.get("frequent_errors", {}).items():
        print(f"[{count}] {err}")
        
    print("\n--- ACTIONABLE INSIGHTS ---")
    for insight in report.get("insights", []):
        print(f"▸ {insight}")
    print("="*40 + "\n")

# Use this to run report generator independently
if __name__ == "__main__":
    print_insights_report()
