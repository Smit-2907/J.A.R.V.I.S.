import json
import logging
import os

# Optional scikit-learn imports
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline
    import joblib # For model persistence
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("[Model] scikit-learn not found. Predictor module disabled.")

class JarvisLearningModel:
    """
    Isolated, Optional ML component to predict task success based on logs.
    """
    def __init__(self, model_path="jarvis_extension/success_predictor.pkl"):
        self.model_path = model_path
        self.pipeline = None
        self._initialized = False

    def train_on_logs(self, logs):
        """
        Train a simple classifier on historical logs.
        Features: Event data / Text
        Target: SUCCESS (1) vs FAILURE (0)
        """
        if not HAS_SKLEARN: return False
        
        # 1. Feature Engineering
        texts = []
        labels = []
        
        for log in logs:
            text = log.get("data", {}).get("text") or log.get("data", {}).get("response") or ""
            # Success label: If no error followed, or explicit success info
            # Simple heuristic for this example: If no ERROR log in same session
            is_success = 1 if "ERROR" not in log.get("event_type") else 0
            
            if text:
                texts.append(text)
                labels.append(is_success)
        
        if len(texts) < 10: 
            print("[Model] Not enough data to train yet.")
            return False

        # 2. Build Pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=200, stop_words='english')),
            ('clf', LogisticRegression())
        ])
        
        # 3. Fit
        self.pipeline.fit(texts, labels)
        self._initialized = True
        
        # 4. Save
        joblib.dump(self.pipeline, self.model_path)
        print(f"[Model] Success predictor trained and saved to {self.model_path}")
        return True

    def predict_success(self, current_input):
        """Predict if current user input will likely lead to success/failure."""
        if not HAS_SKLEARN or not self._initialized: 
            # Try to load existing model
            if os.path.exists(self.model_path):
                self.pipeline = joblib.load(self.model_path)
                self._initialized = True
            else:
                return 1.0 # default assume success

        try:
            prob = self.pipeline.predict_proba([current_input])
            success_prob = prob[0][1]
            return float(success_prob)
        except Exception as e:
            print(f"[Model] Prediction error: {e}")
            return 1.0

# Singleton instance
success_predictor = JarvisLearningModel()
