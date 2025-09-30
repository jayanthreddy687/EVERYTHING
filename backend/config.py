"""
Configuration settings for the EVERYTHING AI Agent System
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
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
GEMINI_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# Logging Configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Agent Configuration
MAX_INSIGHTS_PER_REQUEST = 5
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

# Priority mapping
PRIORITY_MAP = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3
}
