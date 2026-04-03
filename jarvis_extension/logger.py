import uuid
import threading
import queue
import time
import logging
from datetime import datetime
from jarvis_extension.db import db_store

# --- LOGGING QUEUE ---
log_queue = queue.Queue(maxsize=1000)

class EventLogger:
    """
    Asynchronous, non-blocking Event-Based Logging for Jarvis.
    """
    def __init__(self):
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        print("[Logger] Worker initialized.")

    def log(self, event_type, session_id, **data):
        """Send log to background queue."""
        log_entry = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(), # ISO by default in Mongo
            "session_id": session_id,
            "event_type": event_type,
            "data": data
        }
        
        try:
            log_queue.put(log_entry, block=False)
        except queue.Full:
            print("[Logger] Warning: Queue full! Log dropped.")

    def _process_queue(self):
        """Background thread for DB writes."""
        while True:
            try:
                log_entry = log_queue.get()
                if log_entry is None: break
                
                # Write to DB via db_store instance
                db_store.insert_log(log_entry)
                
                log_queue.task_done()
                time.sleep(0.01) # Small throttle
            except Exception as e:
                print(f"[Logger] Background Error: {e}")

    # Helper methods for specific event types
    def user_input(self, session_id, text):
        self.log("USER_INPUT", session_id, text=text)

    def intent(self, session_id, intent_name, **params):
        self.log("INTENT", session_id, intent=intent_name, parameters=params)

    def api_call(self, session_id, service_name, **params):
        self.log("API_CALL", session_id, service=service_name, parameters=params)

    def error(self, session_id, error_msg, **extra_data):
        self.log("ERROR", session_id, message=error_msg, **extra_data)

    def decision(self, session_id, reasoning, **options):
        self.log("DECISION", session_id, reason=reasoning, **options)

    def output(self, session_id, text):
        self.log("OUTPUT", session_id, response=text)

# Singleton instance
jarvis_logger = EventLogger()
