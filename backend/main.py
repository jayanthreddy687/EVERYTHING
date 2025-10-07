"""EVERYTHING AI Agent System - Main API Server"""
import logging
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import (
    API_TITLE,
    API_VERSION,
    API_HOST,
    API_PORT,
    CORS_ORIGINS,
    CORS_CREDENTIALS,
    CORS_METHODS,
    CORS_HEADERS,
    LOG_LEVEL,
    LOG_FORMAT
)
from models import (
    AnalysisRequest,
    VoiceOnboardingRequest,
    VoiceOnboardingResponse,
    OnboardingPreferences,
    OnboardingStatus
)
from orchestrator import AgentOrchestrator
from services import data_loader

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="""
AI Agent System that provides contextual insights based on user data.

Uses 7 specialized agents, RAG for memory, and Google Gemini for LLM.
Agents include context analysis, productivity, social, financial, wellness, emotional, and content curation.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Core", "description": "Main analysis endpoints"},
        {"name": "Data", "description": "User data, calendar, location"},
        {"name": "RAG", "description": "Vector store and search"},
        {"name": "Feedback", "description": "User feedback"},
        {"name": "System", "description": "Health and system info"}
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Onboarding data path
if os.path.exists("/app/data"):
    ONBOARDING_FILE = Path("/app/data/user_onboarding.json")
else:
    ONBOARDING_FILE = Path(__file__).parent.parent / "data" / "user_onboarding.json"

# Index data into RAG on startup
logger.info("📚 Indexing data into RAG vector store...")
try:
    # Load calendar and location data
    calendar_events = data_loader.load_calendar_events()
    location_history = data_loader.load_location_history()
    
    # Index into RAG
    orchestrator.rag.index_calendar_events(calendar_events)
    orchestrator.rag.index_location_history(location_history)
    
    # Get stats
    stats = orchestrator.rag.get_stats()
    logger.info(f"✅ RAG indexing complete:")
    logger.info(f"   • Calendar events: {stats['calendar_events']}")
    logger.info(f"   • Location points: {stats['locations']}")
except Exception as e:
    logger.error(f"❌ RAG indexing failed: {e}")
    logger.warning("   System will continue without RAG capabilities")

logger.info("=" * 70)
logger.info(f"🤖 {API_TITLE} v{API_VERSION}")
logger.info("=" * 70)
logger.info(f"✅ {len(orchestrator.agents)} autonomous agents loaded:")
for agent in orchestrator.agents:
    logger.info(f"   • {agent.name}")
logger.info("")
logger.info(f"🧠 LLM Status: {'✅ ENABLED' if orchestrator.llm.use_llm else '⚠️  FALLBACK MODE'}")
if not orchestrator.llm.use_llm:
    logger.warning("   Set GEMINI_API_KEY to enable real LLM intelligence")
logger.info("=" * 70)
logger.info("")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["System"])
def root():
    """Get system info - version, agents, and RAG stats"""
    rag_stats = orchestrator.rag.get_stats()
    return {
        "service": API_TITLE,
        "version": API_VERSION,
        "agents": [agent.name for agent in orchestrator.agents],
        "architecture": "AI Agents + RAG (Contextual Memory)",
        "rag_enabled": True,
        "rag_indexed_items": rag_stats
    }


@app.post("/analyze", tags=["Core"], response_model=None)
async def analyze(request: AnalysisRequest):
    """
    Main analysis endpoint. Send user data and context, get AI insights back.
    Activates relevant agents based on scenario and returns top insights.
    """
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("📥 NEW REQUEST: /analyze")
    logger.info("=" * 70)
    logger.info(f"   User: {request.user_data.get('name', 'Unknown')}")
    logger.info(f"   Context Type: {request.current_context.get('context_type', 'Unknown')}")
    logger.info(f"   Location: {request.current_context.get('location', {}).get('name', 'Unknown')}")
    logger.info("")
    
    try:
        result = await orchestrator.orchestrate(request)
        
        logger.info("✅ REQUEST COMPLETED SUCCESSFULLY")
        logger.info(f"   Insights returned: {len(result['insights'])}")
        logger.info("=" * 70)
        logger.info("")
        
        return result
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ REQUEST FAILED: {str(e)}")
        logger.error("=" * 70)
        logger.error("")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents", tags=["Core"])
def list_agents():
    """List all available AI agents"""
    return {
        "agents": [
            {
                "name": agent.name,
                "description": agent.__class__.__doc__
            }
            for agent in orchestrator.agents
        ]
    }


@app.get("/health", tags=["System"])
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm_available": orchestrator.llm.use_llm,
        "agents_count": len(orchestrator.agents)
    }


@app.get("/scenarios", tags=["Core"])
def list_scenarios():
    """Get available scenarios with their triggers"""
    scenarios = [
        {
            "id": "commuting_to_work",
            "name": "Commute",
            "description": "Travel, music, and work prep",
            "icon": "🚇",
            "triggers": ["context", "content", "productivity"]
        },
        {
            "id": "at_work",
            "name": "Office",
            "description": "Focus and productivity",
            "icon": "💼",
            "triggers": ["productivity", "content"]
        },
        {
            "id": "social_evening",
            "name": "Social",
            "description": "Events and connections",
            "icon": "🍻",
            "triggers": ["social", "context", "emotional"]
        },
        {
            "id": "shopping",
            "name": "Shopping",
            "description": "Purchases and deals",
            "icon": "🛍️",
            "triggers": ["financial", "context"]
        },
        {
            "id": "lunch_time",
            "name": "Lunch",
            "description": "Food and social time",
            "icon": "🍽️",
            "triggers": ["financial", "social"]
        },
        {
            "id": "workout_time",
            "name": "Workout",
            "description": "Fitness and motivation",
            "icon": "🏃",
            "triggers": ["wellness", "social", "content"]
        },
        {
            "id": "before_sleep",
            "name": "Sleep",
            "description": "Wind down and rest",
            "icon": "🌙",
            "triggers": ["wellness", "content"]
        },
        {
            "id": "weekend",
            "name": "Weekend",
            "description": "Relax and explore",
            "icon": "🎉",
            "triggers": ["social", "wellness", "content"]
        }
    ]
    return {"scenarios": scenarios}


@app.get("/user", tags=["Data"])
def get_user_profile():
    """Get user profile data"""
    return data_loader.get_complete_user_data()


@app.get("/calendar", tags=["Data"])
def get_calendar_events():
    """Get upcoming calendar events (next 20)"""
    events = data_loader.get_upcoming_calendar_events(limit=20)
    return {"events": events}


@app.get("/location/current", tags=["Data"])
def get_current_location():
    """Get current location"""
    return data_loader.get_current_location()


@app.get("/location/history", tags=["Data"])
def get_location_history():
    """Get location history"""
    locations = data_loader.load_location_history()
    return {"locations": locations}


@app.get("/rag/stats", tags=["RAG"])
def get_rag_stats():
    """Get RAG vector store statistics"""
    stats = orchestrator.rag.get_stats()
    return {
        "status": "active",
        "indexed_items": stats,
        "embedding_model": "all-MiniLM-L6-v2"
    }


@app.get("/rag/search", tags=["RAG"])
def search_rag(query: str, collection: str = "calendar_events", top_k: int = 3):
    """
    Search through calendar or location data using natural language.
    collection: 'calendar_events' or 'location_history'
    """
    try:
        if collection == "calendar_events":
            results = orchestrator.rag.retrieve_similar_events(query, top_k)
        elif collection == "location_history":
            results = orchestrator.rag.retrieve_similar_locations(query, top_k)
        else:
            return {"error": "Invalid collection. Use 'calendar_events' or 'location_history'"}
        
        return {
            "query": query,
            "collection": collection,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/feedback", tags=["Feedback"])
async def record_insight_feedback(feedback: Dict[str, Any]):
    """
    Record feedback on an insight.
    action can be: 'clicked', 'dismissed', or 'ignored'
    """
    try:
        insight_data = feedback.get("insight", {})
        user_action = feedback.get("action", "ignored")
        
        # Validate action
        if user_action not in ["clicked", "dismissed", "ignored"]:
            raise HTTPException(status_code=400, detail="Invalid action. Use: clicked, dismissed, or ignored")
        
        # Record feedback
        orchestrator.rag.record_feedback(insight_data, user_action)
        
        # Get updated feedback score for this type of insight
        category = insight_data.get("category", "")
        agent_name = insight_data.get("agent_name", "")
        avg_score = orchestrator.rag.get_feedback_score(category, agent_name)
        
        logger.info(f"📊 Feedback recorded: {user_action} on {category} insight")
        logger.info(f"   Average score for {agent_name}/{category}: {avg_score:.2f}")
        
        return {
            "status": "recorded",
            "action": user_action,
            "category": category,
            "average_score": avg_score
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is (e.g., 400 Bad Request)
        raise
    except Exception as e:
        logger.error(f"❌ Failed to record feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/stats", tags=["Feedback"])
def get_feedback_stats():
    """Get feedback statistics"""
    try:
        stats = orchestrator.rag.get_stats()
        
        # Calculate feedback summary
        feedback_summary = {
            "total_feedback": stats.get("feedback_items", 0),
            "insights_per_category": {}
        }
        
        return {
            "status": "active",
            "feedback_count": stats.get("feedback_items", 0),
            "message": "Feedback tracking active. System learns from user interactions."
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# ONBOARDING ENDPOINTS
# ============================================================================

@app.get("/onboarding/status", tags=["Onboarding"])
def get_onboarding_status():
    """Check if user has completed onboarding"""
    try:
        if ONBOARDING_FILE.exists():
            with open(ONBOARDING_FILE, 'r') as f:
                data = json.load(f)
            return OnboardingStatus(completed=True, preferences=OnboardingPreferences(**data))
        else:
            return OnboardingStatus(completed=False, preferences=None)
    except Exception as e:
        logger.error(f"❌ Failed to check onboarding status: {e}")
        return OnboardingStatus(completed=False, preferences=None)


@app.post("/onboarding/voice-step", tags=["Onboarding"])
async def voice_onboarding_step(request: VoiceOnboardingRequest):
    """
    Process one step of voice onboarding conversation.
    Uses Gemini to intelligently ask follow-up questions and extract preferences.
    """
    logger.info("🎙️ Voice onboarding step received")
    logger.info(f"   Conversation history: {len(request.conversation_history)} messages")
    logger.info(f"   User answer: {request.current_answer[:100]}...")
    
    try:
        # Count user responses (not system messages)
        user_responses = [msg for msg in request.conversation_history if msg.role == "user"]
        num_user_responses = len(user_responses)
        
        logger.info(f"   User has responded {num_user_responses} times")
        
        # Force completion after 4 user responses (max 5 questions including this one)
        force_complete = num_user_responses >= 5
        
        # Build conversation context for Gemini
        conversation_text = "\n".join([
            f"{msg.role.upper()}: {msg.text}" 
            for msg in request.conversation_history
        ])
        
        # Intelligent prompt for Gemini
        completion_directive = ""
        if force_complete:
            completion_directive = "\n\n⚠️ IMPORTANT: This is the final question. You MUST output ONBOARDING_COMPLETE now. The user has already provided enough information."
        elif num_user_responses >= 2:
            completion_directive = "\n\n⚠️ You've asked several questions already. If the user has mentioned their main priorities, complete the onboarding by outputting ONBOARDING_COMPLETE."
        
        prompt = f"""You are an onboarding assistant for EVERYTHING AI - a personal AI system with 7 specialized agents.

