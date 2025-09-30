"""Data Loader - Loads user data from CSV and JSON files"""
import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Path to data directory (relative to project root)
# In Docker: /app/data, Locally: ../data from backend/
import os
if os.path.exists("/app/data"):
    DATA_DIR = Path("/app/data")
else:
    DATA_DIR = Path(__file__).parent.parent.parent / "data"


class DataLoaderService:
    """Service to load and parse user data from files"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        logger.info(f"📂 Data directory: {self.data_dir}")
        
    def load_user_profile(self) -> Dict[str, Any]:
        """Load user profile from JSON"""
        try:
            file_path = self.data_dir / "user_profile.json"
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.info("✅ Loaded user profile")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to load user profile: {e}")
            return {}
    
    def load_spotify_playlists(self) -> Dict[str, Any]:
        """Load Spotify playlists from JSON"""
        try:
            file_path = self.data_dir / "spotify_playlists.json"
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.info("✅ Loaded Spotify playlists")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to load Spotify playlists: {e}")
            return {"playlists": []}
    
    def load_social_media(self) -> Dict[str, Any]:
        """Load social media data from JSON"""
        try:
            file_path = self.data_dir / "social_media.json"
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.info("✅ Loaded social media data")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to load social media: {e}")
            return {}
    
    def load_calendar_events(self) -> List[Dict[str, Any]]:
        """Load calendar events from CSV"""
        try:
            file_path = self.data_dir / "calendar.csv"
            events = []
            
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    events.append({
                        "date": row["date"],
                        "time": row["time"],
                        "event": row["event"],
                        "duration": row["duration_hours"],
                        "location": row["location"]
                    })
            
            logger.info(f"✅ Loaded {len(events)} calendar events")
            return events
        except Exception as e:
            logger.error(f"❌ Failed to load calendar events: {e}")
            return []
    
    def load_location_history(self) -> List[Dict[str, Any]]:
        """Load location history from CSV"""
        try:
            file_path = self.data_dir / "location.csv"
            locations = []
            
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    locations.append({
                        "timestamp": row["timestamp"],
                        "latitude": float(row["latitude"]),
                        "longitude": float(row["longitude"]),
                        "location": row["location"]
                    })
            
            logger.info(f"✅ Loaded {len(locations)} location points")
            return locations
        except Exception as e:
            logger.error(f"❌ Failed to load location history: {e}")
            return []
    
    def get_current_location(self) -> Dict[str, Any]:
        """Get the most recent location from history"""
        locations = self.load_location_history()
        if locations:
            latest = locations[-1]
            return {
                "name": latest["location"],
                "latitude": latest["latitude"],
                "longitude": latest["longitude"]
            }
        return {
            "name": "Unknown",
            "latitude": 0.0,
            "longitude": 0.0
        }
    
    def get_complete_user_data(self) -> Dict[str, Any]:
        """Get all user data combined"""
        profile = self.load_user_profile()
        spotify = self.load_spotify_playlists()
        social_media = self.load_social_media()
        
        # Merge Spotify data into profile
        profile["spotify"] = spotify
        profile["social_media"] = social_media
        
        return profile
    
    def get_upcoming_calendar_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming calendar events"""
        all_events = self.load_calendar_events()
        
        # Sort by date and time
        sorted_events = sorted(all_events, key=lambda x: (x["date"], x["time"]))
        
        # Return upcoming events
        return sorted_events[:limit]


# Global instance
data_loader = DataLoaderService()
