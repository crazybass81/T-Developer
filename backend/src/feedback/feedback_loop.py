"""FeedbackLoop - Day 37
User feedback collection and automatic improvement trigger - Size: ~6.5KB"""
import json
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class FeedbackType(Enum):
    """Feedback types"""

    PERFORMANCE = "performance"
    QUALITY = "quality"
    FEATURE = "feature"
    BUG = "bug"
    IMPROVEMENT = "improvement"


class FeedbackPriority(Enum):
    """Feedback priority"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class FeedbackLoop:
    """Collect feedback and trigger improvements - Size optimized to 6.5KB"""

    def __init__(self):
        self.feedbacks = []
        self.learning_data = {}
        self.improvement_triggers = []
        self.metrics = {
            "total_feedback": 0,
            "improvements_triggered": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
        }
        self.thresholds = {
            "critical_threshold": 1,  # Immediate action
            "high_threshold": 5,  # Quick action
            "medium_threshold": 10,  # Normal action
            "low_threshold": 20,  # Batch action
        }

    def collect_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Collect user feedback"""
        # Create feedback entry
        entry = {
            "id": self._generate_id(),
            "type": FeedbackType[feedback.get("type", "IMPROVEMENT").upper()],
            "priority": FeedbackPriority[feedback.get("priority", "MEDIUM").upper()],
            "description": feedback.get("description", ""),
            "agent_id": feedback.get("agent_id"),
            "user_id": feedback.get("user_id", "anonymous"),
            "timestamp": datetime.now().isoformat(),
            "processed": False,
        }

        # Store feedback
        self.feedbacks.append(entry)
        self.metrics["total_feedback"] += 1

        # Analyze and potentially trigger improvement
        trigger_result = self._analyze_feedback(entry)

        # Update learning data
        self._update_learning_data(entry)

        return {"feedback_id": entry["id"], "status": "collected", "trigger": trigger_result}

    def _analyze_feedback(self, feedback: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze feedback and decide on improvement trigger"""
        priority = feedback["priority"]

        # Count similar feedbacks
        similar_count = self._count_similar_feedback(feedback)

        # Check if threshold met
        should_trigger = False
        if priority == FeedbackPriority.CRITICAL:
            should_trigger = True
        elif (
            priority == FeedbackPriority.HIGH and similar_count >= self.thresholds["high_threshold"]
        ):
            should_trigger = True
        elif (
            priority == FeedbackPriority.MEDIUM
            and similar_count >= self.thresholds["medium_threshold"]
        ):
            should_trigger = True
        elif priority == FeedbackPriority.LOW and similar_count >= self.thresholds["low_threshold"]:
            should_trigger = True

        if should_trigger:
            return self._trigger_improvement(feedback, similar_count)

        return None

    def _trigger_improvement(self, feedback: Dict[str, Any], count: int) -> Dict[str, Any]:
        """Trigger automatic improvement"""
        trigger = {
            "id": self._generate_id(),
            "feedback_id": feedback["id"],
            "type": feedback["type"].value,
            "priority": feedback["priority"].value,
            "agent_id": feedback.get("agent_id"),
            "similar_count": count,
            "triggered_at": datetime.now().isoformat(),
            "action": self._determine_action(feedback),
        }

        self.improvement_triggers.append(trigger)
        self.metrics["improvements_triggered"] += 1

        # Mark related feedbacks as processed
        self._mark_processed(feedback)

        return trigger

    def _determine_action(self, feedback: Dict[str, Any]) -> str:
        """Determine improvement action based on feedback"""
        ftype = feedback["type"]

        if ftype == FeedbackType.PERFORMANCE:
            return "optimize_performance"
        elif ftype == FeedbackType.QUALITY:
            return "improve_quality"
        elif ftype == FeedbackType.BUG:
            return "fix_bug"
        elif ftype == FeedbackType.FEATURE:
            return "add_feature"
        else:
            return "general_improvement"

    def _count_similar_feedback(self, feedback: Dict[str, Any]) -> int:
        """Count similar unprocessed feedback"""
        count = 0
        for fb in self.feedbacks:
            if (
                not fb["processed"]
                and fb["type"] == feedback["type"]
                and fb.get("agent_id") == feedback.get("agent_id")
            ):
                count += 1
        return count

    def _mark_processed(self, feedback: Dict[str, Any]):
        """Mark similar feedback as processed"""
        for fb in self.feedbacks:
            if (
                not fb["processed"]
                and fb["type"] == feedback["type"]
                and fb.get("agent_id") == feedback.get("agent_id")
            ):
                fb["processed"] = True

    def _update_learning_data(self, feedback: Dict[str, Any]):
        """Update learning data for patterns"""
        key = f"{feedback['type'].value}_{feedback.get('agent_id', 'general')}"

        if key not in self.learning_data:
            self.learning_data[key] = {
                "count": 0,
                "priorities": [],
                "timestamps": [],
                "patterns": {},
            }

        self.learning_data[key]["count"] += 1
        self.learning_data[key]["priorities"].append(feedback["priority"].value)
        self.learning_data[key]["timestamps"].append(feedback["timestamp"])

        # Detect patterns
        self._detect_patterns(key)

    def _detect_patterns(self, key: str):
        """Detect feedback patterns"""
        data = self.learning_data[key]

        # Time-based patterns
        if len(data["timestamps"]) >= 5:
            recent = data["timestamps"][-5:]
            time_diffs = []
            for i in range(1, len(recent)):
                t1 = datetime.fromisoformat(recent[i - 1])
                t2 = datetime.fromisoformat(recent[i])
                time_diffs.append((t2 - t1).total_seconds())

            avg_interval = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            data["patterns"]["avg_interval"] = avg_interval

            # Detect if feedback is increasing
            if avg_interval < 3600:  # Less than 1 hour between feedbacks
                data["patterns"]["trend"] = "increasing"
            else:
                data["patterns"]["trend"] = "stable"

    def get_improvement_suggestions(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """Get improvement suggestions based on feedback"""
        suggestions = []

        for key, data in self.learning_data.items():
            if agent_id and agent_id not in key:
                continue

            if data["count"] >= 3:  # Minimum feedback for suggestion
                suggestion = {
                    "agent_id": key.split("_")[-1] if "_" in key else "general",
                    "type": key.split("_")[0],
                    "frequency": data["count"],
                    "trend": data["patterns"].get("trend", "unknown"),
                    "priority": self._calculate_priority(data),
                    "action": self._suggest_action(key, data),
                }
                suggestions.append(suggestion)

        return sorted(suggestions, key=lambda x: x["priority"])

    def _calculate_priority(self, data: Dict[str, Any]) -> int:
        """Calculate priority based on feedback data"""
        priorities = data["priorities"]
        if not priorities:
            return 4

        # Weight recent feedback more
        recent_priorities = priorities[-10:] if len(priorities) > 10 else priorities
        avg_priority = sum(recent_priorities) / len(recent_priorities)

        return round(avg_priority)

    def _suggest_action(self, key: str, data: Dict[str, Any]) -> str:
        """Suggest action based on patterns"""
        if "performance" in key:
            return "Optimize algorithms and caching"
        elif "quality" in key:
            return "Refactor and add tests"
        elif "bug" in key:
            return "Debug and fix issues"
        elif "feature" in key:
            return "Implement requested features"
        else:
            return "General improvements needed"

    def track_improvement_effect(self, trigger_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Track the effect of triggered improvements"""
        # Find trigger
        trigger = None
        for t in self.improvement_triggers:
            if t["id"] == trigger_id:
                trigger = t
                break

        if not trigger:
            return {"error": "Trigger not found"}

        # Record result
        trigger["result"] = result
        trigger["completed_at"] = datetime.now().isoformat()

        # Update success rate
        successful = result.get("success", False)
        total = self.metrics["improvements_triggered"]
        if total > 0:
            current_success = self.metrics["success_rate"] * (total - 1)
            self.metrics["success_rate"] = (current_success + (1 if successful else 0)) / total

        return {"trigger_id": trigger_id, "success": successful, "metrics_updated": True}

    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid

        return str(uuid.uuid4())[:8]

    def get_metrics(self) -> Dict[str, Any]:
        """Get feedback loop metrics"""
        return {
            **self.metrics,
            "pending_feedback": sum(1 for f in self.feedbacks if not f["processed"]),
            "learning_data_size": len(self.learning_data),
        }