Your goal: Learn about the user's priorities and preferences through a BRIEF conversation (3-4 questions maximum).

Conversation so far ({num_user_responses} user responses):
{conversation_text}

User just said: "{request.current_answer}"
{completion_directive}

CRITICAL RULES:
1. If user has mentioned their main priority area (work, health, social, finance), ask ONE follow-up question, then COMPLETE
2. After 3 user responses, you MUST complete onboarding
3. Don't repeat questions or ask about areas they haven't mentioned
4. Don't ask "what matters to you" again if they already answered

ANALYZE their answer:
- What priorities did they mention? (work/productivity, health/wellness, social, finances)
- What specific issues? (e.g., work: meetings, stress; health: sleep, exercise)
- Is this enough to personalize their experience? (YES after 2-3 responses)

Format your response EXACTLY like this:

ANALYSIS: [What you learned - be specific about priorities identified]
PREFERENCES: {{"priorities": ["work", "wellness", etc], "work_stress": ["meetings", "focus"], "health_goals": ["sleep", "exercise"], "social_style": "balanced", "financial_interest": "low"}}
NEXT_QUESTION: ONBOARDING_COMPLETE OR [ONE specific follow-up question about what they just mentioned]
REASONING: [Why completing OR why this ONE follow-up is needed]"""

        # Get Gemini's response
        response = await orchestrator.llm.analyze(prompt)
        
        logger.debug(f"   Gemini response: {response[:200]}...")
        
        # Parse response
        analysis = ""
        preferences = {}
        next_question = ""
        is_complete = False
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith("ANALYSIS:"):
                analysis = line.replace("ANALYSIS:", "").strip()
            elif line.startswith("PREFERENCES:"):
                pref_str = line.replace("PREFERENCES:", "").strip()
                try:
                    preferences = json.loads(pref_str)
                except:
                    preferences = {}
            elif line.startswith("NEXT_QUESTION:"):
                next_question = line.replace("NEXT_QUESTION:", "").strip()
                if "ONBOARDING_COMPLETE" in next_question:
                    is_complete = True
                    next_question = "ONBOARDING_COMPLETE"
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
                logger.info(f"   Reasoning: {reasoning}")
        
        # If no next question was parsed, generate a default
        if not next_question:
            next_question = "Tell me more about what you'd like help with."
        
        # HARD LIMIT: Force completion after 4 user responses
        if force_complete and not is_complete:
            logger.info("   ⚠️ FORCING COMPLETION - Maximum questions reached")
            is_complete = True
            next_question = "ONBOARDING_COMPLETE"
            if not analysis:
                analysis = "User has provided sufficient information about their priorities"
        
        logger.info(f"   Analysis: {analysis}")
        logger.info(f"   Preferences extracted: {preferences}")
        logger.info(f"   Next question: {next_question}")
        logger.info(f"   Complete: {is_complete}")
        
        return VoiceOnboardingResponse(
            next_question=next_question,
            analysis=analysis,
            preferences_extracted=preferences,
            is_complete=is_complete
        )
    
    except Exception as e:
        logger.error(f"❌ Voice onboarding step failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/onboarding/save", tags=["Onboarding"])
async def save_onboarding(preferences: OnboardingPreferences):
    """
    Save user onboarding preferences and calculate agent weights.
    """
    logger.info("💾 Saving onboarding preferences...")
    
    try:
        # Calculate agent weights based on priorities
        agent_weights = {
            "context": 1.0,  # Always active
            "emotional": 1.0  # Always active
        }
        
        # Weight agents based on user priorities
        for priority in preferences.priorities:
            priority_lower = priority.lower()
            
            if any(w in priority_lower for w in ['work', 'productivity', 'focus', 'meeting']):
                agent_weights["productivity"] = agent_weights.get("productivity", 1.0) + 0.5
            
            if any(w in priority_lower for w in ['health', 'wellness', 'sleep', 'fitness', 'exercise']):
                agent_weights["wellness"] = agent_weights.get("wellness", 1.0) + 0.5
            
            if any(w in priority_lower for w in ['social', 'friends', 'connection', 'people']):
                agent_weights["social"] = agent_weights.get("social", 1.0) + 0.5
            
            if any(w in priority_lower for w in ['money', 'financial', 'saving', 'budget', 'spending']):
                agent_weights["financial"] = agent_weights.get("financial", 1.0) + 0.5
        
        # Add weights for music/content if mentioned
        if preferences.health_goals or preferences.work_stress_areas:
            agent_weights["content"] = agent_weights.get("content", 1.0) + 0.3
        
        preferences.agent_weights = agent_weights
        
        # Save to file
        ONBOARDING_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ONBOARDING_FILE, 'w') as f:
            json.dump(preferences.dict(), f, indent=2)
        
        logger.info("✅ Onboarding preferences saved")
        logger.info(f"   Priorities: {preferences.priorities}")
        logger.info(f"   Agent weights: {agent_weights}")
        
        return {
            "status": "saved",
            "preferences": preferences,
            "message": "Your preferences have been saved. EVERYTHING is now personalized for you!"
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to save onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/onboarding/reset", tags=["Onboarding"])
def reset_onboarding():
    """Reset onboarding (for testing)"""
    try:
        if ONBOARDING_FILE.exists():
            os.remove(ONBOARDING_FILE)
        return {"status": "reset", "message": "Onboarding has been reset"}
    except Exception as e:
        logger.error(f"❌ Failed to reset onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
