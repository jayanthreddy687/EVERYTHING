"""
LLM Service for AI model interactions
"""
import os
import asyncio
import logging

# Suppress gRPC verbosity
os.environ['GRPC_VERBOSITY'] = 'ERROR'

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_CONFIG

logger = logging.getLogger(__name__)


class LLMService:
    """LLM service for making API calls to Gemini"""
    
    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        
        if self.gemini_key and GEMINI_AVAILABLE:
            self.provider = "gemini"
            self.api_key = self.gemini_key
            self.use_llm = True
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                generation_config=GEMINI_CONFIG
            )
            
            logger.info(f"✅ LLM Service initialized with Google Gemini")
            logger.info(f"   Model: {GEMINI_MODEL}")
            logger.info(f"   Provider: Google AI")
        elif self.gemini_key and not GEMINI_AVAILABLE:
            self.provider = "fallback"
            self.use_llm = False
            logger.warning("⚠️  Gemini API key found but google-generativeai not installed")
            logger.warning("   Install with: pip install google-generativeai")
        else:
            self.provider = "fallback"
            self.use_llm = False
            logger.warning("⚠️  LLM Service initialized in FALLBACK mode (no API key)")
            logger.warning("   Set GEMINI_API_KEY environment variable to use real LLM")
    
    async def analyze(self, prompt: str, max_tokens: int = 400) -> str:
        """Send prompt to LLM and get response"""
        
        if not self.use_llm:
            logger.info("🔄 Using FALLBACK response (no LLM API key)")
            return self._generate_fallback(prompt)
        
        logger.info(f"🤖 Calling Gemini API...")
        logger.debug(f"   Prompt (first 200 chars): {prompt[:200]}...")
        
        try:
            # Use Google Generative AI SDK (sync call wrapped in async)
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            llm_output = response.text
            logger.info("✅ Gemini Response received successfully")
            logger.debug(f"   LLM Output (first 300 chars): {llm_output[:300]}...")
            return llm_output
                
        except Exception as e:
            logger.error(f"❌ Gemini API Exception: {str(e)}")
            logger.info("🔄 Falling back to hardcoded response")
        
        return self._generate_fallback(prompt)
    
    def _generate_fallback(self, prompt: str) -> str:
        """Fallback when LLM unavailable"""
        logger.debug("   Generating fallback response based on prompt keywords")
        
        prompt_lower = prompt.lower()
        
        if "wellness" in prompt_lower:
            return "Poor sleep detected. Suggest enabling Do Not Disturb mode after 10 PM."
        elif "productivity" in prompt_lower:
            return "Code review scheduled. Recommend preparing PRs 30 minutes before."
        elif "social" in prompt_lower:
            return "Social event detected. Suggest muting work notifications."
        elif "emotional" in prompt_lower:
            return "Frustration detected in tweets. Recommend stress-relief activities."
        elif "financial" in prompt_lower:
            return "Recent tech purchases detected. Monitor for deals on similar items."
        
        return "Analyzed context. Recommendations available."
