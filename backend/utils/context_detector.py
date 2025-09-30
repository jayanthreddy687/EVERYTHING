"""
Context Detector - Detects current user situation/scenario
EXACT copy from original backend/main.py lines 1057-1334
"""
import logging
from typing import Dict, Any
from datetime import datetime
from models import AnalysisRequest

logger = logging.getLogger(__name__)


class ContextDetector:
    """Detects current user situation/scenario"""
    
    @staticmethod
    def get_scenario_config(scenario_type: str) -> Dict[str, Any]:
        """Get predefined scenario configuration by type"""
        
        scenarios = {
            "commuting_to_work": {
                "type": "commuting_to_work",
                "description": "Commuting to work - travel, music, and preparation",
                "confidence": 1.0,
                "triggers": ["context", "content", "productivity"],
                "context_data": {}
            },
            "at_work": {
                "type": "at_work",
                "description": "At work - focus and productivity mode",
                "confidence": 1.0,
                "triggers": ["productivity", "content"],
                "context_data": {}
            },
            "before_sleep": {
                "type": "before_sleep",
                "description": "Winding down - sleep optimization time",
                "confidence": 1.0,
                "triggers": ["wellness", "content"],
                "context_data": {}
            },
            "lunch_time": {
                "type": "lunch_time",
                "description": "Lunch break - food and social time",
                "confidence": 1.0,
                "triggers": ["financial", "social"],
                "context_data": {}
            },
            "social_evening": {
                "type": "social_evening",
                "description": "Social time - events and connections",
                "confidence": 1.0,
                "triggers": ["social", "context", "emotional"],
                "context_data": {}
            },
            "weekend": {
                "type": "weekend",
                "description": "Weekend mode - relaxation and activities",
                "confidence": 1.0,
                "triggers": ["social", "wellness", "content"],
                "context_data": {}
            },
            "workout_time": {
                "type": "workout_time",
                "description": "Workout mode - fitness and motivation",
                "confidence": 1.0,
                "triggers": ["wellness", "social", "content"],
                "context_data": {}
            },
            "shopping": {
                "type": "shopping",
                "description": "Shopping mode - purchases and deals",
                "confidence": 1.0,
                "triggers": ["financial", "context"],
                "context_data": {}
            },
            "general": {
                "type": "general",
                "description": "General context - adaptive mode",
                "confidence": 0.5,
                "triggers": ["context", "emotional"],
                "context_data": {}
            }
        }
        
        return scenarios.get(scenario_type, scenarios["general"])
    
    @staticmethod
    def detect_scenario(request: AnalysisRequest) -> Dict[str, Any]:
        """Analyze user context and determine the current scenario"""
        
        # Check for manual scenario override first
        if request.manual_scenario:
            logger.info(f"📱 MANUAL SCENARIO SELECTED: {request.manual_scenario}")
            scenario = ContextDetector.get_scenario_config(request.manual_scenario)
            scenario["manual"] = True
            logger.info(f"   Description: {scenario['description']}")
            logger.info(f"   Agents to trigger: {', '.join(scenario['triggers'])}")
            logger.info("")
            return scenario
        
        current_loc = request.current_context.get("location", {})
        current_time = request.current_context.get("time", "")
        user_data = request.user_data
        calendar = request.calendar_events
        location_history = request.location_data
        
        # Parse current time
        try:
            time_obj = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
            hour = time_obj.hour
            day_of_week = time_obj.weekday()  # 0=Monday, 6=Sunday
        except:
            hour = 9
            day_of_week = 1
        
        # Get home/work coordinates
        home_coords = user_data.get("location", {}).get("home", {}).get("coordinates", {})
        work_coords = user_data.get("location", {}).get("work", {}).get("coordinates", {})
        
        current_lat = current_loc.get("latitude", 0)
        current_lon = current_loc.get("longitude", 0)
        
        # Helper: Calculate distance (simple euclidean for demo)
        def distance(lat1, lon1, lat2, lon2):
            return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
        
        at_home = distance(current_lat, current_lon, 
                          home_coords.get("latitude", 0), 
                          home_coords.get("longitude", 0)) < 0.01
        
        at_work = distance(current_lat, current_lon,
                          work_coords.get("latitude", 0),
                          work_coords.get("longitude", 0)) < 0.01
        
        # Check next calendar event
        next_event = calendar[0] if calendar else None
        next_event_title = next_event.get("event", "").lower() if next_event else ""
        next_event_location = next_event.get("location", "").lower() if next_event else ""
        
        # SCENARIO DETECTION LOGIC
        scenario = {
            "type": "general",
            "description": "General context",
            "confidence": 0.5,
            "triggers": ["context", "emotional"],
            "context_data": {}
        }
        
        # 0. SHOPPING MODE (farmers market, shopping events)
        if next_event and any(w in next_event_title for w in ['market', 'shopping', 'store', 'mall']):
            scenario = {
                "type": "shopping",
                "description": "Shopping trip - deals and purchases",
                "confidence": 0.85,
                "triggers": ["financial", "context"],
                "context_data": {
                    "shopping_event": next_event,
                    "recent_purchases": user_data.get("purchases", [])
                }
            }
        
        # 1. COMMUTING TO WORK (morning, at home, work event soon)
        elif (7 <= hour <= 10 and at_home and 
            any(w in next_event_title for w in ['standup', 'meeting', 'work', 'office', 'review', 'demo'])):
            scenario = {
                "type": "commuting_to_work",
                "description": "User is at home with work event coming up - likely commuting soon",
                "confidence": 0.9,
                "triggers": ["context", "content", "productivity"],
                "context_data": {
                    "origin": home_coords,
                    "destination": work_coords,
                    "next_event": next_event,
                    "commute_playlists": user_data.get("spotify", {}).get("playlists", [])
                }
            }
        
        # 2. AT WORK - PRODUCTIVITY MODE
        elif (at_work or 'office' in current_loc.get("name", "").lower() or 
              'office' in next_event_location) and 9 <= hour <= 18:
            # Check if it's deep work time
            is_deep_work = next_event and any(w in next_event_title for w in ['deep work', 'feature', 'dev', 'coding'])
            
            scenario = {
                "type": "at_work",
                "description": "At work - focus and productivity mode" if is_deep_work else "At work - meetings and collaboration",
                "confidence": 0.95,
                "triggers": ["productivity", "content"],
                "context_data": {
                    "work_events": [e for e in calendar if any(w in e.get('event', '').lower() 
                                   for w in ['meeting', 'review', 'standup', 'demo', 'planning'])],
                    "focus_playlists": [p for p in user_data.get("spotify", {}).get("playlists", []) 
                                       if 'focus' in p.get('name', '').lower()],
                    "is_deep_work": is_deep_work
                }
            }
        
        # 3. BEFORE SLEEP
        elif hour >= 22 or hour <= 1:
            sleep_data = user_data.get("fitness_data", {}).get("sleep", {})
            scenario = {
                "type": "before_sleep",
                "description": "Late night - sleep optimization time",
                "confidence": 0.9,
                "triggers": ["wellness", "content"],
                "context_data": {
                    "sleep_quality": sleep_data.get("quality", "unknown"),
                    "screen_time": user_data.get("app_usage", {}).get("screen_time", ""),
                    "late_night_playlists": [p for p in user_data.get("spotify", {}).get("playlists", []) 
                                            if 'night' in p.get('name', '').lower() or 'sleep' in p.get('name', '').lower()]
                }
            }
        
        # 4. LUNCH TIME
        elif (12 <= hour <= 14 or 
              (next_event and any(w in next_event_title for w in ['lunch', 'sandwich', 'food', 'grab']))):
            scenario = {
                "type": "lunch_time",
                "description": "Lunch hour - food and cost optimization",
                "confidence": 0.85,
                "triggers": ["financial", "social"],
                "context_data": {
                    "lunch_events": [e for e in calendar if any(w in e.get('event', '').lower() 
                                    for w in ['lunch', 'sandwich', 'food'])],
                    "recent_food_purchases": [p for p in user_data.get("purchases", []) 
                                             if any(f in p.get('item', '').lower() 
                                                   for f in ['sandwich', 'coffee', 'lunch', 'food'])],
                    "contacts": user_data.get("contacts", [])
                }
            }
        
        # 5. EVENING SOCIAL TIME
        elif ((18 <= hour <= 23 and day_of_week <= 4) or  # Weekday evening
              (next_event and any(w in next_event_title for w in ['drinks', 'pub', 'quiz', 'dinner', 'mates']))):
            social_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                           for w in ['drinks', 'pub', 'dinner', 'meet', 'quiz', 'mates'])]
            if social_events or (next_event and any(w in next_event_title for w in ['drinks', 'pub', 'quiz'])):
                scenario = {
                    "type": "social_evening",
                    "description": "Social time - events and connections",
                    "confidence": 0.9,
                    "triggers": ["social", "context", "emotional"],
                    "context_data": {
                        "social_events": social_events,
                        "contacts": user_data.get("contacts", []),
                        "current_location": current_loc,
                        "next_event": next_event
                    }
                }
        
        # 6. WEEKEND MODE
        elif day_of_week >= 5:  # Saturday or Sunday
            scenario = {
                "type": "weekend",
                "description": "Weekend - relaxation and social activities",
                "confidence": 0.8,
                "triggers": ["social", "wellness", "content"],
                "context_data": {
                    "weekend_events": calendar,
                    "fitness_data": user_data.get("fitness_data", {})
                }
            }
        
        # 7. WORKOUT TIME
        fitness = user_data.get("fitness_data", {})
        last_workout = fitness.get("last_workout", {})
        is_workout_event = next_event and any(w in next_event_title for w in ['workout', 'run', 'gym', 'exercise', 'morning run'])
        
        if is_workout_event or (6 <= hour <= 8 and any(w in next_event_title for w in ['run'])):
            scenario = {
                "type": "workout_time",
                "description": "Workout scheduled or in progress",
                "confidence": 0.85,
                "triggers": ["wellness", "social", "content"],
                "context_data": {
                    "workout_data": last_workout,
                    "next_event": next_event,
                    "fitness_contacts": [c for c in user_data.get("contacts", []) 
                                        if 'runner' in c.get('email', '').lower()]
                }
            }
        
        logger.info(f"🎯 SCENARIO DETECTED: {scenario['type']}")
        logger.info(f"   Description: {scenario['description']}")
        logger.info(f"   Confidence: {scenario['confidence']}")
        logger.info(f"   Agents to trigger: {', '.join(scenario['triggers'])}")
        logger.info("")
        
        return scenario