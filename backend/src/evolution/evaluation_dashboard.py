"""EvaluationDashboard - Day 45
Comprehensive evaluation dashboard for evolution monitoring - Size: ~6.5KB"""
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class EvaluationDashboard:
    """Dashboard for monitoring evolution evaluation - Size optimized"""

    def __init__(self):
        self.metrics = {}
        self.agents = {}
        self.generations = {}
        self.alerts = []
        self.thresholds = self._initialize_thresholds()

    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialize alert thresholds"""
        return {
            "fitness_decline": 10,  # Alert if fitness drops by 10%
            "error_rate": 5,  # Alert if error rate > 5%
            "stagnation": 5,  # Alert if no improvement for 5 generations
            "resource_usage": 90,  # Alert if resource usage > 90%
            "diversity_loss": 20,  # Alert if diversity drops by 20%
        }

    def update_agent(self, agent_id: str, evaluation_data: Dict[str, Any]):
        """Update agent evaluation data"""
        if agent_id not in self.agents:
            self.agents[agent_id] = {"history": [], "current_generation": 0, "status": "active"}

        self.agents[agent_id]["history"].append(
            {"timestamp": datetime.now().isoformat(), "data": evaluation_data}
        )

        # Keep only last 100 entries
        if len(self.agents[agent_id]["history"]) > 100:
            self.agents[agent_id]["history"] = self.agents[agent_id]["history"][-100:]

        # Check for alerts
        self._check_alerts(agent_id, evaluation_data)

    def update_generation(self, generation: int, summary: Dict[str, Any]):
        """Update generation summary"""
        self.generations[generation] = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "agent_count": len(summary.get("agents", [])),
            "average_fitness": summary.get("average_fitness", 0),
        }

    def _check_alerts(self, agent_id: str, data: Dict[str, Any]):
        """Check for alert conditions"""
        history = self.agents[agent_id]["history"]

        # Check fitness decline
        if len(history) >= 2:
            prev_fitness = history[-2]["data"].get("fitness", 100)
            curr_fitness = data.get("fitness", 100)

            if prev_fitness > 0:
                decline = ((prev_fitness - curr_fitness) / prev_fitness) * 100
                if decline > self.thresholds["fitness_decline"]:
                    self._add_alert(
                        "fitness_decline", agent_id, f"Fitness declined by {decline:.1f}%"
                    )

        # Check error rate
        error_rate = data.get("error_rate", 0)
        if error_rate > self.thresholds["error_rate"]:
            self._add_alert("high_error_rate", agent_id, f"Error rate: {error_rate:.1f}%")

        # Check stagnation
        if len(history) >= self.thresholds["stagnation"]:
            recent = history[-int(self.thresholds["stagnation"]) :]
            fitness_values = [h["data"].get("fitness", 0) for h in recent]

            if all(abs(f - fitness_values[0]) < 1 for f in fitness_values):
                self._add_alert("stagnation", agent_id, "No improvement in recent generations")

    def _add_alert(self, alert_type: str, agent_id: str, message: str):
        """Add alert to dashboard"""
        alert = {
            "type": alert_type,
            "agent_id": agent_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "severity": self._get_severity(alert_type),
        }

        self.alerts.append(alert)

        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]

    def _get_severity(self, alert_type: str) -> str:
        """Get alert severity"""
        severities = {
            "fitness_decline": "warning",
            "high_error_rate": "critical",
            "stagnation": "info",
            "resource_usage": "warning",
            "diversity_loss": "warning",
        }
        return severities.get(alert_type, "info")

    def get_overview(self) -> Dict[str, Any]:
        """Get dashboard overview"""
        active_agents = [aid for aid, data in self.agents.items() if data["status"] == "active"]

        # Calculate overall metrics
        total_fitness = 0
        total_error_rate = 0
        count = 0

        for agent_id in active_agents:
            if agent_id in self.agents and self.agents[agent_id]["history"]:
                latest = self.agents[agent_id]["history"][-1]["data"]
                total_fitness += latest.get("fitness", 0)
                total_error_rate += latest.get("error_rate", 0)
                count += 1

        overview = {
            "timestamp": datetime.now().isoformat(),
            "active_agents": len(active_agents),
            "total_agents": len(self.agents),
            "generations": len(self.generations),
            "average_fitness": total_fitness / count if count > 0 else 0,
            "average_error_rate": total_error_rate / count if count > 0 else 0,
            "recent_alerts": len(
                [
                    a
                    for a in self.alerts
                    if datetime.fromisoformat(a["timestamp"]) > datetime.now() - timedelta(hours=1)
                ]
            ),
            "status": self._get_system_status(),
        }

        return overview

    def _get_system_status(self) -> str:
        """Get overall system status"""
        critical_alerts = [a for a in self.alerts if a["severity"] == "critical"]
        warning_alerts = [a for a in self.alerts if a["severity"] == "warning"]

        if critical_alerts:
            return "critical"
        elif len(warning_alerts) > 5:
            return "warning"
        else:
            return "healthy"

    def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed agent information"""
        if agent_id not in self.agents:
            return {"error": "Agent not found"}

        agent_data = self.agents[agent_id]
        history = agent_data["history"]

        if not history:
            return {"error": "No evaluation data"}

        latest = history[-1]["data"]

        details = {
            "agent_id": agent_id,
            "status": agent_data["status"],
            "generation": agent_data["current_generation"],
            "evaluations": len(history),
            "current_fitness": latest.get("fitness", 0),
            "current_metrics": latest,
            "trend": self._calculate_trend(history),
            "recent_alerts": [a for a in self.alerts if a["agent_id"] == agent_id][-5:],
            "performance_chart": self._generate_chart_data(history, "fitness"),
            "error_chart": self._generate_chart_data(history, "error_rate"),
        }

        return details

    def _calculate_trend(self, history: List[Dict]) -> str:
        """Calculate metric trend"""
        if len(history) < 2:
            return "insufficient_data"

        recent = history[-5:]
        values = [h["data"].get("fitness", 0) for h in recent]

        if all(values[i] <= values[i + 1] for i in range(len(values) - 1)):
            return "improving"
        elif all(values[i] >= values[i + 1] for i in range(len(values) - 1)):
            return "declining"
        else:
            return "stable"

    def _generate_chart_data(self, history: List[Dict], metric: str) -> List[Dict]:
        """Generate chart data for visualization"""
        chart_data = []

        for entry in history[-20:]:  # Last 20 points
            chart_data.append(
                {"timestamp": entry["timestamp"], "value": entry["data"].get(metric, 0)}
            )

        return chart_data

    def get_generation_comparison(self, gen1: int, gen2: int) -> Dict[str, Any]:
        """Compare two generations"""
        if gen1 not in self.generations or gen2 not in self.generations:
            return {"error": "Generation data not found"}

        g1_data = self.generations[gen1]
        g2_data = self.generations[gen2]

        comparison = {
            "generation_1": {
                "number": gen1,
                "agent_count": g1_data["agent_count"],
                "average_fitness": g1_data["average_fitness"],
            },
            "generation_2": {
                "number": gen2,
                "agent_count": g2_data["agent_count"],
                "average_fitness": g2_data["average_fitness"],
            },
            "agent_change": g2_data["agent_count"] - g1_data["agent_count"],
            "fitness_change": g2_data["average_fitness"] - g1_data["average_fitness"],
            "improvement_rate": (
                (g2_data["average_fitness"] - g1_data["average_fitness"])
                / g1_data["average_fitness"]
                * 100
            )
            if g1_data["average_fitness"] > 0
            else 0,
        }

        return comparison

    def get_top_performers(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get top performing agents"""
        performers = []

        for agent_id, data in self.agents.items():
            if data["history"]:
                latest = data["history"][-1]["data"]
                performers.append(
                    {
                        "agent_id": agent_id,
                        "fitness": latest.get("fitness", 0),
                        "generation": data["current_generation"],
                        "trend": self._calculate_trend(data["history"]),
                    }
                )

        # Sort by fitness
        performers.sort(key=lambda x: x["fitness"], reverse=True)

        return performers[:count]

    def get_alerts(self, severity: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        cutoff = datetime.now() - timedelta(hours=hours)

        filtered = []
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert["timestamp"])

            if alert_time > cutoff:
                if severity is None or alert["severity"] == severity:
                    filtered.append(alert)

        return filtered

    def export_data(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Export dashboard data"""
        export = {"timestamp": datetime.now().isoformat(), "overview": self.get_overview()}

        if agent_id:
            export["agent_details"] = self.get_agent_details(agent_id)
        else:
            export["top_performers"] = self.get_top_performers()
            export["recent_alerts"] = self.get_alerts(hours=1)

        if self.generations:
            latest_gen = max(self.generations.keys())
            export["latest_generation"] = {
                "number": latest_gen,
                "data": self.generations[latest_gen],
            }

        return export

    def get_evolution_summary(self) -> Dict[str, Any]:
        """Get evolution progress summary"""
        if not self.generations:
            return {"error": "No generation data"}

        generations = sorted(self.generations.keys())

        summary = {
            "total_generations": len(generations),
            "first_generation": generations[0],
            "latest_generation": generations[-1],
            "fitness_progression": [],
            "population_changes": [],
            "evolution_rate": 0,
        }

        # Track fitness progression
        for gen in generations:
            summary["fitness_progression"].append(
                {
                    "generation": gen,
                    "average_fitness": self.generations[gen]["average_fitness"],
                    "agent_count": self.generations[gen]["agent_count"],
                }
            )

        # Calculate evolution rate
        if len(generations) >= 2:
            start_fitness = self.generations[generations[0]]["average_fitness"]
            end_fitness = self.generations[generations[-1]]["average_fitness"]

            if start_fitness > 0:
                summary["evolution_rate"] = (end_fitness - start_fitness) / start_fitness * 100

        return summary
