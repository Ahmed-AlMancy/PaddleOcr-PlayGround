import os
import shutil
from typing import List

# Allowed categories for semantic expense classification
ALLOWED_CATEGORIES: List[str] = [
    "Food",
    "Groceries",
    "Dining",
    "Clothing",
    "Electronics",
    "Health",
    "Transportation",
    "Housing",
    "Utilities",
    "Entertainment",
    "Shopping",
    "Travel",
    "Education",
    "Personal Care",
    "Services",
    "Other",
]

# Standard category map for case-insensitive exact matching
CATEGORY_CASE_MAP = {cat.lower(): cat for cat in ALLOWED_CATEGORIES}

# Default Ollama executable path on Windows
DEFAULT_OLLAMA_PATH = r"C:\Users\AlMancy\AppData\Local\Programs\Ollama\ollama.exe"

def get_ollama_path() -> str:
    """Discover Ollama executable path via env var, PATH, or fallback location."""
    env_path = os.environ.get("OLLAMA_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    
    which_path = shutil.which("ollama")
    if which_path:
        return which_path

    if os.path.exists(DEFAULT_OLLAMA_PATH):
        return DEFAULT_OLLAMA_PATH

    # Return "ollama" command as fallback
    return "ollama"

def get_ollama_model() -> str:
    """Get configured Ollama model name."""
    return os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
