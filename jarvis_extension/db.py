import os
import json
import time
import threading
import logging
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# --- CONFIGURATION ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "jarvis_logs"
COLLECTION_NAME = "events"
FALLBACK_LOG_FILE = "jarvis_extension/fallback_logs.json"

class MongoStore:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.is_connected = False
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            self.client.admin.command('ping') # Test connection
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Setup Indexes
            self.collection.create_index([("timestamp", ASCENDING)])
            self.collection.create_index([("session_id", ASCENDING)])
            self.collection.create_index([("event_type", ASCENDING)])
            
            self.is_connected = True
            print(f"[DB] Connected to MongoDB: {DATABASE_NAME}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.is_connected = False
            print(f"[DB] MongoDB Offline! Using fallback file. Error: {e}")

    def insert_log(self, log_entry):
        if self.is_connected:
            try:
                self.collection.insert_one(log_entry)
            except Exception as e:
                print(f"[DB] Insertion error: {e}")
                self._fallback_write(log_entry)
        else:
            self._fallback_write(log_entry)

    def _fallback_write(self, log_entry):
        """Append log to local JSON file if DB is down."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(FALLBACK_LOG_FILE), exist_ok=True)
            with open(FALLBACK_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, default=str) + "\n")
        except Exception as e:
            print(f"[DB] Fallback write failed: {e}")

    def _read_fallback(self, query=None, limit=1000):
        """Read logs from the local fallback file."""
        logs = []
        if not os.path.exists(FALLBACK_LOG_FILE):
            return []
            
        try:
            with open(FALLBACK_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        # Simple query filter (session_id)
                        if query and "session_id" in query:
                            if log.get("session_id") != query["session_id"]:
                                continue
                        logs.append(log)
                    except: continue
        except Exception as e:
            print(f"[DB] Error reading fallback: {e}")
            
        # Return newest first
        return sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]

    def get_logs(self, query=None, limit=1000):
        if not self.is_connected:
            self._connect() 
            
        if self.is_connected:
            try:
                return list(self.collection.find(query or {}).sort("timestamp", -1).limit(limit))
            except Exception:
                return self._read_fallback(query, limit)
        else:
            return self._read_fallback(query, limit)

# Singleton instance
db_store = MongoStore()
