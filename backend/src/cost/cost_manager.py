"""CostManager - Day 38
AI API and AWS resource cost tracking - Size: ~6.5KB"""
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class ResourceType(Enum):
    """Resource types"""

    AI_API = "ai_api"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"


class CostAlert(Enum):
    """Cost alert levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CostManager:
    """Manage AI API and AWS costs - Size optimized to 6.5KB"""

    def __init__(self):
        self.costs = []
        self.budgets = {"daily": 100.0, "weekly": 500.0, "monthly": 2000.0}
        self.pricing = {
            # AI API pricing (per 1K tokens)
            "claude_opus": 0.015,
            "claude_sonnet": 0.003,
            "gpt4_turbo": 0.01,
            "gpt3_5": 0.002,
            # AWS pricing (per hour)
            "ec2_t3_micro": 0.0104,
            "ec2_t3_small": 0.0208,
            "rds_db_t3_micro": 0.017,
            "lambda_request": 0.0000002,  # per request
            "s3_storage": 0.023 / 730,  # per GB/hour
            "elasticache": 0.016,
        }
        self.usage = {"ai_tokens": 0, "compute_hours": 0, "storage_gb": 0, "requests": 0}
        self.alerts = []
        self.optimizations = []

    def track_cost(
        self, resource: str, amount: float, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Track resource cost"""
        entry = {
            "id": self._generate_id(),
            "resource": resource,
            "type": self._determine_type(resource),
            "amount": amount,
            "cost": self._calculate_cost(resource, amount),
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self.costs.append(entry)
        self._update_usage(resource, amount)

        # Check budget
        alert = self._check_budget()
        if alert:
            self.alerts.append(alert)

        # Suggest optimization if needed
        optimization = self._suggest_optimization(resource)
        if optimization:
            self.optimizations.append(optimization)

        return {
            "cost_id": entry["id"],
            "cost": entry["cost"],
            "total_today": self._get_today_total(),
            "alert": alert,
            "optimization": optimization,
        }

    def _calculate_cost(self, resource: str, amount: float) -> float:
        """Calculate cost based on resource and amount"""
        if resource in self.pricing:
            return round(self.pricing[resource] * amount, 4)

        # Default pricing for unknown resources
        if "ai" in resource.lower():
            return round(0.005 * amount, 4)  # Default AI pricing
        elif "compute" in resource.lower():
            return round(0.01 * amount, 4)  # Default compute pricing
        else:
            return round(0.001 * amount, 4)  # Default minimal pricing

    def _determine_type(self, resource: str) -> ResourceType:
        """Determine resource type"""
        if any(ai in resource for ai in ["claude", "gpt", "ai"]):
            return ResourceType.AI_API
        elif any(comp in resource for comp in ["ec2", "lambda", "compute"]):
            return ResourceType.COMPUTE
        elif any(stor in resource for stor in ["s3", "storage"]):
            return ResourceType.STORAGE
        elif any(db in resource for db in ["rds", "dynamodb", "database"]):
            return ResourceType.DATABASE
        else:
            return ResourceType.NETWORK

    def _update_usage(self, resource: str, amount: float):
        """Update usage metrics"""
        if "ai" in resource.lower() or "token" in resource.lower():
            self.usage["ai_tokens"] += amount
        elif "ec2" in resource.lower() or "compute" in resource.lower():
            self.usage["compute_hours"] += amount
        elif "s3" in resource.lower() or "storage" in resource.lower():
            self.usage["storage_gb"] += amount
        else:
            self.usage["requests"] += amount

    def _check_budget(self) -> Optional[Dict[str, Any]]:
        """Check if budget exceeded"""
        daily_total = self._get_today_total()
        weekly_total = self._get_week_total()
        monthly_total = self._get_month_total()

        # Check thresholds
        if daily_total > self.budgets["daily"]:
            return {
                "level": CostAlert.CRITICAL,
                "message": f"Daily budget exceeded: ${daily_total:.2f} > ${self.budgets['daily']:.2f}",
                "timestamp": datetime.now().isoformat(),
            }
        elif daily_total > self.budgets["daily"] * 0.8:
            return {
                "level": CostAlert.WARNING,
                "message": f"80% of daily budget used: ${daily_total:.2f}",
                "timestamp": datetime.now().isoformat(),
            }
        elif weekly_total > self.budgets["weekly"] * 0.9:
            return {
                "level": CostAlert.WARNING,
                "message": f"90% of weekly budget used: ${weekly_total:.2f}",
                "timestamp": datetime.now().isoformat(),
            }

        return None

    def _suggest_optimization(self, resource: str) -> Optional[Dict[str, Any]]:
        """Suggest cost optimization"""
        # Check AI token usage
        if "claude_opus" in resource and self.usage["ai_tokens"] > 10000:
            return {
                "resource": resource,
                "suggestion": "Switch to Claude Sonnet for non-critical tasks",
                "potential_savings": "80% reduction",
                "action": "use_sonnet_for_simple_tasks",
            }

        # Check compute usage
        if "ec2" in resource and self.usage["compute_hours"] > 24:
            return {
                "resource": resource,
                "suggestion": "Use spot instances or Lambda for batch jobs",
                "potential_savings": "70% reduction",
                "action": "migrate_to_serverless",
            }

        # Check storage
        if "s3" in resource and self.usage["storage_gb"] > 100:
            return {
                "resource": resource,
                "suggestion": "Enable S3 Intelligent-Tiering",
                "potential_savings": "30% reduction",
                "action": "enable_intelligent_tiering",
            }

        return None

    def apply_optimization(self, optimization_id: str) -> Dict[str, Any]:
        """Apply cost optimization"""
        # Find optimization
        opt = None
        for o in self.optimizations:
            if o.get("resource") == optimization_id:
                opt = o
                break

        if not opt:
            return {"error": "Optimization not found"}

        # Apply action
        action = opt["action"]

        if action == "use_sonnet_for_simple_tasks":
            # Update default AI model
            self.pricing["claude_sonnet"] = 0.003  # Ensure lower pricing
            result = "Switched to Claude Sonnet for simple tasks"
        elif action == "migrate_to_serverless":
            # Simulate migration
            self.usage["compute_hours"] *= 0.3  # Reduce compute hours
            result = "Migrated batch jobs to Lambda"
        elif action == "enable_intelligent_tiering":
            # Enable tiering
            self.pricing["s3_storage"] *= 0.7  # Reduce storage cost
            result = "Enabled S3 Intelligent-Tiering"
        else:
            result = "Optimization applied"

        return {"optimization": opt, "result": result, "timestamp": datetime.now().isoformat()}

    def _get_today_total(self) -> float:
        """Get today's total cost"""
        today = datetime.now().date()
        total = 0.0

        for cost in self.costs:
            cost_date = datetime.fromisoformat(cost["timestamp"]).date()
            if cost_date == today:
                total += cost["cost"]

        return round(total, 2)

    def _get_week_total(self) -> float:
        """Get this week's total cost"""
        week_ago = datetime.now() - timedelta(days=7)
        total = 0.0

        for cost in self.costs:
            cost_time = datetime.fromisoformat(cost["timestamp"])
            if cost_time > week_ago:
                total += cost["cost"]

        return round(total, 2)

    def _get_month_total(self) -> float:
        """Get this month's total cost"""
        month_start = datetime.now().replace(day=1)
        total = 0.0

        for cost in self.costs:
            cost_time = datetime.fromisoformat(cost["timestamp"])
            if cost_time >= month_start:
                total += cost["cost"]

        return round(total, 2)

    def get_cost_report(self, period: str = "daily") -> Dict[str, Any]:
        """Generate cost report"""
        if period == "daily":
            total = self._get_today_total()
            budget = self.budgets["daily"]
        elif period == "weekly":
            total = self._get_week_total()
            budget = self.budgets["weekly"]
        else:  # monthly
            total = self._get_month_total()
            budget = self.budgets["monthly"]

        # Group by resource type
        by_type = {}
        for cost in self.costs:
            rtype = cost["type"].value
            if rtype not in by_type:
                by_type[rtype] = 0.0
            by_type[rtype] += cost["cost"]

        return {
            "period": period,
            "total_cost": total,
            "budget": budget,
            "utilization": round((total / budget) * 100, 1) if budget > 0 else 0,
            "by_type": by_type,
            "top_resources": self._get_top_resources(),
            "alerts": len([a for a in self.alerts if a["level"] == CostAlert.CRITICAL]),
            "optimizations_available": len(self.optimizations),
        }

    def _get_top_resources(self) -> List[Dict[str, Any]]:
        """Get top cost resources"""
        resource_costs = {}

        for cost in self.costs:
            resource = cost["resource"]
            if resource not in resource_costs:
                resource_costs[resource] = 0.0
            resource_costs[resource] += cost["cost"]

        # Sort by cost
        sorted_resources = sorted(resource_costs.items(), key=lambda x: x[1], reverse=True)

        return [{"resource": r, "cost": c} for r, c in sorted_resources[:5]]  # Top 5

    def set_budget(self, period: str, amount: float) -> Dict[str, Any]:
        """Set budget for period"""
        if period in self.budgets:
            old_budget = self.budgets[period]
            self.budgets[period] = amount

            return {
                "period": period,
                "old_budget": old_budget,
                "new_budget": amount,
                "updated": True,
            }

        return {"error": f"Invalid period: {period}"}

    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid

        return str(uuid.uuid4())[:8]

    def get_metrics(self) -> Dict[str, Any]:
        """Get cost metrics"""
        return {
            "total_costs_tracked": len(self.costs),
            "daily_total": self._get_today_total(),
            "weekly_total": self._get_week_total(),
            "monthly_total": self._get_month_total(),
            "usage": self.usage,
            "active_alerts": len(self.alerts),
            "optimizations_available": len(self.optimizations),
        }
