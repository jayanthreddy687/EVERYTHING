"""
RAG Service - Vector search for contextual memory
Uses ChromaDB to retrieve relevant historical context
"""
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class RAGService:
    """Handles vector storage and semantic search for user context"""
    
    def __init__(self, use_persistent=True):
        # Initialize ChromaDB client - persistent for production, in-memory for tests
        if use_persistent:
            self.client = chromadb.PersistentClient(path="./chroma_db")
        else:
            self.client = chromadb.Client()  # In-memory for testing
        
        # Use sentence transformers for embeddings - lightweight and fast
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create collections for different data types
        self.calendar_collection = self.client.get_or_create_collection(
            name="calendar_events",
            embedding_function=self.embedding_fn,
            metadata={"description": "Historical calendar events"}
        )
        
        self.location_collection = self.client.get_or_create_collection(
            name="location_history",
            embedding_function=self.embedding_fn,
            metadata={"description": "Location visit history"}
        )
        
        # New: Collection for tracking user feedback on insights
        self.feedback_collection = self.client.get_or_create_collection(
            name="insight_feedback",
            embedding_function=self.embedding_fn,
            metadata={"description": "User feedback on generated insights"}
        )
        
        # In-memory feedback scores for quick lookup
        self.feedback_scores = {}  # {query_pattern: score}
        
        logger.info("✅ RAG Service initialized with ChromaDB")
        logger.info(f"   Embedding model: all-MiniLM-L6-v2")
        logger.info(f"   Collections: calendar_events, location_history, insight_feedback")
    
    def index_calendar_events(self, events: List[Dict[str, Any]]):
        """Index calendar events for semantic search"""
        if not events:
            logger.warning("⚠️  No calendar events to index")
            return
        
        try:
            # Create searchable text from events
            documents = []
            ids = []
            metadatas = []
            
            for i, event in enumerate(events):
                # Build semantic text - what would someone search for?
                doc_text = f"{event.get('date', '')} {event.get('time', '')}: {event.get('event', '')} at {event.get('location', '')}"
                documents.append(doc_text)
                ids.append(f"cal_event_{i}")
                
                # Store the full event as metadata for retrieval
                metadatas.append({
                    "date": event.get("date", ""),
                    "time": event.get("time", ""),
                    "event": event.get("event", ""),
                    "location": event.get("location", ""),
                    "duration": event.get("duration", "")
                })
            
            # Add to collection
            self.calendar_collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            
            logger.info(f"✅ Indexed {len(events)} calendar events into vector store")
        
        except Exception as e:
            logger.error(f"❌ Failed to index calendar events: {e}")
    
    def index_location_history(self, locations: List[Dict[str, Any]]):
        """Index location history for pattern detection"""
        if not locations:
            logger.warning("⚠️  No location history to index")
            return
        
        try:
            documents = []
            ids = []
            metadatas = []
            
            for i, loc in enumerate(locations):
                # Make it semantic - what patterns do we want to find?
                doc_text = f"{loc.get('timestamp', '')}: Visited {loc.get('location', '')}"
                documents.append(doc_text)
                ids.append(f"location_{i}")
                metadatas.append({
                    "timestamp": loc.get("timestamp", ""),
                    "location": loc.get("location", ""),
                    "latitude": loc.get("latitude", 0.0),
                    "longitude": loc.get("longitude", 0.0)
                })
            
            self.location_collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            
            logger.info(f"✅ Indexed {len(locations)} location points into vector store")
        
        except Exception as e:
            logger.error(f"❌ Failed to index location history: {e}")
    
    def retrieve_similar_events(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Find similar calendar events based on semantic search
        
        Example query: "meeting at office" or "commuting to work"
        """
        try:
            results = self.calendar_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Return the metadata (full event details)
            if results and results['metadatas'] and len(results['metadatas']) > 0:
                similar_events = results['metadatas'][0]
                logger.info(f"🔍 Found {len(similar_events)} similar events for query: '{query}'")
                return similar_events
            
            return []
        
        except Exception as e:
            logger.error(f"❌ RAG retrieval failed: {e}")
            return []
    
    def retrieve_similar_locations(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find similar location patterns"""
        try:
            results = self.location_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            if results and results['metadatas'] and len(results['metadatas']) > 0:
                similar_locs = results['metadatas'][0]
                logger.info(f"🔍 Found {len(similar_locs)} similar locations for query: '{query}'")
                return similar_locs
            
            return []
        
        except Exception as e:
            logger.error(f"❌ Location retrieval failed: {e}")
            return []
    
    def record_feedback(self, insight_data: Dict[str, Any], user_action: str):
        """
        Record user feedback on an insight
        
        Args:
            insight_data: The insight that was shown to user
            user_action: 'clicked', 'dismissed', or 'ignored'
        """
        try:
            import time
            from datetime import datetime
            
            # Create searchable text from insight
            doc_text = f"{insight_data.get('category', '')}: {insight_data.get('title', '')} - {insight_data.get('message', '')}"
            
            # Assign feedback score
            score = {
                'clicked': 1.0,      # User engaged with suggestion
                'dismissed': -0.5,   # User actively rejected
                'ignored': 0.0       # Neutral
            }.get(user_action, 0.0)
            
            # Store in collection
            feedback_id = f"feedback_{int(time.time() * 1000)}"
            self.feedback_collection.add(
                documents=[doc_text],
                ids=[feedback_id],
                metadatas=[{
                    "category": insight_data.get('category', ''),
                    "agent_name": insight_data.get('agent_name', ''),
                    "action": user_action,
                    "score": score,
                    "timestamp": datetime.now().isoformat()
                }]
            )
            
            # Update in-memory scores for faster lookup
            pattern_key = f"{insight_data.get('category', '')}_{insight_data.get('agent_name', '')}"
            if pattern_key not in self.feedback_scores:
                self.feedback_scores[pattern_key] = []
            self.feedback_scores[pattern_key].append(score)
            
            logger.info(f"📊 Feedback recorded: {user_action} on {insight_data.get('category')} insight (score: {score})")
            
        except Exception as e:
            logger.error(f"❌ Failed to record feedback: {e}")
    
    def get_feedback_score(self, category: str, agent_name: str) -> float:
        """
        Get average feedback score for a category/agent combination
        Returns value between -1.0 (all dismissed) and 1.0 (all clicked)
        """
        pattern_key = f"{category}_{agent_name}"
        scores = self.feedback_scores.get(pattern_key, [])
        
        if not scores:
            return 0.0  # Neutral if no feedback yet
        
        avg_score = sum(scores) / len(scores)
        return avg_score
    
    def retrieve_similar_events_with_feedback(self, query: str, category: str = "", top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Enhanced retrieval that considers user feedback
        Boosts results similar to previously clicked insights
        """
        try:
            # Get more results than needed
            results = self.calendar_collection.query(
                query_texts=[query],
                n_results=top_k * 2  # Get extra for re-ranking
            )
            
            if not results or not results['metadatas'] or len(results['metadatas']) == 0:
                return []
            
            events = results['metadatas'][0]
            distances = results['distances'][0] if results.get('distances') else [0] * len(events)
            
            # Check if we have positive feedback for similar contexts
            # Find insights user clicked on that match this query
            try:
                similar_feedback = self.feedback_collection.query(
                    query_texts=[query],
                    n_results=5,
                    where={"action": "clicked"}  # Only positive feedback
                )
                has_positive_feedback = (similar_feedback and 
                                        similar_feedback.get('metadatas') and 
                                        len(similar_feedback['metadatas'][0]) > 0)
            except:
                has_positive_feedback = False
            
            # Re-rank based on feedback
            scored_events = []
            for event, distance in zip(events, distances):
                score = 1.0 / (1.0 + distance)  # Convert distance to similarity score
                
                # Boost if similar queries got positive feedback
                if has_positive_feedback:
                    score *= 1.2  # 20% boost
                    logger.debug(f"   Boosting result based on past positive feedback")
                
                scored_events.append((score, event))
            
            # Sort by score and return top_k
            scored_events.sort(reverse=True, key=lambda x: x[0])
            final_events = [event for _, event in scored_events[:top_k]]
            
            if has_positive_feedback:
                logger.info(f"🔍 Found {len(final_events)} events (feedback-enhanced)")
            else:
                logger.info(f"🔍 Found {len(final_events)} events for query: '{query}'")
            
            return final_events
            
        except Exception as e:
            logger.error(f"❌ Feedback-enhanced retrieval failed, falling back to standard: {e}")
            # Fallback to standard retrieval
            return self.retrieve_similar_events(query, top_k)
    
    def get_stats(self) -> Dict[str, int]:
        """Get stats about indexed data"""
        try:
            return {
                "calendar_events": self.calendar_collection.count(),
                "locations": self.location_collection.count(),
                "feedback_items": self.feedback_collection.count()
            }
        except:
            return {"calendar_events": 0, "locations": 0, "feedback_items": 0}
