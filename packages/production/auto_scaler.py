"""
Intelligent auto-scaling system for T-Developer production environment.

This module provides predictive scaling based on patterns, cost-aware scaling
decisions, and comprehensive resource optimization for enterprise workloads.
"""

from __future__ import annotations

import asyncio
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, TypedDict, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from collections import deque, defaultdict


class ScalingDirection(Enum):
    """Direction of scaling operations."""
    UP = "scale_up"
    DOWN = "scale_down"
    STEADY = "steady"


class ScalingPolicy(Enum):
    """Scaling policy types."""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    HYBRID = "hybrid"


class ResourceMetric(Enum):
    """Types of resource metrics for scaling decisions."""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    ERROR_RATE = "error_rate"
    CUSTOM = "custom"


class ScalingTrigger(Enum):
    """Types of scaling triggers."""
    THRESHOLD = "threshold"
    TREND = "trend"
    SCHEDULE = "schedule"
    PREDICTION = "prediction"
    COST_OPTIMIZATION = "cost_optimization"


@dataclass
class MetricThreshold:
    """Threshold configuration for metrics.
    
    Attributes:
        metric: Type of metric to monitor
        scale_up_threshold: Value above which to scale up
        scale_down_threshold: Value below which to scale down
        evaluation_periods: Number of periods to evaluate
        breach_duration_seconds: How long threshold must be breached
        cooldown_seconds: Minimum time between scaling actions
    """
    metric: ResourceMetric
    scale_up_threshold: float
    scale_down_threshold: float
    evaluation_periods: int = 3
    breach_duration_seconds: int = 300  # 5 minutes
    cooldown_seconds: int = 600  # 10 minutes
    
    def is_scale_up_triggered(self, values: List[float], 
                            now: datetime) -> bool:
        """Check if scale up should be triggered."""
        if len(values) < self.evaluation_periods:
            return False
        return all(v > self.scale_up_threshold for v in values[-self.evaluation_periods:])
        
    def is_scale_down_triggered(self, values: List[float],
                              now: datetime) -> bool:
        """Check if scale down should be triggered."""
        if len(values) < self.evaluation_periods:
            return False
        return all(v < self.scale_down_threshold for v in values[-self.evaluation_periods:])


@dataclass
class PredictionModel:
    """Predictive model for forecasting resource needs.
    
    Attributes:
        model_type: Type of prediction model
        accuracy: Model accuracy percentage
        prediction_horizon_minutes: How far ahead to predict
        training_data_points: Number of data points used for training
        last_trained: When model was last trained
        model_parameters: Model-specific parameters
    """
    model_type: str
    accuracy: float = 0.0
    prediction_horizon_minutes: int = 30
    training_data_points: int = 1000
    last_trained: Optional[datetime] = None
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    
    def predict(self, historical_data: List[float], 
               future_timestamps: List[datetime]) -> List[float]:
        """Generate predictions for future timestamps.
        
        Args:
            historical_data: Historical metric values
            future_timestamps: Future times to predict for
            
        Returns:
            Predicted values for each timestamp
        """
        if not historical_data:
            return [0.0] * len(future_timestamps)
            
        # Simple linear trend prediction for demonstration
        if len(historical_data) < 2:
            return [historical_data[-1]] * len(future_timestamps)
            
        # Calculate trend
        x_values = list(range(len(historical_data)))
        y_values = historical_data
        
        # Simple linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Generate predictions
        predictions = []
        for i, _ in enumerate(future_timestamps):
            future_x = len(historical_data) + i
            prediction = slope * future_x + intercept
            predictions.append(max(0, prediction))  # No negative predictions
            
        return predictions


