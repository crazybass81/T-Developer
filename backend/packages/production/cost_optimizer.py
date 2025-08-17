"""
Cost optimization and FinOps system for T-Developer production environment.

This module provides comprehensive cost management including per-tenant cost tracking,
resource waste identification, optimization recommendations, and budget management.
"""

from __future__ import annotations

import asyncio
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class ResourceType(Enum):
    """Types of billable resources."""

    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    API_CALLS = "api_calls"
    DATA_TRANSFER = "data_transfer"
    BACKUP = "backup"
    MONITORING = "monitoring"


class CostCategory(Enum):
    """Cost categorization."""

    INFRASTRUCTURE = "infrastructure"
    PLATFORM = "platform"
    APPLICATION = "application"
    OPERATIONS = "operations"
    SUPPORT = "support"
    COMPLIANCE = "compliance"


class OptimizationType(Enum):
    """Types of optimization recommendations."""

    RIGHT_SIZE = "right_size"
    RESERVED_CAPACITY = "reserved_capacity"
    SPOT_INSTANCES = "spot_instances"
    STORAGE_TIERING = "storage_tiering"
    IDLE_RESOURCES = "idle_resources"
    SCHEDULE_BASED = "schedule_based"
    REGION_OPTIMIZATION = "region_optimization"


class BudgetStatus(Enum):
    """Budget status levels."""

    ON_TRACK = "on_track"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"


@dataclass
class CostRecord:
    """Individual cost record.

    Attributes:
        record_id: Unique record identifier
        timestamp: When cost was incurred
        tenant_id: Tenant identifier
        resource_type: Type of resource
        resource_id: Specific resource identifier
        cost_amount: Cost amount in dollars
        currency: Currency code
        usage_quantity: Quantity of resource used
        usage_unit: Unit of measurement
        region: Geographic region
        category: Cost category
        tags: Additional metadata tags
    """

    record_id: str
    timestamp: datetime
    tenant_id: str
    resource_type: ResourceType
    resource_id: str
    cost_amount: float
    currency: str = "USD"
    usage_quantity: float = 0.0
    usage_unit: str = ""
    region: str = ""
    category: CostCategory = CostCategory.INFRASTRUCTURE
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "cost_amount": self.cost_amount,
            "currency": self.currency,
            "usage_quantity": self.usage_quantity,
            "usage_unit": self.usage_unit,
            "region": self.region,
            "category": self.category.value,
            "tags": self.tags,
        }


@dataclass
class Budget:
    """Budget definition and tracking.

    Attributes:
        budget_id: Unique budget identifier
        name: Budget name
        description: Budget description
        tenant_id: Tenant this budget applies to (None for global)
        amount: Budget amount
        currency: Currency code
        period: Budget period (monthly, quarterly, annual)
        start_date: Budget period start
        end_date: Budget period end
        spent_amount: Amount spent so far
        alerts: Alert thresholds as percentages
        categories: Cost categories included in budget
        tags: Budget tags for organization
    """

    budget_id: str
    name: str
    description: str
    amount: float
    currency: str = "USD"
    period: str = "monthly"
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    spent_amount: float = 0.0
    alerts: list[float] = field(default_factory=lambda: [50.0, 75.0, 90.0])
    categories: set[CostCategory] = field(default_factory=set)
    tenant_id: Optional[str] = None
    tags: dict[str, str] = field(default_factory=dict)

    @property
    def utilization_percentage(self) -> float:
        """Calculate budget utilization percentage."""
        return (self.spent_amount / self.amount * 100) if self.amount > 0 else 0

    @property
    def remaining_amount(self) -> float:
        """Calculate remaining budget amount."""
        return max(0, self.amount - self.spent_amount)

    @property
    def status(self) -> BudgetStatus:
        """Get current budget status."""
        utilization = self.utilization_percentage

        if utilization >= 100:
            return BudgetStatus.EXCEEDED
        elif utilization >= 90:
            return BudgetStatus.CRITICAL
        elif utilization >= 75:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.ON_TRACK

    @property
    def days_remaining(self) -> int:
        """Get days remaining in budget period."""
        if self.end_date:
            return max(0, (self.end_date - datetime.utcnow()).days)
        return 0


