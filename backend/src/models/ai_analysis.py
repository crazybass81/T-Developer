"""
AI Analysis Result Storage Model
Day 6: Agent Registry Data Model
Generated: 2024-11-18

Store and manage AI analysis results from multiple models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class AIAnalysisResult:
    """Store AI analysis results"""

    agent_id: str
    analysis_type: str
    ai_model: str
    findings: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def get_recommendations(self) -> List[str]:
        """Get recommendations from findings"""
        return self.findings.get("recommendations", [])

    def get_confidence(self) -> float:
        """Get confidence score"""
        return self.findings.get("confidence", 0.0)


class ConsensusAnalyzer:
    """Analyze consensus from multiple AI models"""

    def __init__(self):
        self.results: Dict[str, Dict] = {}

    def add_result(self, ai_model: str, findings: Dict):
        """Add analysis result from an AI model"""
        self.results[ai_model] = findings

    def get_consensus(self) -> Dict:
        """Get consensus from all AI models"""
        if not self.results:
            return {}

        # Find common issues
        all_issues = []
        confidence_scores = []

        for model, findings in self.results.items():
            if "issue" in findings:
                all_issues.append(findings["issue"])
            if "confidence" in findings:
                confidence_scores.append(findings["confidence"])

        # Find most common issue
        if all_issues:
            # Count occurrences
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

            # Get most common
            agreed_issue = max(issue_counts.keys(), key=lambda k: issue_counts[k])
            agreement_count = issue_counts[agreed_issue]

            # Calculate agreement level
            agreement_ratio = agreement_count / len(all_issues)
            if agreement_ratio >= 0.8:
                agreement_level = "high"
            elif agreement_ratio >= 0.5:
                agreement_level = "medium"
            else:
                agreement_level = "low"
        else:
            agreed_issue = None
            agreement_level = "none"

        # Average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        return {
            "agreed_issue": agreed_issue,
            "confidence": avg_confidence,
            "agreement_level": agreement_level,
            "model_count": len(self.results),
        }


class AnalysisHistory:
    """Track analysis history over time"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.analyses: List[Dict] = []

    def add_analysis(self, timestamp: datetime, findings: Dict):
        """Add an analysis to history"""
        self.analyses.append({"timestamp": timestamp, "findings": findings})

        # Sort by timestamp
        self.analyses.sort(key=lambda x: x["timestamp"])

    def get_trend(self) -> str:
        """Get trend from analysis history"""
        if len(self.analyses) < 2:
            return "insufficient_data"

        # Compare first and last scores
        first_score = self.analyses[0]["findings"].get("score", 0)
        last_score = self.analyses[-1]["findings"].get("score", 0)

        if last_score > first_score:
            return "improving"
        elif last_score < first_score:
            return "degrading"
        else:
            return "stable"

    def get_improvement_rate(self) -> float:
        """Calculate improvement rate"""
        if len(self.analyses) < 2:
            return 0.0

        first_score = self.analyses[0]["findings"].get("score", 0)
        last_score = self.analyses[-1]["findings"].get("score", 0)

        return last_score - first_score

    def get_latest_findings(self) -> Dict:
        """Get most recent findings"""
        if self.analyses:
            return self.analyses[-1]["findings"]
        return {}
