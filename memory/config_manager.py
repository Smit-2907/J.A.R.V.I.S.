import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR  = get_base_dir()
ENV_FILE  = BASE_DIR / ".env"


def config_exists() -> bool:
    key = os.getenv("GEMINI_API_KEY", "")
    return bool(key and len(key) > 15 and "[" not in key)


def save_api_keys(gemini_api_key: str) -> None:
    set_key(str(ENV_FILE), "GEMINI_API_KEY", gemini_api_key.strip())
    load_dotenv(str(ENV_FILE), override=True)


def get_gemini_key() -> str | None:
    return os.getenv("GEMINI_API_KEY")


def is_configured() -> bool:
    return config_exists()