@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation.

    Attributes:
        recommendation_id: Unique identifier
        type: Type of optimization
        title: Short recommendation title
        description: Detailed description
        tenant_id: Affected tenant
        resource_ids: Affected resources
        estimated_savings_monthly: Estimated monthly savings
        estimated_savings_annual: Estimated annual savings
        implementation_effort: Implementation effort (low, medium, high)
        risk_level: Risk level (low, medium, high)
        prerequisites: Prerequisites for implementation
        implementation_steps: Implementation steps
        created_at: When recommendation was created
        expires_at: When recommendation expires
        applied: Whether recommendation has been applied
    """

    recommendation_id: str
    type: OptimizationType
    title: str
    description: str
    estimated_savings_monthly: float
    estimated_savings_annual: float
    implementation_effort: str = "medium"
    risk_level: str = "low"
    prerequisites: list[str] = field(default_factory=list)
    implementation_steps: list[str] = field(default_factory=list)
    tenant_id: Optional[str] = None
    resource_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    applied: bool = False

    @property
    def is_expired(self) -> bool:
        """Check if recommendation has expired."""
        return self.expires_at and datetime.utcnow() > self.expires_at

    @property
    def roi_months(self) -> Optional[float]:
        """Calculate return on investment in months."""
        if self.estimated_savings_monthly > 0:
            # Assume implementation cost is proportional to effort
            effort_costs = {"low": 500, "medium": 2000, "high": 5000}
            implementation_cost = effort_costs.get(self.implementation_effort, 2000)
            return implementation_cost / self.estimated_savings_monthly
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "recommendation_id": self.recommendation_id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "tenant_id": self.tenant_id,
            "resource_ids": self.resource_ids,
            "estimated_savings_monthly": self.estimated_savings_monthly,
            "estimated_savings_annual": self.estimated_savings_annual,
            "implementation_effort": self.implementation_effort,
            "risk_level": self.risk_level,
            "prerequisites": self.prerequisites,
            "implementation_steps": self.implementation_steps,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "applied": self.applied,
            "roi_months": self.roi_months,
        }


@dataclass
class ResourceUsageMetrics:
    """Resource usage metrics for optimization analysis.

    Attributes:
        resource_id: Resource identifier
        resource_type: Type of resource
        tenant_id: Tenant owning the resource
        avg_cpu_utilization: Average CPU utilization percentage
        avg_memory_utilization: Average memory utilization percentage
        avg_storage_utilization: Average storage utilization percentage
        peak_utilization: Peak utilization percentage
        idle_time_percentage: Percentage of time resource was idle
        cost_per_hour: Cost per hour for this resource
        observation_period_hours: Period over which metrics were collected
        last_updated: When metrics were last updated
    """

    resource_id: str
    resource_type: ResourceType
    tenant_id: str
    avg_cpu_utilization: float = 0.0
    avg_memory_utilization: float = 0.0
    avg_storage_utilization: float = 0.0
    peak_utilization: float = 0.0
    idle_time_percentage: float = 0.0
    cost_per_hour: float = 0.0
    observation_period_hours: int = 24
    last_updated: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_underutilized(self) -> bool:
        """Check if resource is underutilized."""
        # Consider resource underutilized if avg utilization < 20% or idle > 80%
        avg_util = max(self.avg_cpu_utilization, self.avg_memory_utilization)
        return avg_util < 20 or self.idle_time_percentage > 80

    @property
    def is_overutilized(self) -> bool:
        """Check if resource is overutilized."""
        # Consider resource overutilized if peak utilization > 90%
        return self.peak_utilization > 90

    @property
    def waste_cost_per_hour(self) -> float:
        """Calculate wasted cost per hour."""
        if self.is_underutilized:
            # Assume we could downsize by the unused percentage
            unused_percentage = (
                100 - max(self.avg_cpu_utilization, self.avg_memory_utilization)
            ) / 100
            return self.cost_per_hour * unused_percentage
        return 0.0


class CostOptimizer:
    """Cost optimization and FinOps system.

    Provides comprehensive cost management including tracking, analysis,
    optimization recommendations, and budget management.

    Example:
        >>> optimizer = CostOptimizer()
        >>> await optimizer.initialize()
        >>> await optimizer.record_cost("tenant-1", ResourceType.COMPUTE, "instance-1", 5.20)
        >>> recommendations = await optimizer.analyze_optimization_opportunities()
    """

    def __init__(self, config: dict[str, Any] = None) -> None:
        """Initialize cost optimizer.

        Args:
            config: Optimizer configuration options
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cost_records: list[CostRecord] = []
        self._budgets: dict[str, Budget] = {}
        self._recommendations: dict[str, OptimizationRecommendation] = {}
        self._resource_metrics: dict[str, ResourceUsageMetrics] = {}
        self._cost_alerts: list[dict[str, Any]] = []
        self._pricing_data: dict[str, dict[str, float]] = {}
        self._monitoring_active = False

    async def initialize(self) -> None:
        """Initialize the cost optimizer.

        Sets up pricing data, default budgets, and monitoring.
        """
        self.logger.info("Initializing cost optimizer")

        await self._load_pricing_data()
        await self._create_default_budgets()
        await self._load_historical_costs()

        self.logger.info("Cost optimizer initialized successfully")

    async def _load_pricing_data(self) -> None:
        """Load pricing data for different resources."""
        # In production, load from cloud provider pricing APIs
        self._pricing_data = {
            "compute": {
                "small": 0.05,  # $0.05 per hour
                "medium": 0.20,  # $0.20 per hour
                "large": 0.80,  # $0.80 per hour
                "xlarge": 3.20,  # $3.20 per hour
            },
            "storage": {
                "standard": 0.023,  # $0.023 per GB per month
                "premium": 0.045,  # $0.045 per GB per month
                "archive": 0.004,  # $0.004 per GB per month
            },
            "network": {
                "data_transfer": 0.09,  # $0.09 per GB
                "load_balancer": 0.025,  # $0.025 per hour
            },
            "database": {
                "small": 0.12,  # $0.12 per hour
                "medium": 0.48,  # $0.48 per hour
                "large": 1.92,  # $1.92 per hour
            },
        }

        self.logger.info("Loaded pricing data")

    async def _create_default_budgets(self) -> None:
        """Create default budgets."""
        default_budgets = [
            {
                "budget_id": "global_monthly",
                "name": "Global Monthly Budget",
                "description": "Overall monthly spending budget",
                "amount": 10000.0,
                "period": "monthly",
                "categories": {CostCategory.INFRASTRUCTURE, CostCategory.PLATFORM},
            },
            {
                "budget_id": "compute_monthly",
                "name": "Compute Monthly Budget",
                "description": "Monthly compute spending budget",
                "amount": 5000.0,
                "period": "monthly",
                "categories": {CostCategory.INFRASTRUCTURE},
            },
            {
                "budget_id": "storage_monthly",
                "name": "Storage Monthly Budget",
                "description": "Monthly storage spending budget",
                "amount": 2000.0,
                "period": "monthly",
                "categories": {CostCategory.INFRASTRUCTURE},
            },
        ]

        for budget_data in default_budgets:
            end_date = budget_data.get("start_date", datetime.utcnow()) + timedelta(days=30)

            budget = Budget(
                budget_id=budget_data["budget_id"],
                name=budget_data["name"],
                description=budget_data["description"],
                amount=budget_data["amount"],
                period=budget_data["period"],
                end_date=end_date,
                categories=budget_data["categories"],
            )

            self._budgets[budget.budget_id] = budget

        self.logger.info(f"Created {len(self._budgets)} default budgets")

    async def _load_historical_costs(self) -> None:
        """Load historical cost data."""
        # In production, load from cost data store
        # For simulation, generate some sample data

        sample_tenants = ["tenant-1", "tenant-2", "tenant-3"]
        sample_resources = ["web-server-1", "db-server-1", "storage-1", "load-balancer-1"]

        # Generate cost data for last 30 days
        for days_ago in range(30):
            timestamp = datetime.utcnow() - timedelta(days=days_ago)

            for tenant_id in sample_tenants:
                for resource_id in sample_resources:
                    # Simulate varying costs
                    base_cost = {
                        "web-server": 2.40,
                        "db-server": 4.80,
                        "storage": 0.50,
                        "load-balancer": 0.60,
                    }
                    resource_type_key = resource_id.split("-")[0]

                    if resource_type_key in base_cost:
                        daily_cost = base_cost[resource_type_key] * (
                            0.8 + 0.4 * (days_ago % 7) / 7
                        )  # Weekly variation

                        record = CostRecord(
                            record_id=f"cost_{tenant_id}_{resource_id}_{timestamp.date()}",
                            timestamp=timestamp,
                            tenant_id=tenant_id,
                            resource_type=ResourceType.COMPUTE
                            if "server" in resource_id
                            else ResourceType.STORAGE,
                            resource_id=resource_id,
                            cost_amount=daily_cost,
                            usage_quantity=24,  # 24 hours
                            usage_unit="hours",
                            region="us-east-1",
                        )

                        self._cost_records.append(record)

        self.logger.info(f"Loaded {len(self._cost_records)} historical cost records")

    async def start_monitoring(self) -> None:
        """Start continuous cost monitoring and optimization."""
        if self._monitoring_active:
            self.logger.warning("Cost monitoring already active")
            return

        self._monitoring_active = True
        self.logger.info("Started cost monitoring and optimization")

        # Start monitoring tasks
        asyncio.create_task(self._cost_analysis_loop())
        asyncio.create_task(self._budget_monitoring_loop())
        asyncio.create_task(self._optimization_analysis_loop())
        asyncio.create_task(self._data_cleanup_loop())

    async def stop_monitoring(self) -> None:
        """Stop cost monitoring."""
        self._monitoring_active = False
        self.logger.info("Stopped cost monitoring")

    async def _cost_analysis_loop(self) -> None:
        """Cost analysis and alerting loop."""
        while self._monitoring_active:
            try:
                await self._analyze_cost_trends()
                await self._detect_cost_anomalies()
                await asyncio.sleep(1800)  # Run every 30 minutes
            except Exception as e:
                self.logger.error(f"Cost analysis error: {e}")
                await asyncio.sleep(300)

    async def _budget_monitoring_loop(self) -> None:
        """Budget monitoring loop."""
        while self._monitoring_active:
            try:
                await self._update_budget_utilization()
                await self._check_budget_alerts()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.logger.error(f"Budget monitoring error: {e}")
                await asyncio.sleep(300)

    async def _optimization_analysis_loop(self) -> None:
        """Optimization analysis loop."""
        while self._monitoring_active:
            try:
                await self._analyze_optimization_opportunities()
                await asyncio.sleep(7200)  # Run every 2 hours
            except Exception as e:
                self.logger.error(f"Optimization analysis error: {e}")
                await asyncio.sleep(600)

    async def _data_cleanup_loop(self) -> None:
        """Data cleanup loop."""
        while self._monitoring_active:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(86400)  # Run daily
            except Exception as e:
                self.logger.error(f"Data cleanup error: {e}")
                await asyncio.sleep(3600)

    async def record_cost(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        resource_id: str,
        cost_amount: float,
        usage_quantity: float = 0.0,
        usage_unit: str = "",
        region: str = "",
        tags: dict[str, str] = None,
    ) -> CostRecord:
        """Record a cost entry.

        Args:
            tenant_id: Tenant identifier
            resource_type: Type of resource
            resource_id: Resource identifier
            cost_amount: Cost amount in dollars
            usage_quantity: Quantity of resource used
            usage_unit: Unit of measurement
            region: Geographic region
            tags: Additional metadata tags

        Returns:
            Created cost record
        """
        record_id = f"cost_{tenant_id}_{resource_id}_{int(datetime.utcnow().timestamp())}"

        record = CostRecord(
            record_id=record_id,
            timestamp=datetime.utcnow(),
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            cost_amount=cost_amount,
            usage_quantity=usage_quantity,
            usage_unit=usage_unit,
            region=region,
            tags=tags or {},
        )

        self._cost_records.append(record)

        # Update budgets
        await self._update_budget_spending(record)

        self.logger.debug(f"Recorded cost: {cost_amount} for {resource_id}")
        return record

    async def _update_budget_spending(self, record: CostRecord) -> None:
        """Update budget spending with new cost record.

        Args:
            record: Cost record to apply to budgets
        """
        for budget in self._budgets.values():
            # Check if record applies to this budget
            applies = True

            # Check tenant filter
            if budget.tenant_id and budget.tenant_id != record.tenant_id:
                applies = False

            # Check category filter
            if budget.categories and record.category not in budget.categories:
                applies = False

            # Check date range
            if budget.end_date and record.timestamp > budget.end_date:
                applies = False

            if applies:
                budget.spent_amount += record.cost_amount

    async def _analyze_cost_trends(self) -> None:
        """Analyze cost trends and patterns."""
        # Analyze costs by tenant, resource type, and time
        now = datetime.utcnow()
        last_7_days = [
            record for record in self._cost_records if (now - record.timestamp).days <= 7
        ]

        if not last_7_days:
            return

        # Calculate daily costs
        daily_costs = defaultdict(float)
        for record in last_7_days:
            date_key = record.timestamp.date()
            daily_costs[date_key] += record.cost_amount

        # Check for significant cost increases
        if len(daily_costs) >= 3:
            costs = list(daily_costs.values())
            avg_cost = statistics.mean(costs)
            latest_cost = costs[-1]

            if latest_cost > avg_cost * 1.5:  # 50% increase
                alert = {
                    "type": "cost_spike",
                    "message": f"Daily cost spike detected: ${latest_cost:.2f} vs avg ${avg_cost:.2f}",
                    "timestamp": now.isoformat(),
                    "severity": "warning",
                }
                self._cost_alerts.append(alert)
                self.logger.warning(alert["message"])

    async def _detect_cost_anomalies(self) -> None:
        """Detect cost anomalies using statistical analysis."""
        # Analyze costs by tenant for anomalies
        tenant_costs = defaultdict(list)
        last_30_days = datetime.utcnow() - timedelta(days=30)

        for record in self._cost_records:
            if record.timestamp >= last_30_days:
                tenant_costs[record.tenant_id].append(record.cost_amount)

        for tenant_id, costs in tenant_costs.items():
            if len(costs) >= 10:  # Need enough data points
                mean_cost = statistics.mean(costs)
                std_cost = statistics.stdev(costs)

                # Check for outliers (costs > 2 standard deviations from mean)
                recent_costs = costs[-5:]  # Last 5 cost entries
                for cost in recent_costs:
                    if cost > mean_cost + 2 * std_cost:
                        alert = {
                            "type": "cost_anomaly",
                            "message": f"Cost anomaly for {tenant_id}: ${cost:.2f} (mean: ${mean_cost:.2f})",
                            "timestamp": datetime.utcnow().isoformat(),
                            "severity": "warning",
                            "tenant_id": tenant_id,
                        }
                        self._cost_alerts.append(alert)
                        self.logger.warning(alert["message"])

    async def _update_budget_utilization(self) -> None:
        """Update budget utilization calculations."""
        current_time = datetime.utcnow()

        for budget in self._budgets.values():
            # Reset spent amount and recalculate from records
            budget.spent_amount = 0.0

            applicable_records = []
            for record in self._cost_records:
                # Check if record applies to this budget
                if budget.tenant_id and budget.tenant_id != record.tenant_id:
                    continue

                if budget.categories and record.category not in budget.categories:
                    continue

                if record.timestamp < budget.start_date:
                    continue

                if budget.end_date and record.timestamp > budget.end_date:
                    continue

                applicable_records.append(record)

            budget.spent_amount = sum(record.cost_amount for record in applicable_records)

    async def _check_budget_alerts(self) -> None:
        """Check budget utilization and generate alerts."""
        for budget in self._budgets.values():
            utilization = budget.utilization_percentage

            # Check alert thresholds
            for threshold in budget.alerts:
                if utilization >= threshold:
                    # Check if we've already alerted for this threshold recently
                    recent_alerts = [
                        alert
                        for alert in self._cost_alerts
                        if (
                            alert.get("budget_id") == budget.budget_id
                            and alert.get("threshold") == threshold
                            and (
                                datetime.utcnow() - datetime.fromisoformat(alert["timestamp"])
                            ).hours
                            < 6
                        )
                    ]

                    if not recent_alerts:
                        severity = (
                            "critical"
                            if threshold >= 90
                            else ("warning" if threshold >= 75 else "info")
                        )

                        alert = {
                            "type": "budget_alert",
                            "message": f"Budget {budget.name} is {utilization:.1f}% utilized (${budget.spent_amount:.2f}/${budget.amount:.2f})",
                            "timestamp": datetime.utcnow().isoformat(),
                            "severity": severity,
                            "budget_id": budget.budget_id,
                            "threshold": threshold,
                            "utilization": utilization,
                        }

                        self._cost_alerts.append(alert)
                        self.logger.warning(alert["message"])

    async def update_resource_metrics(
        self,
        resource_id: str,
        resource_type: ResourceType,
        tenant_id: str,
        cpu_utilization: float = 0.0,
        memory_utilization: float = 0.0,
        storage_utilization: float = 0.0,
        idle_time_percentage: float = 0.0,
    ) -> None:
        """Update resource usage metrics for optimization analysis.

        Args:
            resource_id: Resource identifier
            resource_type: Type of resource
            tenant_id: Tenant owning the resource
            cpu_utilization: CPU utilization percentage
            memory_utilization: Memory utilization percentage
            storage_utilization: Storage utilization percentage
            idle_time_percentage: Idle time percentage
        """
        if resource_id not in self._resource_metrics:
            self._resource_metrics[resource_id] = ResourceUsageMetrics(
                resource_id=resource_id, resource_type=resource_type, tenant_id=tenant_id
            )

        metrics = self._resource_metrics[resource_id]

        # Update with exponential moving average for smoothing
        alpha = 0.3  # Smoothing factor
        metrics.avg_cpu_utilization = (
            alpha * cpu_utilization + (1 - alpha) * metrics.avg_cpu_utilization
        )
        metrics.avg_memory_utilization = (
            alpha * memory_utilization + (1 - alpha) * metrics.avg_memory_utilization
        )
        metrics.avg_storage_utilization = (
            alpha * storage_utilization + (1 - alpha) * metrics.avg_storage_utilization
        )
        metrics.idle_time_percentage = (
            alpha * idle_time_percentage + (1 - alpha) * metrics.idle_time_percentage
        )

        # Update peak utilization
        current_peak = max(cpu_utilization, memory_utilization, storage_utilization)
        metrics.peak_utilization = max(metrics.peak_utilization, current_peak)

        metrics.last_updated = datetime.utcnow()

    async def _analyze_optimization_opportunities(self) -> None:
        """Analyze and generate optimization recommendations."""
        await self._analyze_underutilized_resources()
        await self._analyze_overutilized_resources()
        await self._analyze_storage_optimization()
        await self._analyze_regional_optimization()
        await self._analyze_schedule_based_optimization()

    async def _analyze_underutilized_resources(self) -> None:
        """Analyze underutilized resources for right-sizing opportunities."""
        for resource_id, metrics in self._resource_metrics.items():
            if metrics.is_underutilized and metrics.cost_per_hour > 0:
                # Calculate potential savings from right-sizing
                potential_savings_hourly = metrics.waste_cost_per_hour
                potential_savings_monthly = potential_savings_hourly * 24 * 30

                if potential_savings_monthly > 50:  # Minimum threshold for recommendation
                    recommendation_id = (
                        f"rightsize_{resource_id}_{int(datetime.utcnow().timestamp())}"
                    )

                    recommendation = OptimizationRecommendation(
                        recommendation_id=recommendation_id,
                        type=OptimizationType.RIGHT_SIZE,
                        title=f"Right-size underutilized resource {resource_id}",
                        description=f"Resource {resource_id} is underutilized with {metrics.avg_cpu_utilization:.1f}% avg CPU and {metrics.idle_time_percentage:.1f}% idle time. Consider downsizing.",
                        tenant_id=metrics.tenant_id,
                        resource_ids=[resource_id],
                        estimated_savings_monthly=potential_savings_monthly,
                        estimated_savings_annual=potential_savings_monthly * 12,
                        implementation_effort="low",
                        risk_level="low",
                        implementation_steps=[
                            "Analyze historical usage patterns",
                            "Identify appropriate smaller instance size",
                            "Schedule maintenance window",
                            "Resize instance",
                            "Monitor performance post-resize",
                        ],
                        expires_at=datetime.utcnow() + timedelta(days=7),
                    )

                    self._recommendations[recommendation_id] = recommendation
                    self.logger.info(f"Generated right-sizing recommendation: {recommendation_id}")

    async def _analyze_overutilized_resources(self) -> None:
        """Analyze overutilized resources that may need scaling up."""
        for resource_id, metrics in self._resource_metrics.items():
            if metrics.is_overutilized:
                recommendation_id = f"scaleup_{resource_id}_{int(datetime.utcnow().timestamp())}"

                recommendation = OptimizationRecommendation(
                    recommendation_id=recommendation_id,
                    type=OptimizationType.RIGHT_SIZE,
                    title=f"Scale up overutilized resource {resource_id}",
                    description=f"Resource {resource_id} is overutilized with {metrics.peak_utilization:.1f}% peak utilization. Consider scaling up to avoid performance issues.",
                    tenant_id=metrics.tenant_id,
                    resource_ids=[resource_id],
                    estimated_savings_monthly=0.0,  # This is more about performance than cost savings
                    estimated_savings_annual=0.0,
                    implementation_effort="medium",
                    risk_level="low",
                    implementation_steps=[
                        "Identify appropriate larger instance size",
                        "Estimate additional costs",
                        "Schedule maintenance window",
                        "Scale up instance",
                        "Monitor performance improvement",
                    ],
                    expires_at=datetime.utcnow() + timedelta(days=3),  # More urgent
                )

                self._recommendations[recommendation_id] = recommendation
                self.logger.info(f"Generated scale-up recommendation: {recommendation_id}")

    async def _analyze_storage_optimization(self) -> None:
        """Analyze storage optimization opportunities."""
        # Group storage costs by tenant
        storage_costs = defaultdict(float)
        last_30_days = datetime.utcnow() - timedelta(days=30)

        for record in self._cost_records:
            if record.resource_type == ResourceType.STORAGE and record.timestamp >= last_30_days:
                storage_costs[record.tenant_id] += record.cost_amount

        for tenant_id, monthly_cost in storage_costs.items():
            if monthly_cost > 500:  # Significant storage costs
                # Assume 30% savings potential through tiering
                potential_savings = monthly_cost * 0.30

                recommendation_id = f"storage_tier_{tenant_id}_{int(datetime.utcnow().timestamp())}"

                recommendation = OptimizationRecommendation(
                    recommendation_id=recommendation_id,
                    type=OptimizationType.STORAGE_TIERING,
                    title=f"Implement storage tiering for {tenant_id}",
                    description=f"Tenant {tenant_id} has ${monthly_cost:.2f} in monthly storage costs. Implementing storage tiering could reduce costs by moving infrequently accessed data to cheaper storage tiers.",
                    tenant_id=tenant_id,
                    estimated_savings_monthly=potential_savings,
                    estimated_savings_annual=potential_savings * 12,
                    implementation_effort="medium",
                    risk_level="low",
                    prerequisites=["Analyze data access patterns", "Identify rarely accessed data"],
                    implementation_steps=[
                        "Audit current storage usage",
                        "Identify data access patterns",
                        "Configure automated tiering policies",
                        "Migrate appropriate data to lower-cost tiers",
                        "Monitor cost savings",
                    ],
                    expires_at=datetime.utcnow() + timedelta(days=14),
                )

                self._recommendations[recommendation_id] = recommendation
                self.logger.info(f"Generated storage tiering recommendation: {recommendation_id}")

    async def _analyze_regional_optimization(self) -> None:
        """Analyze regional cost optimization opportunities."""
        # Analyze costs by region
        regional_costs = defaultdict(float)
        last_30_days = datetime.utcnow() - timedelta(days=30)

        for record in self._cost_records:
            if record.timestamp >= last_30_days and record.region:
                regional_costs[record.region] += record.cost_amount

        # Look for opportunities to move workloads to cheaper regions
        if len(regional_costs) > 1:
            regions_by_cost = sorted(regional_costs.items(), key=lambda x: x[1], reverse=True)
            most_expensive = regions_by_cost[0]
            least_expensive = regions_by_cost[-1]

            # If there's a significant cost difference, recommend moving some workloads
            cost_difference = most_expensive[1] - least_expensive[1]
            if cost_difference > 1000:  # $1000+ difference
                potential_savings = cost_difference * 0.4  # Assume 40% could be moved

                recommendation_id = f"region_opt_{int(datetime.utcnow().timestamp())}"

                recommendation = OptimizationRecommendation(
                    recommendation_id=recommendation_id,
                    type=OptimizationType.REGION_OPTIMIZATION,
                    title="Consider regional optimization",
                    description=f"Significant cost difference between regions. Consider moving some workloads from {most_expensive[0]} (${most_expensive[1]:.2f}) to {least_expensive[0]} (${least_expensive[1]:.2f}).",
                    estimated_savings_monthly=potential_savings,
                    estimated_savings_annual=potential_savings * 12,
                    implementation_effort="high",
                    risk_level="medium",
                    prerequisites=[
                        "Analyze latency requirements",
                        "Check compliance requirements",
                        "Assess data transfer costs",
                    ],
                    implementation_steps=[
                        "Identify workloads suitable for relocation",
                        "Assess latency and compliance impacts",
                        "Plan migration strategy",
                        "Execute phased migration",
                        "Monitor performance and costs",
                    ],
                    expires_at=datetime.utcnow() + timedelta(days=30),
                )

                self._recommendations[recommendation_id] = recommendation
                self.logger.info(
                    f"Generated regional optimization recommendation: {recommendation_id}"
                )

    async def _analyze_schedule_based_optimization(self) -> None:
        """Analyze schedule-based optimization opportunities."""
        # Look for resources that could benefit from scheduled scaling
        for resource_id, metrics in self._resource_metrics.items():
            if metrics.resource_type == ResourceType.COMPUTE and metrics.cost_per_hour > 1.0:
                # In production, would analyze hourly usage patterns
                # For simulation, assume 30% of compute could be scheduled off-hours
                potential_savings = metrics.cost_per_hour * 24 * 30 * 0.30

                if potential_savings > 100:  # Minimum threshold
                    recommendation_id = (
                        f"schedule_{resource_id}_{int(datetime.utcnow().timestamp())}"
                    )

                    recommendation = OptimizationRecommendation(
                        recommendation_id=recommendation_id,
                        type=OptimizationType.SCHEDULE_BASED,
                        title=f"Implement scheduled scaling for {resource_id}",
                        description=f"Resource {resource_id} could benefit from scheduled scaling based on usage patterns. Consider automatically stopping/starting during off-hours.",
                        tenant_id=metrics.tenant_id,
                        resource_ids=[resource_id],
                        estimated_savings_monthly=potential_savings,
                        estimated_savings_annual=potential_savings * 12,
                        implementation_effort="medium",
                        risk_level="medium",
                        prerequisites=[
                            "Analyze usage patterns",
                            "Identify non-critical time windows",
                        ],
                        implementation_steps=[
                            "Analyze historical usage patterns",
                            "Define scaling schedule",
                            "Implement automated scaling",
                            "Test scaling behavior",
                            "Monitor cost savings",
                        ],
                        expires_at=datetime.utcnow() + timedelta(days=10),
                    )

                    self._recommendations[recommendation_id] = recommendation
                    self.logger.info(
                        f"Generated schedule-based optimization recommendation: {recommendation_id}"
                    )

    async def _cleanup_old_data(self) -> None:
        """Clean up old cost data and recommendations."""
        # Clean up cost records older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        initial_count = len(self._cost_records)

        self._cost_records = [
            record for record in self._cost_records if record.timestamp >= cutoff_date
        ]

        cleaned_records = initial_count - len(self._cost_records)

        # Clean up expired recommendations
        expired_recommendations = [
            rec_id for rec_id, rec in self._recommendations.items() if rec.is_expired
        ]

        for rec_id in expired_recommendations:
            del self._recommendations[rec_id]

        if cleaned_records > 0 or expired_recommendations:
            self.logger.info(
                f"Cleaned up {cleaned_records} old cost records and {len(expired_recommendations)} expired recommendations"
            )

    async def create_budget(
        self,
        name: str,
        amount: float,
        period: str = "monthly",
        tenant_id: Optional[str] = None,
        categories: set[CostCategory] = None,
    ) -> Budget:
        """Create a new budget.

        Args:
            name: Budget name
            amount: Budget amount
            period: Budget period
            tenant_id: Tenant this budget applies to
            categories: Cost categories to include

        Returns:
            Created budget
        """
        budget_id = f"budget_{int(datetime.utcnow().timestamp())}_{hash(name) % 10000}"

        # Calculate end date based on period
        start_date = datetime.utcnow()
        if period == "monthly":
            end_date = start_date + timedelta(days=30)
        elif period == "quarterly":
            end_date = start_date + timedelta(days=90)
        elif period == "annual":
            end_date = start_date + timedelta(days=365)
        else:
            end_date = start_date + timedelta(days=30)

        budget = Budget(
            budget_id=budget_id,
            name=name,
            description=f"Budget: {name}",
            amount=amount,
            period=period,
            start_date=start_date,
            end_date=end_date,
            tenant_id=tenant_id,
            categories=categories or set(),
        )

        self._budgets[budget_id] = budget

        self.logger.info(f"Created budget: {name} (${amount}) for {period}")
        return budget

    async def get_cost_summary(
        self, tenant_id: Optional[str] = None, days: int = 30
    ) -> dict[str, Any]:
        """Get cost summary for a tenant or globally.

        Args:
            tenant_id: Tenant to get summary for (None for global)
            days: Number of days to include

        Returns:
            Cost summary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Filter records
        records = [
            record
            for record in self._cost_records
            if (
                record.timestamp >= cutoff_date
                and (tenant_id is None or record.tenant_id == tenant_id)
            )
        ]

        if not records:
            return {
                "total_cost": 0.0,
                "record_count": 0,
                "by_resource_type": {},
                "by_day": {},
                "top_resources": [],
            }

        # Calculate totals
        total_cost = sum(record.cost_amount for record in records)

        # Group by resource type
        by_resource_type = defaultdict(float)
        for record in records:
            by_resource_type[record.resource_type.value] += record.cost_amount

        # Group by day
        by_day = defaultdict(float)
        for record in records:
            day_key = record.timestamp.date().isoformat()
            by_day[day_key] += record.cost_amount

        # Top resources by cost
        resource_costs = defaultdict(float)
        for record in records:
            resource_costs[record.resource_id] += record.cost_amount

        top_resources = sorted(resource_costs.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "tenant_id": tenant_id,
            "period_days": days,
            "total_cost": total_cost,
            "average_daily_cost": total_cost / days if days > 0 else 0,
            "record_count": len(records),
            "by_resource_type": dict(by_resource_type),
            "by_day": dict(by_day),
            "top_resources": [
                {"resource_id": resource_id, "cost": cost} for resource_id, cost in top_resources
            ],
        }

    async def get_cost_status(self) -> dict[str, Any]:
        """Get comprehensive cost optimization status.

        Returns:
            Cost status and metrics
        """
        # Calculate recent costs
        last_30_days = datetime.utcnow() - timedelta(days=30)
        recent_records = [r for r in self._cost_records if r.timestamp >= last_30_days]
        total_monthly_cost = sum(r.cost_amount for r in recent_records)

        # Budget status
        budget_statuses = {}
        total_budget_amount = 0
        total_budget_spent = 0

        for budget in self._budgets.values():
            budget_statuses[budget.budget_id] = {
                "name": budget.name,
                "amount": budget.amount,
                "spent": budget.spent_amount,
                "utilization": budget.utilization_percentage,
                "status": budget.status.value,
                "days_remaining": budget.days_remaining,
            }
            total_budget_amount += budget.amount
            total_budget_spent += budget.spent_amount

        # Recommendations summary
        active_recommendations = [r for r in self._recommendations.values() if not r.is_expired]
        total_potential_savings = sum(r.estimated_savings_monthly for r in active_recommendations)

        # Resource metrics summary
        underutilized_resources = sum(
            1 for m in self._resource_metrics.values() if m.is_underutilized
        )
        overutilized_resources = sum(
            1 for m in self._resource_metrics.values() if m.is_overutilized
        )

        return {
            "monitoring_active": self._monitoring_active,
            "costs": {
                "monthly_total": total_monthly_cost,
                "daily_average": total_monthly_cost / 30,
                "record_count": len(recent_records),
            },
            "budgets": {
                "total_amount": total_budget_amount,
                "total_spent": total_budget_spent,
                "overall_utilization": (total_budget_spent / total_budget_amount * 100)
                if total_budget_amount > 0
                else 0,
                "budget_count": len(self._budgets),
                "budget_details": budget_statuses,
            },
            "optimization": {
                "active_recommendations": len(active_recommendations),
                "potential_monthly_savings": total_potential_savings,
                "potential_annual_savings": total_potential_savings * 12,
                "underutilized_resources": underutilized_resources,
                "overutilized_resources": overutilized_resources,
            },
            "alerts": {
                "recent_count": len(
                    [
                        a
                        for a in self._cost_alerts
                        if (datetime.utcnow() - datetime.fromisoformat(a["timestamp"])).days <= 1
                    ]
                ),
                "total_count": len(self._cost_alerts),
            },
            "last_updated": datetime.utcnow().isoformat(),
        }

    def get_recommendations(
        self, tenant_id: Optional[str] = None, optimization_type: Optional[OptimizationType] = None
    ) -> list[dict[str, Any]]:
        """Get optimization recommendations.

        Args:
            tenant_id: Filter by tenant
            optimization_type: Filter by optimization type

        Returns:
            List of recommendations
        """
        recommendations = list(self._recommendations.values())

        # Filter by tenant
        if tenant_id:
            recommendations = [r for r in recommendations if r.tenant_id == tenant_id]

        # Filter by type
        if optimization_type:
            recommendations = [r for r in recommendations if r.type == optimization_type]

        # Filter out expired
        recommendations = [r for r in recommendations if not r.is_expired]

        # Sort by potential savings
        recommendations.sort(key=lambda r: r.estimated_savings_monthly, reverse=True)

        return [r.to_dict() for r in recommendations]

    def get_budget(self, budget_id: str) -> Optional[dict[str, Any]]:
        """Get budget information.

        Args:
            budget_id: Budget ID

        Returns:
            Budget information or None if not found
        """
        budget = self._budgets.get(budget_id)
        if not budget:
            return None

        return {
            "budget_id": budget.budget_id,
            "name": budget.name,
            "description": budget.description,
            "amount": budget.amount,
            "spent_amount": budget.spent_amount,
            "remaining_amount": budget.remaining_amount,
            "utilization_percentage": budget.utilization_percentage,
            "status": budget.status.value,
            "period": budget.period,
            "start_date": budget.start_date.isoformat(),
            "end_date": budget.end_date.isoformat() if budget.end_date else None,
            "days_remaining": budget.days_remaining,
            "tenant_id": budget.tenant_id,
            "categories": [cat.value for cat in budget.categories],
            "alerts": budget.alerts,
        }
