"""
Conversation Memory Module
Manages conversation history and maintains context across interactions
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import hashlib
from dataclasses import dataclass, asdict

@dataclass
class ConversationTurn:
    """Single turn in conversation"""
    timestamp: str
    user_input: str
    agent_response: Dict[str, Any]
    context: Dict[str, Any]
    turn_number: int

@dataclass
class ConversationSession:
    """Complete conversation session"""
    session_id: str
    user_id: str
    started_at: str
    last_updated: str
    turns: List[ConversationTurn]
    extracted_requirements: Dict[str, Any]
    project_evolution: List[Dict[str, Any]]
    status: str  # active, completed, abandoned

class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 10, ttl_hours: int = 24):
        self.max_history = max_history
        self.ttl_hours = ttl_hours
        self.sessions = {}
        self.user_profiles = {}
        self.context_cache = {}
        
        # Memory strategies
        self.summarization_threshold = 5  # Summarize after 5 turns
        self.relevance_decay = 0.8  # Decay factor for old information
    
    async def create_session(
        self,
        user_id: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new conversation session"""
        
        session_id = self._generate_session_id(user_id)
        
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            started_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            turns=[],
            extracted_requirements={},
            project_evolution=[],
            status="active"
        )
        
        self.sessions[session_id] = session
        
        # Initialize user profile if new
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "preferences": {},
                "common_domains": [],
                "technology_stack": [],
                "interaction_style": "detailed",
                "clarification_count": 0
            }
        
        # Set initial context
        if initial_context:
            self.context_cache[session_id] = initial_context
        
        return session_id
    
    async def add_turn(
        self,
        session_id: str,
        user_input: str,
        agent_response: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add conversation turn to session"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            agent_response=agent_response,
            context=context or {},
            turn_number=len(session.turns) + 1
        )
        
        session.turns.append(turn)
        session.last_updated = datetime.now().isoformat()
        
        # Update extracted requirements
        if "requirements" in agent_response:
            self._merge_requirements(session, agent_response["requirements"])
        
        # Track project evolution
        if "project_changes" in agent_response:
            session.project_evolution.append({
                "turn": turn.turn_number,
                "changes": agent_response["project_changes"],
                "timestamp": turn.timestamp
            })
        
        # Summarize if needed
        if len(session.turns) >= self.summarization_threshold:
            await self._summarize_conversation(session_id)
        
        # Update user profile
        await self._update_user_profile(session.user_id, user_input, agent_response)
    
    async def get_context(
        self,
        session_id: str,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """Get conversation context for session"""
        
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        
        context = {
            "session_id": session_id,
            "user_id": session.user_id,
            "turn_count": len(session.turns),
            "extracted_requirements": session.extracted_requirements,
            "project_evolution": session.project_evolution[-3:],  # Last 3 changes
            "user_profile": self.user_profiles.get(session.user_id, {})
        }
        
        if include_history:
            # Get relevant history with decay
            relevant_turns = self._get_relevant_turns(session)
            context["conversation_history"] = relevant_turns
            
            # Add summarized context
            if session_id in self.context_cache:
                context["summarized_context"] = self.context_cache[session_id]
        
        return context
    
    async def get_previous_requirements(
        self,
        user_id: str,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get previous requirements from user's past sessions"""
        
        user_sessions = [
            s for s in self.sessions.values()
            if s.user_id == user_id and s.status == "completed"
        ]
        
        requirements = []
        
        for session in user_sessions:
            req = session.extracted_requirements.copy()
            req["session_id"] = session.session_id
            req["created_at"] = session.started_at
            
            # Filter by domain if specified
            if domain and req.get("domain") != domain:
                continue
            
            requirements.append(req)
        
        # Sort by recency
        requirements.sort(key=lambda x: x["created_at"], reverse=True)
        
        return requirements[:5]  # Return last 5 projects
    
    async def find_similar_conversations(
        self,
        current_input: str,
        limit: int = 3
    ) -> List[Tuple[str, float]]:
        """Find similar past conversations"""
        
        similar = []
        current_hash = self._hash_input(current_input)
        
        for session_id, session in self.sessions.items():
            if session.status != "completed":
                continue
            
            # Calculate similarity based on requirements
            similarity = self._calculate_similarity(
                current_input,
                session.extracted_requirements
            )
            
            if similarity > 0.7:  # 70% similarity threshold
                similar.append((session_id, similarity))
        
        # Sort by similarity
        similar.sort(key=lambda x: x[1], reverse=True)
        
        return similar[:limit]
    
    async def _summarize_conversation(self, session_id: str) -> None:
        """Summarize conversation to reduce memory usage"""
        
        session = self.sessions[session_id]
        
        if len(session.turns) < self.summarization_threshold:
            return
        
        # Extract key points from conversation
        summary = {
            "key_requirements": [],
            "clarifications": [],
            "decisions": [],
            "constraints": []
        }
        
        for turn in session.turns:
            response = turn.agent_response
            
            # Extract key information
            if "requirements" in response:
                summary["key_requirements"].extend(
                    response["requirements"].get("functional_requirements", [])[:3]
                )
            
            if "clarifications" in response:
                summary["clarifications"].append({
                    "turn": turn.turn_number,
                    "clarification": response["clarifications"]
                })
            
            if "decisions" in response:
                summary["decisions"].extend(response["decisions"])
            
            if "constraints" in response:
                summary["constraints"].extend(response["constraints"])
        
        # Store summary
        self.context_cache[session_id] = summary
        
        # Keep only recent turns in memory
        if len(session.turns) > self.max_history:
            session.turns = session.turns[-self.max_history:]
    
    def _merge_requirements(
        self,
        session: ConversationSession,
        new_requirements: Dict[str, Any]
    ) -> None:
        """Merge new requirements with existing ones"""
        
        existing = session.extracted_requirements
        
        for key, value in new_requirements.items():
            if key not in existing:
                existing[key] = value
            elif isinstance(value, list):
                # Merge lists without duplicates
                existing[key] = list(set(existing[key] + value))
            elif isinstance(value, dict):
                # Merge dictionaries
                existing[key].update(value)
            else:
                # Overwrite with new value
                existing[key] = value
    
    def _get_relevant_turns(
        self,
        session: ConversationSession,
        max_turns: int = 5
    ) -> List[Dict[str, Any]]:
        """Get relevant conversation turns with decay"""
        
        if not session.turns:
            return []
        
        relevant = []
        total_turns = len(session.turns)
        
        for i, turn in enumerate(session.turns[-max_turns:]):
            # Calculate relevance with decay
            age_factor = (total_turns - turn.turn_number) / total_turns
            relevance = self.relevance_decay ** age_factor
            
            relevant.append({
                "turn": turn.turn_number,
                "user_input": turn.user_input,
                "key_points": self._extract_key_points(turn.agent_response),
                "relevance": relevance
            })
        
        return relevant
    
    def _extract_key_points(self, response: Dict[str, Any]) -> List[str]:
        """Extract key points from agent response"""
        
        key_points = []
        
        # Extract main requirements
        if "requirements" in response:
            reqs = response["requirements"]
            if "functional_requirements" in reqs:
                key_points.extend(reqs["functional_requirements"][:2])
        
        # Extract decisions
        if "decisions" in response:
            key_points.extend(response["decisions"][:2])
        
        # Extract important features
        if "features" in response:
            key_points.extend(response["features"][:2])
        
        return key_points
    
    async def _update_user_profile(
        self,
        user_id: str,
        user_input: str,
        agent_response: Dict[str, Any]
    ) -> None:
        """Update user profile based on interaction"""
        
        if user_id not in self.user_profiles:
            return
        
        profile = self.user_profiles[user_id]
        
        # Track domain preferences
        if "domain" in agent_response:
            domain = agent_response["domain"]
            if domain not in profile["common_domains"]:
                profile["common_domains"].append(domain)
        
        # Track technology preferences
        if "technology_preferences" in agent_response:
            tech_prefs = agent_response["technology_preferences"]
            for tech in tech_prefs.get("preferred", []):
                if tech not in profile["technology_stack"]:
                    profile["technology_stack"].append(tech)
        
        # Track clarification patterns
        if "needs_clarification" in agent_response:
            profile["clarification_count"] += 1
        
        # Adjust interaction style
        if len(user_input) > 500:
            profile["interaction_style"] = "detailed"
        elif len(user_input) < 100:
            profile["interaction_style"] = "concise"
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate unique session ID"""
        
        timestamp = datetime.now().isoformat()
        data = f"{user_id}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _hash_input(self, input_text: str) -> str:
        """Generate hash for input text"""
        
        return hashlib.sha256(input_text.encode()).hexdigest()
    
    def _calculate_similarity(
        self,
        current_input: str,
        past_requirements: Dict[str, Any]
    ) -> float:
        """Calculate similarity between current input and past requirements"""
        
        # Simple keyword-based similarity
        current_words = set(current_input.lower().split())
        past_words = set()
        
        # Extract words from past requirements
        for key, value in past_requirements.items():
            if isinstance(value, str):
                past_words.update(value.lower().split())
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        past_words.update(item.lower().split())
        
        if not past_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(current_words & past_words)
        union = len(current_words | past_words)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        
        current_time = datetime.now()
        expired_count = 0
        
        for session_id in list(self.sessions.keys()):
            session = self.sessions[session_id]
            last_updated = datetime.fromisoformat(session.last_updated)
            
            if (current_time - last_updated) > timedelta(hours=self.ttl_hours):
                del self.sessions[session_id]
                if session_id in self.context_cache:
                    del self.context_cache[session_id]
                expired_count += 1
        
        return expired_count