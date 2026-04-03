# 📈 Jarvis Intelligence & Learning Layer

This is a modular extension for JARVIS that provides session logging, sentiment analysis, error tracking, and success prediction.

## 📁 Components
- `db.py`: Multi-storage engine (MongoDB + JSON Fallback).
- `logger.py`: Async event-based logging worker.
- `middleware.py`: Non-invasive decorators and wrappers for integration.
- `brain.py`: Logic for sentiment, pattern, and error analysis.
- `insights.py`: Generates human-readable intelligence reports.
- `optional_model.py`: scikit-learn based success predictor.

## 🚀 Quick Start
1. Install dependencies: `pip install pymongo textblob scikit-learn joblib`
2. Run the simulation: `python test_extension.py`
3. View report: `python insights.py`

## 🔌 Integration
Use the `jarvis_extension.middleware` to wrap your existing functions without breaking them.

```python
from jarvis_extension.middleware import log_event_decorator

@log_event_decorator(event_type="INTENT")
def handle_user_command(command): ...
```