@dataclass
class ScalingAction:
    """Record of a scaling action taken.
    
    Attributes:
        action_id: Unique identifier for the action
        timestamp: When action was taken
        direction: Direction of scaling
        trigger: What triggered the scaling
        resource_type: Type of resource scaled
        from_count: Previous resource count
        to_count: New resource count
        reason: Human-readable reason for scaling
        cost_impact: Estimated cost impact
        success: Whether action was successful
        duration_seconds: How long action took
    """
    action_id: str
    timestamp: datetime
    direction: ScalingDirection
    trigger: ScalingTrigger
    resource_type: str
    from_count: int
    to_count: int
    reason: str
    cost_impact: float = 0.0
    success: bool = True
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingTarget:
    """Definition of a resource that can be scaled.
    
    Attributes:
        target_id: Unique identifier for scaling target
        name: Human-readable name
        resource_type: Type of resource (pods, instances, etc.)
        current_count: Current number of resources
        min_count: Minimum allowed count
        max_count: Maximum allowed count
        thresholds: Metric thresholds for scaling
        scaling_policy: Policy for scaling decisions
        cost_per_unit: Cost per resource unit per hour
        tags: Additional metadata tags
    """
    target_id: str
    name: str
    resource_type: str
    current_count: int
    min_count: int = 1
    max_count: int = 100
    thresholds: List[MetricThreshold] = field(default_factory=list)
    scaling_policy: ScalingPolicy = ScalingPolicy.REACTIVE
    cost_per_unit: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)
    last_scaled: Optional[datetime] = None
    
    def can_scale_up(self) -> bool:
        """Check if target can be scaled up."""
        return self.current_count < self.max_count
        
    def can_scale_down(self) -> bool:
        """Check if target can be scaled down."""
        return self.current_count > self.min_count
        
    def is_in_cooldown(self, cooldown_seconds: int = 600) -> bool:
        """Check if target is in cooldown period."""
        if not self.last_scaled:
            return False
        return (datetime.utcnow() - self.last_scaled).total_seconds() < cooldown_seconds


