import os
import logging
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_TITLE = "EVERYTHING AI Agent System"
API_VERSION = "3.0.0"
API_HOST = "0.0.0.0"
API_PORT = 8000

# CORS Settings
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("NEXT_PUBLIC_GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_TEMPERATURE = 1
GEMINI_TOP_P = 0.95
GEMINI_TOP_K = 40
GEMINI_MAX_TOKENS = 8192

GEMINI_CONFIG = {
    "temperature": GEMINI_TEMPERATURE,
    "top_p": GEMINI_TOP_P,
    "top_k": GEMINI_TOP_K,
    "max_output_tokens": GEMINI_MAX_TOKENS,
}

# Logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Agent Configuration
MAX_INSIGHTS_PER_REQUEST = 5
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

PRIORITY_MAP = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3
}

# Context Detection
USE_LLM_CONTEXT_DETECTION = os.getenv("USE_LLM_CONTEXT_DETECTION", "true").lower() == "true"

