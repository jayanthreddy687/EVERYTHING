"""
EVERYTHING AI Agent System - Main API Server
Production-ready FastAPI application with modular architecture
"""
import logging
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
from models import AnalysisRequest
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