class AutoScaler:
    """Intelligent auto-scaling system for T-Developer.
    
    Provides predictive scaling, cost optimization, and comprehensive
    resource management for production workloads.
    
    Example:
        >>> scaler = AutoScaler()
        >>> await scaler.initialize()
        >>> target = ScalingTarget("web-servers", "Web Servers", "pods", 3)
        >>> await scaler.register_target(target)
        >>> await scaler.start_monitoring()
    """
    
    def __init__(self, config: Dict[str, Any] = None) -> None:
        """Initialize auto-scaler.
        
        Args:
            config: Scaler configuration options
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._targets: Dict[str, ScalingTarget] = {}
        self._metrics_history: Dict[str, Dict[ResourceMetric, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=1000))
        )
        self._scaling_actions: List[ScalingAction] = []
        self._prediction_models: Dict[str, Dict[ResourceMetric, PredictionModel]] = defaultdict(dict)
        self._cost_calculator: Optional[Callable] = None
        self._monitoring_active = False
        self._evaluation_interval = 60  # seconds
        self._max_scaling_velocity = 0.5  # Max 50% change per scaling action
        
    async def initialize(self) -> None:
        """Initialize the auto-scaler.
        
        Sets up prediction models, cost calculators, and monitoring.
        """
        self.logger.info("Initializing auto-scaler")
        
        await self._setup_prediction_models()
        await self._setup_cost_calculator()
        await self._load_scaling_history()
        
        self.logger.info("Auto-scaler initialized successfully")
        
    async def _setup_prediction_models(self) -> None:
        """Set up prediction models for different metrics."""
        model_configs = {
            ResourceMetric.CPU_UTILIZATION: {
                "model_type": "linear_trend",
                "prediction_horizon_minutes": 30
            },
            ResourceMetric.MEMORY_UTILIZATION: {
                "model_type": "exponential_smoothing",
                "prediction_horizon_minutes": 20
            },
            ResourceMetric.REQUEST_RATE: {
                "model_type": "seasonal_arima",
                "prediction_horizon_minutes": 60
            }
        }
        
        for metric, config in model_configs.items():
            model = PredictionModel(
                model_type=config["model_type"],
                prediction_horizon_minutes=config["prediction_horizon_minutes"]
            )
            # Store as default model for all targets
            self._prediction_models["default"][metric] = model
            
        self.logger.info("Prediction models initialized")
        
    async def _setup_cost_calculator(self) -> None:
        """Set up cost calculation functionality."""
        # In production, integrate with cloud provider pricing APIs
        def simple_cost_calculator(resource_type: str, count: int, duration_hours: float) -> float:
            # Simple cost model - in production, use actual pricing
            base_costs = {
                "pods": 0.05,  # $0.05 per pod per hour
                "instances": 0.20,  # $0.20 per instance per hour
                "containers": 0.02  # $0.02 per container per hour
            }
            return base_costs.get(resource_type, 0.10) * count * duration_hours
            
        self._cost_calculator = simple_cost_calculator
        self.logger.info("Cost calculator initialized")
        
    async def _load_scaling_history(self) -> None:
        """Load historical scaling actions."""
        # In production, load from persistent storage
        self.logger.info("Loaded scaling history")
        
    async def register_target(self, target: ScalingTarget) -> None:
        """Register a new scaling target.
        
        Args:
            target: Scaling target to register
            
        Raises:
            ValueError: If target already exists or is invalid
        """
        if target.target_id in self._targets:
            raise ValueError(f"Target {target.target_id} already registered")
            
        if target.min_count >= target.max_count:
            raise ValueError("min_count must be less than max_count")
            
        if target.current_count < target.min_count or target.current_count > target.max_count:
            raise ValueError("current_count must be between min_count and max_count")
            
        # Set up default thresholds if none provided
        if not target.thresholds:
            target.thresholds = self._create_default_thresholds()
            
        # Initialize metrics history
        for metric in ResourceMetric:
            self._metrics_history[target.target_id][metric] = deque(maxlen=1000)
            
        # Set up prediction models for this target
        if target.target_id not in self._prediction_models:
            self._prediction_models[target.target_id] = {}
            for metric in [ResourceMetric.CPU_UTILIZATION, ResourceMetric.MEMORY_UTILIZATION, 
                          ResourceMetric.REQUEST_RATE]:
                self._prediction_models[target.target_id][metric] = PredictionModel(
                    model_type="linear_trend",
                    prediction_horizon_minutes=30
                )
                
        self._targets[target.target_id] = target
        
        self.logger.info(f"Registered scaling target: {target.target_id}")
        
    def _create_default_thresholds(self) -> List[MetricThreshold]:
        """Create default metric thresholds."""
        return [
            MetricThreshold(
                metric=ResourceMetric.CPU_UTILIZATION,
                scale_up_threshold=70.0,
                scale_down_threshold=30.0,
                evaluation_periods=3,
                breach_duration_seconds=300,
                cooldown_seconds=600
            ),
            MetricThreshold(
                metric=ResourceMetric.MEMORY_UTILIZATION,
                scale_up_threshold=80.0,
                scale_down_threshold=40.0,
                evaluation_periods=3,
                breach_duration_seconds=300,
                cooldown_seconds=600
            ),
            MetricThreshold(
                metric=ResourceMetric.REQUEST_RATE,
                scale_up_threshold=1000.0,  # requests per minute
                scale_down_threshold=200.0,
                evaluation_periods=2,
                breach_duration_seconds=180,
                cooldown_seconds=300
            )
        ]
        
    async def start_monitoring(self) -> None:
        """Start continuous monitoring and scaling."""
        if self._monitoring_active:
            self.logger.warning("Monitoring already active")
            return
            
        self._monitoring_active = True
        self.logger.info("Started auto-scaling monitoring")
        
        # Start monitoring tasks
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._prediction_loop())
        asyncio.create_task(self._cost_optimization_loop())
        
    async def stop_monitoring(self) -> None:
        """Stop monitoring and scaling."""
        self._monitoring_active = False
        self.logger.info("Stopped auto-scaling monitoring")
        
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring_active:
            try:
                await self._collect_metrics()
                await self._evaluate_scaling_decisions()
                await asyncio.sleep(self._evaluation_interval)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)  # Short retry delay
                
    async def _prediction_loop(self) -> None:
        """Predictive scaling loop."""
        while self._monitoring_active:
            try:
                await self._update_prediction_models()
                await self._evaluate_predictive_scaling()
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Prediction loop error: {e}")
                await asyncio.sleep(60)
                
    async def _cost_optimization_loop(self) -> None:
        """Cost optimization loop."""
        while self._monitoring_active:
            try:
                await self._evaluate_cost_optimizations()
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"Cost optimization loop error: {e}")
                await asyncio.sleep(300)
                
    async def _collect_metrics(self) -> None:
        """Collect current metrics for all targets."""
        for target_id, target in self._targets.items():
            try:
                metrics = await self._fetch_target_metrics(target)
                
                # Store metrics in history
                for metric_type, value in metrics.items():
                    self._metrics_history[target_id][metric_type].append({
                        "timestamp": datetime.utcnow(),
                        "value": value
                    })
                    
            except Exception as e:
                self.logger.error(f"Failed to collect metrics for {target_id}: {e}")
                
    async def _fetch_target_metrics(self, target: ScalingTarget) -> Dict[ResourceMetric, float]:
        """Fetch current metrics for a target.
        
        Args:
            target: Target to fetch metrics for
            
        Returns:
            Dictionary of current metric values
        """
        # In production, fetch from monitoring systems like Prometheus, CloudWatch, etc.
        # For now, simulate metrics with some realistic patterns
        
        current_time = datetime.utcnow()
        hour = current_time.hour
        
        # Simulate daily traffic patterns
        traffic_multiplier = 0.5 + 0.5 * math.sin((hour - 6) * math.pi / 12)
        traffic_multiplier = max(0.2, min(1.5, traffic_multiplier))
        
        # Add some randomness
        import random
        noise = 1 + (random.random() - 0.5) * 0.2
        
        base_cpu = 40 * traffic_multiplier * noise
        base_memory = 50 * traffic_multiplier * noise
        base_requests = 500 * traffic_multiplier * noise
        
        return {
            ResourceMetric.CPU_UTILIZATION: min(100, base_cpu),
            ResourceMetric.MEMORY_UTILIZATION: min(100, base_memory),
            ResourceMetric.REQUEST_RATE: max(0, base_requests),
            ResourceMetric.RESPONSE_TIME: 100 + 50 * traffic_multiplier,
            ResourceMetric.ERROR_RATE: max(0, 1 * traffic_multiplier)
        }
        
    async def _evaluate_scaling_decisions(self) -> None:
        """Evaluate scaling decisions for all targets."""
        for target_id, target in self._targets.items():
            try:
                decision = await self._make_scaling_decision(target)
                
                if decision["action"] != ScalingDirection.STEADY:
                    await self._execute_scaling_action(target, decision)
                    
            except Exception as e:
                self.logger.error(f"Failed to evaluate scaling for {target_id}: {e}")
                
    async def _make_scaling_decision(self, target: ScalingTarget) -> Dict[str, Any]:
        """Make scaling decision for a target.
        
        Args:
            target: Target to make decision for
            
        Returns:
            Scaling decision with action and reasoning
        """
        decision = {
            "action": ScalingDirection.STEADY,
            "new_count": target.current_count,
            "reason": "No scaling needed",
            "trigger": None,
            "confidence": 0.0
        }
        
        # Check if in cooldown
        if target.is_in_cooldown():
            decision["reason"] = "In cooldown period"
            return decision
            
        # Get recent metric values
        recent_metrics = self._get_recent_metrics(target.target_id, minutes=10)
        
        # Evaluate each threshold
        for threshold in target.thresholds:
            metric_values = [m["value"] for m in recent_metrics.get(threshold.metric, [])]
            
            if not metric_values:
                continue
                
            # Check for scale up
            if threshold.is_scale_up_triggered(metric_values, datetime.utcnow()):
                if target.can_scale_up():
                    new_count = self._calculate_scale_up_count(target, threshold, metric_values)
                    decision = {
                        "action": ScalingDirection.UP,
                        "new_count": new_count,
                        "reason": f"{threshold.metric.value} above {threshold.scale_up_threshold}",
                        "trigger": ScalingTrigger.THRESHOLD,
                        "confidence": 0.8
                    }
                    break
                    
            # Check for scale down
            elif threshold.is_scale_down_triggered(metric_values, datetime.utcnow()):
                if target.can_scale_down():
                    new_count = self._calculate_scale_down_count(target, threshold, metric_values)
                    decision = {
                        "action": ScalingDirection.DOWN,
                        "new_count": new_count,
                        "reason": f"{threshold.metric.value} below {threshold.scale_down_threshold}",
                        "trigger": ScalingTrigger.THRESHOLD,
                        "confidence": 0.7
                    }
                    # Continue checking - prefer scale up over scale down
                    
        return decision
        
    def _get_recent_metrics(self, target_id: str, minutes: int = 10) -> Dict[ResourceMetric, List[Dict]]:
        """Get recent metrics for a target.
        
        Args:
            target_id: Target ID
            minutes: Number of minutes of history to retrieve
            
        Returns:
            Recent metrics organized by type
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = {}
        
        for metric_type, metric_history in self._metrics_history[target_id].items():
            recent = [
                m for m in metric_history 
                if m["timestamp"] >= cutoff_time
            ]
            recent_metrics[metric_type] = recent
            
        return recent_metrics
        
    def _calculate_scale_up_count(self, target: ScalingTarget, 
                                threshold: MetricThreshold,
                                metric_values: List[float]) -> int:
        """Calculate new count for scale up operation.
        
        Args:
            target: Scaling target
            threshold: Threshold that triggered scaling
            metric_values: Recent metric values
            
        Returns:
            New resource count
        """
        # Calculate scaling factor based on how much threshold is exceeded
        avg_value = statistics.mean(metric_values)
        excess_ratio = avg_value / threshold.scale_up_threshold
        
        # Conservative scaling - increase by 25-50% based on excess
        scale_factor = 1 + min(self._max_scaling_velocity, 0.25 + 0.25 * (excess_ratio - 1))
        
        new_count = math.ceil(target.current_count * scale_factor)
        return min(new_count, target.max_count)
        
    def _calculate_scale_down_count(self, target: ScalingTarget,
                                  threshold: MetricThreshold,
                                  metric_values: List[float]) -> int:
        """Calculate new count for scale down operation.
        
        Args:
            target: Scaling target
            threshold: Threshold that triggered scaling
            metric_values: Recent metric values
            
        Returns:
            New resource count
        """
        # Calculate scaling factor based on how much below threshold
        avg_value = statistics.mean(metric_values)
        under_ratio = avg_value / threshold.scale_down_threshold
        
        # Conservative scaling - decrease by 10-25% based on under-utilization
        scale_factor = 1 - min(self._max_scaling_velocity, 0.1 + 0.15 * (1 - under_ratio))
        
        new_count = math.floor(target.current_count * scale_factor)
        return max(new_count, target.min_count)
        
    async def _execute_scaling_action(self, target: ScalingTarget, 
                                    decision: Dict[str, Any]) -> None:
        """Execute a scaling action.
        
        Args:
            target: Target to scale
            decision: Scaling decision to execute
        """
        action_id = f"scale-{target.target_id}-{int(time.time())}"
        start_time = time.time()
        
        try:
            # Calculate cost impact
            old_cost = self._calculate_hourly_cost(target.resource_type, target.current_count)
            new_cost = self._calculate_hourly_cost(target.resource_type, decision["new_count"])
            cost_impact = new_cost - old_cost
            
            # Perform scaling
            success = await self._perform_scaling(target, decision["new_count"])
            
            # Record action
            action = ScalingAction(
                action_id=action_id,
                timestamp=datetime.utcnow(),
                direction=decision["action"],
                trigger=decision["trigger"],
                resource_type=target.resource_type,
                from_count=target.current_count,
                to_count=decision["new_count"],
                reason=decision["reason"],
                cost_impact=cost_impact,
                success=success,
                duration_seconds=time.time() - start_time
            )
            
            self._scaling_actions.append(action)
            
            if success:
                target.current_count = decision["new_count"]
                target.last_scaled = datetime.utcnow()
                
                self.logger.info(
                    f"Scaled {target.target_id} {decision['action'].value}: "
                    f"{action.from_count} -> {action.to_count} "
                    f"(cost impact: ${cost_impact:.2f}/hour)"
                )
            else:
                self.logger.error(f"Failed to scale {target.target_id}")
                
        except Exception as e:
            self.logger.error(f"Error executing scaling action for {target.target_id}: {e}")
            
    async def _perform_scaling(self, target: ScalingTarget, new_count: int) -> bool:
        """Perform the actual scaling operation.
        
        Args:
            target: Target to scale
            new_count: New resource count
            
        Returns:
            True if scaling was successful
        """
        # In production, this would call the appropriate scaling APIs:
        # - Kubernetes HPA/VPA
        # - AWS Auto Scaling Groups
        # - Azure VMSS
        # - Google Cloud Instance Groups
        
        # Simulate scaling operation
        await asyncio.sleep(2.0)  # Simulate scaling delay
        
        self.logger.debug(f"Scaled {target.target_id} to {new_count} {target.resource_type}")
        return True
        
    def _calculate_hourly_cost(self, resource_type: str, count: int) -> float:
        """Calculate hourly cost for resources.
        
        Args:
            resource_type: Type of resource
            count: Number of resources
            
        Returns:
            Hourly cost in dollars
        """
        if self._cost_calculator:
            return self._cost_calculator(resource_type, count, 1.0)
        return 0.0
        
    async def _update_prediction_models(self) -> None:
        """Update prediction models with recent data."""
        for target_id, target in self._targets.items():
            for metric_type, model in self._prediction_models.get(target_id, {}).items():
                try:
                    # Get historical data for training
                    historical_data = self._get_historical_metric_values(target_id, metric_type, hours=24)
                    
                    if len(historical_data) >= 10:  # Minimum data for training
                        model.last_trained = datetime.utcnow()
                        model.training_data_points = len(historical_data)
                        
                        # In production, train actual ML models
                        # For now, just update metadata
                        model.accuracy = min(95.0, 70.0 + len(historical_data) * 0.01)
                        
                except Exception as e:
                    self.logger.error(f"Failed to update prediction model for {target_id}/{metric_type}: {e}")
                    
    def _get_historical_metric_values(self, target_id: str, metric_type: ResourceMetric, hours: int = 24) -> List[float]:
        """Get historical metric values for training.
        
        Args:
            target_id: Target ID
            metric_type: Type of metric
            hours: Number of hours of history
            
        Returns:
            List of historical values
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        metric_history = self._metrics_history[target_id][metric_type]
        
        return [
            m["value"] for m in metric_history
            if m["timestamp"] >= cutoff_time
        ]
        
    async def _evaluate_predictive_scaling(self) -> None:
        """Evaluate predictive scaling opportunities."""
        for target_id, target in self._targets.items():
            if target.scaling_policy in [ScalingPolicy.PREDICTIVE, ScalingPolicy.HYBRID]:
                try:
                    await self._make_predictive_scaling_decision(target)
                except Exception as e:
                    self.logger.error(f"Predictive scaling error for {target_id}: {e}")
                    
    async def _make_predictive_scaling_decision(self, target: ScalingTarget) -> None:
        """Make predictive scaling decision for a target.
        
        Args:
            target: Target to make prediction for
        """
        # Get prediction models
        models = self._prediction_models.get(target.target_id, {})
        
        # Focus on CPU utilization for predictive scaling
        cpu_model = models.get(ResourceMetric.CPU_UTILIZATION)
        if not cpu_model or not cpu_model.last_trained:
            return
            
        # Get historical data
        historical_data = self._get_historical_metric_values(
            target.target_id, ResourceMetric.CPU_UTILIZATION, hours=6
        )
        
        if len(historical_data) < 10:
            return
            
        # Generate predictions for next 30 minutes
        future_timestamps = [
            datetime.utcnow() + timedelta(minutes=i*5)
            for i in range(1, 7)  # Next 30 minutes in 5-minute intervals
        ]
        
        predictions = cpu_model.predict(historical_data, future_timestamps)
        
        # Check if any predictions exceed scale-up threshold
        cpu_threshold = next(
            (t for t in target.thresholds if t.metric == ResourceMetric.CPU_UTILIZATION),
            None
        )
        
        if cpu_threshold:
            max_predicted = max(predictions)
            
            if max_predicted > cpu_threshold.scale_up_threshold and target.can_scale_up():
                # Predictive scale up
                new_count = self._calculate_predictive_scale_count(target, max_predicted, cpu_threshold)
                
                decision = {
                    "action": ScalingDirection.UP,
                    "new_count": new_count,
                    "reason": f"Predicted CPU utilization: {max_predicted:.1f}%",
                    "trigger": ScalingTrigger.PREDICTION,
                    "confidence": cpu_model.accuracy / 100
                }
                
                await self._execute_scaling_action(target, decision)
                
    def _calculate_predictive_scale_count(self, target: ScalingTarget,
                                        predicted_value: float,
                                        threshold: MetricThreshold) -> int:
        """Calculate scale count based on prediction.
        
        Args:
            target: Scaling target
            predicted_value: Predicted metric value
            threshold: Threshold configuration
            
        Returns:
            New resource count
        """
        # More conservative scaling for predictions
        excess_ratio = predicted_value / threshold.scale_up_threshold
        scale_factor = 1 + min(0.3, 0.15 * excess_ratio)  # Max 30% increase
        
        new_count = math.ceil(target.current_count * scale_factor)
        return min(new_count, target.max_count)
        
    async def _evaluate_cost_optimizations(self) -> None:
        """Evaluate cost optimization opportunities."""
        for target_id, target in self._targets.items():
            try:
                await self._evaluate_target_cost_optimization(target)
            except Exception as e:
                self.logger.error(f"Cost optimization error for {target_id}: {e}")
                
    async def _evaluate_target_cost_optimization(self, target: ScalingTarget) -> None:
        """Evaluate cost optimization for a specific target.
        
        Args:
            target: Target to optimize
        """
        # Analyze recent utilization patterns
        recent_cpu = self._get_historical_metric_values(
            target.target_id, ResourceMetric.CPU_UTILIZATION, hours=2
        )
        
        if len(recent_cpu) < 10:
            return
            
        avg_cpu = statistics.mean(recent_cpu)
        max_cpu = max(recent_cpu)
        
        # If consistently low utilization and no recent scale events
        if (avg_cpu < 20 and max_cpu < 40 and 
            target.can_scale_down() and
            not target.is_in_cooldown(cooldown_seconds=1800)):  # 30 min cooldown for cost optimization
            
            # Calculate potential savings
            current_cost = self._calculate_hourly_cost(target.resource_type, target.current_count)
            new_count = max(target.min_count, target.current_count - 1)
            new_cost = self._calculate_hourly_cost(target.resource_type, new_count)
            
            potential_savings = (current_cost - new_cost) * 24 * 30  # Monthly savings
            
            if potential_savings > 10:  # $10/month threshold
                decision = {
                    "action": ScalingDirection.DOWN,
                    "new_count": new_count,
                    "reason": f"Cost optimization: avg CPU {avg_cpu:.1f}%, savings ${potential_savings:.0f}/month",
                    "trigger": ScalingTrigger.COST_OPTIMIZATION,
                    "confidence": 0.6
                }
                
                await self._execute_scaling_action(target, decision)
                
    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get comprehensive scaling status.
        
        Returns:
            Dictionary with scaling status and metrics
        """
        total_targets = len(self._targets)
        active_targets = sum(1 for t in self._targets.values() if t.current_count > 0)
        
        recent_actions = [
            a for a in self._scaling_actions
            if (datetime.utcnow() - a.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        total_cost = sum(
            self._calculate_hourly_cost(t.resource_type, t.current_count)
            for t in self._targets.values()
        )
        
        return {
            "monitoring_active": self._monitoring_active,
            "targets": {
                "total": total_targets,
                "active": active_targets,
                "in_cooldown": sum(1 for t in self._targets.values() if t.is_in_cooldown())
            },
            "recent_actions": {
                "total": len(recent_actions),
                "scale_up": sum(1 for a in recent_actions if a.direction == ScalingDirection.UP),
                "scale_down": sum(1 for a in recent_actions if a.direction == ScalingDirection.DOWN),
                "success_rate": statistics.mean([a.success for a in recent_actions]) if recent_actions else 1.0
            },
            "cost": {
                "current_hourly": total_cost,
                "estimated_monthly": total_cost * 24 * 30,
                "recent_cost_impact": sum(a.cost_impact for a in recent_actions)
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    def get_target_info(self, target_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a scaling target.
        
        Args:
            target_id: Target ID to get information for
            
        Returns:
            Target information or None if not found
        """
        target = self._targets.get(target_id)
        if not target:
            return None
            
        # Get recent metrics
        recent_metrics = self._get_recent_metrics(target_id, minutes=60)
        
        # Calculate utilization stats
        cpu_values = [m["value"] for m in recent_metrics.get(ResourceMetric.CPU_UTILIZATION, [])]
        memory_values = [m["value"] for m in recent_metrics.get(ResourceMetric.MEMORY_UTILIZATION, [])]
        
        return {
            "target_id": target.target_id,
            "name": target.name,
            "resource_type": target.resource_type,
            "current_count": target.current_count,
            "min_count": target.min_count,
            "max_count": target.max_count,
            "scaling_policy": target.scaling_policy.value,
            "last_scaled": target.last_scaled.isoformat() if target.last_scaled else None,
            "in_cooldown": target.is_in_cooldown(),
            "current_metrics": {
                "cpu_avg": statistics.mean(cpu_values) if cpu_values else 0,
                "cpu_max": max(cpu_values) if cpu_values else 0,
                "memory_avg": statistics.mean(memory_values) if memory_values else 0,
                "memory_max": max(memory_values) if memory_values else 0
            },
            "hourly_cost": self._calculate_hourly_cost(target.resource_type, target.current_count),
            "thresholds": [
                {
                    "metric": t.metric.value,
                    "scale_up": t.scale_up_threshold,
                    "scale_down": t.scale_down_threshold
                }
                for t in target.thresholds
            ]
        }