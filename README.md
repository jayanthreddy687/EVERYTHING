# EVERYTHING AI Agent System

An AI assistant that actually understands what you're doing and gives you helpful suggestions at the right time. Built with 7 specialized agents, a memory system that learns from past events, and Google's Gemini AI.

## What does it do?

This is a context-aware AI system that analyzes your calendar, location, and habits to give you timely recommendations. For example:
- When you're about to commute, it suggests the best route and playlist
- During work hours, it helps you prepare for meetings
- In the evening, it recommends music for your social plans
- Before sleep, it helps you wind down

The system uses 7 different AI agents, each focused on a specific area like productivity, social life, wellness, or content recommendations. It also has a memory system (RAG) that remembers patterns from your past activities to make better suggestions.

## 📹 Demo Video

![EVERYTHING Demo](EVERYTHING%20DEMO.gif)

Watch the system in action with explaination: [View Demo Video Here](https://drive.google.com/file/d/13RpKVrKsZT4EiKb8lo-qYfFEL87EEEx9/view?usp=drive_link)

## Main Features

**7 AI Agents** - Each one handles a different aspect of your life:
- Context Analyzer - figures out what you're doing right now
- Productivity - helps you work smarter
- Social Intelligence - manages your social calendar
- Emotional Intelligence - picks up on your mood
- Financial - tracks spending and finds savings
- Wellness - improves sleep and fitness
- Content Curator - recommends music based on context

**Memory System** - Uses ChromaDB to remember your patterns and learn from feedback

**Scenario Detection** - Automatically knows if you're commuting, at work, working out, etc.

**Feedback Learning** - Gets better over time by learning what suggestions you like

**Modern UI** - Clean React interface that's easy to use

## How it works

```
Frontend (React + TypeScript)
    ↓
Backend API (FastAPI + Python)
    ↓
Agent Orchestrator
    ↓
7 Specialized AI Agents
    ↓
Google Gemini (for AI) + ChromaDB (for memory)
```

The system detects what you're doing based on time, location, and calendar. Then it activates only the relevant agents for that situation. Each agent analyzes your data and returns insights, which get sorted by priority.

## Tech Stack

**Backend:**
- FastAPI - web framework
- Python 3.13
- Google Gemini API - for the AI brain
- ChromaDB - vector database for memory
- Sentence Transformers - for semantic search
- Pydantic - data validation

**Frontend:**
- React 19
- TypeScript
- Vite - build tool
- Tailwind CSS - styling
- Framer Motion - animations
- Lucide Icons

**Infrastructure:**
- Docker & Docker Compose

## Getting Started

You'll need Docker installed. That's it.

### 1. Get a Gemini API Key (recommended)

Go to [Google AI Studio](https://aistudio.google.com/app/apikey), sign in, and create an API key. It's free.

The system works without it (using fallback responses), but you'll get much better results with real AI.

### 2. Create environment file

Create a file called `.env` in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Run the setup script

```bash
chmod +x run.sh
./run.sh
```

The script will:
- Check if Docker is installed
- Ask for your API key if you don't have a .env file
- Build everything
- Start the services
- Wait for them to be ready

### 4. Open your browser

- App: http://localhost:5173
- API docs: http://localhost:8000/docs

That's it. The system is now running.

## Manual Setup

If you prefer to run commands yourself:

```bash
# Create .env file
echo "GEMINI_API_KEY=your_key" > .env

# Build and start
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## Project Structure

```
backend/
  agents/          - 7 AI agents
  services/        - LLM, RAG, and data loading
  models/          - data schemas
  utils/           - helpers like context detection
  tests/           - unit and integration tests
  main.py          - FastAPI app
  orchestrator.py  - coordinates the agents
  config.py        - settings

frontend/
  src/
    components/    - UI components
    features/      - main views (now, agenda, profile)
    hooks/         - React hooks for state management
    services/      - API calls
    types/         - TypeScript types
    
data/
  user_profile.json      - user info
  calendar.csv           - events
  location.csv           - location history
  spotify_playlists.json - music data
  social_media.json      - posts and activity
```

## API Endpoints

**Main endpoints:**
- `GET /` - system info
- `POST /analyze` - get AI insights for current context
- `GET /scenarios` - list available scenarios
- `GET /agents` - list all agents

**Data endpoints:**
- `GET /user` - user profile
- `GET /calendar` - upcoming events
- `GET /location/current` - current location
- `GET /location/history` - location history

**RAG (memory) endpoints:**
- `GET /rag/stats` - see what's indexed
- `GET /rag/search` - search past events

**Feedback:**
- `POST /feedback` - record if insight was helpful
- `GET /feedback/stats` - feedback summary

Full API documentation is at http://localhost:8000/docs when running.

## The 8 Scenarios

The system detects these situations automatically:

1. **Commuting** - travel planning and music
2. **At Work** - productivity and focus
3. **Social Evening** - events with friends
4. **Shopping** - deals and purchases
5. **Lunch Time** - food and social
6. **Workout** - fitness and motivation
7. **Before Sleep** - wind down routine
8. **Weekend** - relaxation and activities

You can also manually pick a scenario in the UI if auto-detection gets it wrong.

**Note**: Manual scenario selection is included to demonstrate the system's capabilities by simulating different times and contexts. This lets you quickly see how the AI responds in various situations (commute, work, social, etc.) without waiting for those times or changing your actual location. Just select a scenario from the UI and the system will generate appropriate insights as if you were actually in that situation.

## How the Agents Work

**Context Analyzer** - Looks at your location, time, and calendar to figure out what's happening. Example: "You're at home with a 9:30 meeting. Leave now to catch the Northern Line."

**Productivity** - Analyzes your work calendar and suggests optimizations. Example: "Code review at 11am. Block 30 minutes before to prepare."

**Social Intelligence** - Tracks your social calendar and connections. Example: "Tom's quiz night tonight. Invite Sarah?"

**Emotional Intelligence** - Reads your social media mood. Example: "Stressed posts lately. Try your relaxation playlist?"

**Financial** - Finds spending patterns and savings. Example: "Lunch costs £12/day. Meal prep saves £240/month."

**Wellness** - Improves sleep and fitness. Example: "6h sleep, poor quality. Enable DND after 10pm."

**Content Curator** - Picks music for the moment. Example: "Commute playlist ready: Pink Floyd, Tame Impala..."

## Memory System (RAG)

The system uses ChromaDB to remember things:

**What it stores:**
- Past calendar events
- Location history
- Your feedback (what insights you liked or dismissed)

**How it helps:**
- Finds patterns like "You usually leave at 8:45 for 9:30 meetings"
- Suggests things similar to what worked before
- Gets better over time as it learns your preferences

**How it works:**
1. Text gets converted to embeddings (math vectors)
2. Similar events are found using vector search
3. Past context is added to the AI prompts
4. Better, more personalized suggestions come back

## Data Files

All your data is in the `data/` folder. Nothing is sent to external servers except the AI prompts to Gemini.

**user_profile.json** - Your info, contacts, app usage, purchases, fitness data

**calendar.csv** - Your events and meetings
```csv
date,time,event,duration_hours,location
2024-05-16,09:00,Morning standup,0.5,Office
```

**location.csv** - Where you've been
```csv
timestamp,latitude,longitude,location
2024-05-16T08:30:00,51.5074,-0.1278,Home
```

**spotify_playlists.json** - Your playlists and tracks

**social_media.json** - Posts and activity

You can edit these files to test different scenarios.

## Development

### Running backend locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key
uvicorn main:app --reload
```

### Running frontend locally (without Docker)

```bash
cd frontend
npm install
npm run dev
```

### Running tests

```bash
cd backend
pytest                    # all tests
pytest tests/unit/        # unit tests only
pytest --cov              # with coverage
```

## Configuration

**Backend** - Edit `backend/config.py`:
```python
GEMINI_MODEL = "gemini-2.5-flash-lite"
MAX_INSIGHTS_PER_REQUEST = 5
API_PORT = 8000
```

**Frontend** - Edit `frontend/src/constants/config.ts`:
```typescript
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000'
};
```

## Troubleshooting

**Backend won't start**
```bash
docker-compose logs backend
# Usually: wrong API key, port 8000 in use, or missing data files
```

**No AI responses (fallback mode)**
```bash
# Check if API key is set
docker-compose exec backend env | grep GEMINI
```

**Frontend can't connect**
```bash
# Make sure backend is running
curl http://localhost:8000/health
```

**Docker issues**
```bash
# Nuclear option - clear everything and start fresh
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

**Port conflicts**
```bash
# Check what's using the ports
lsof -i :8000  # backend
lsof -i :3000  # frontend
```

## Notes

- The system works offline (except for Gemini API calls)
- All data stays local
- You can run it without Docker if you prefer
- First build takes a few minutes, then it's fast
- ChromaDB data persists in a Docker volume

## Quick Reference

```bash
# Start everything
./run.sh

# Or manually
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Fresh start (deletes data)
docker-compose down -v

# Access
# Frontend: http://localhost:5173
# API: http://localhost:8000/docs
```