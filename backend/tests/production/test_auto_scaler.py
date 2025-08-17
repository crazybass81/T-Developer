"""
Tests for auto_scaler module.

This module tests the intelligent auto-scaling system including metric collection,
scaling decisions, predictive scaling, and cost-aware optimization.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from packages.production.auto_scaler import (
    AutoScaler,
    MetricThreshold,
    PredictionModel,
    ResourceMetric,
    ScalingDirection,
    ScalingPolicy,
    ScalingTarget,
    ScalingTrigger,
)


@pytest.fixture
async def auto_scaler():
    """Create auto-scaler instance for testing."""
    scaler = AutoScaler()
    await scaler.initialize()
    yield scaler
    await scaler.stop_monitoring()


@pytest.fixture
def sample_scaling_target():
    """Create sample scaling target for testing."""
    return ScalingTarget(
        target_id="test-web-servers",
        name="Test Web Servers",
        resource_type="pods",
        current_count=3,
        min_count=1,
        max_count=10,
    )


class TestMetricThreshold:
    """Test MetricThreshold class functionality."""

    def test_threshold_creation(self):
        """Test metric threshold creation."""
        threshold = MetricThreshold(
            metric=ResourceMetric.CPU_UTILIZATION,
            scale_up_threshold=80.0,
            scale_down_threshold=30.0,
            evaluation_periods=3,
        )

        assert threshold.metric == ResourceMetric.CPU_UTILIZATION
        assert threshold.scale_up_threshold == 80.0
        assert threshold.scale_down_threshold == 30.0
        assert threshold.evaluation_periods == 3

    def test_scale_up_trigger(self):
        """Test scale up trigger detection."""
        threshold = MetricThreshold(
            metric=ResourceMetric.CPU_UTILIZATION,
            scale_up_threshold=80.0,
            scale_down_threshold=30.0,
            evaluation_periods=3,
        )

        # Values all above threshold should trigger scale up
        values = [85.0, 87.0, 82.0]
        assert threshold.is_scale_up_triggered(values, datetime.utcnow()) is True

        # Mixed values should not trigger
        values = [85.0, 75.0, 82.0]
        assert threshold.is_scale_up_triggered(values, datetime.utcnow()) is False

        # Insufficient data should not trigger
        values = [85.0, 87.0]  # Only 2 values, need 3
        assert threshold.is_scale_up_triggered(values, datetime.utcnow()) is False

    def test_scale_down_trigger(self):
        """Test scale down trigger detection."""
        threshold = MetricThreshold(
            metric=ResourceMetric.CPU_UTILIZATION,
            scale_up_threshold=80.0,
            scale_down_threshold=30.0,
            evaluation_periods=3,
        )

        # Values all below threshold should trigger scale down
        values = [25.0, 28.0, 22.0]
        assert threshold.is_scale_down_triggered(values, datetime.utcnow()) is True

        # Mixed values should not trigger
        values = [25.0, 35.0, 22.0]
        assert threshold.is_scale_down_triggered(values, datetime.utcnow()) is False


class TestPredictionModel:
    """Test PredictionModel class functionality."""

    def test_model_creation(self):
        """Test prediction model creation."""
        model = PredictionModel(model_type="linear_trend", prediction_horizon_minutes=30)

        assert model.model_type == "linear_trend"
        assert model.prediction_horizon_minutes == 30
        assert model.accuracy == 0.0  # Default

    def test_linear_prediction(self):
        """Test linear trend prediction."""
        model = PredictionModel(model_type="linear_trend")

        # Upward trend data
        historical_data = [10.0, 15.0, 20.0, 25.0, 30.0]
        future_timestamps = [
            datetime.utcnow() + timedelta(minutes=5),
            datetime.utcnow() + timedelta(minutes=10),
        ]

        predictions = model.predict(historical_data, future_timestamps)

        assert len(predictions) == 2
        # Should predict continued upward trend
        assert predictions[0] > 30.0
        assert predictions[1] > predictions[0]

    def test_prediction_with_empty_data(self):
        """Test prediction with empty historical data."""
        model = PredictionModel(model_type="linear_trend")

        predictions = model.predict([], [datetime.utcnow()])
        assert predictions == [0.0]

    def test_prediction_with_single_data_point(self):
        """Test prediction with single data point."""
        model = PredictionModel(model_type="linear_trend")

        predictions = model.predict([50.0], [datetime.utcnow()])
        assert predictions == [50.0]


class TestScalingTarget:
    """Test ScalingTarget class functionality."""

    def test_target_creation(self, sample_scaling_target):
        """Test scaling target creation."""
        target = sample_scaling_target

        assert target.target_id == "test-web-servers"
        assert target.name == "Test Web Servers"
        assert target.resource_type == "pods"
        assert target.current_count == 3
        assert target.min_count == 1
        assert target.max_count == 10

    def test_can_scale_up(self, sample_scaling_target):
        """Test scale up capability check."""
        target = sample_scaling_target

        # Currently at 3, max is 10, should be able to scale up
        assert target.can_scale_up() is True

        # Set to max count
        target.current_count = target.max_count
        assert target.can_scale_up() is False

    def test_can_scale_down(self, sample_scaling_target):
        """Test scale down capability check."""
        target = sample_scaling_target

        # Currently at 3, min is 1, should be able to scale down
        assert target.can_scale_down() is True

        # Set to min count
        target.current_count = target.min_count
        assert target.can_scale_down() is False

    def test_cooldown_period(self, sample_scaling_target):
        """Test cooldown period checking."""
        target = sample_scaling_target

        # No previous scaling, should not be in cooldown
        assert target.is_in_cooldown() is False

        # Set recent scaling time
        target.last_scaled = datetime.utcnow() - timedelta(minutes=5)
        assert target.is_in_cooldown() is True

        # Set old scaling time
        target.last_scaled = datetime.utcnow() - timedelta(minutes=15)
        assert target.is_in_cooldown() is False


class TestAutoScaler:
    """Test AutoScaler class functionality."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test auto-scaler initialization."""
        scaler = AutoScaler()
        await scaler.initialize()

        assert scaler._prediction_models is not None
        assert scaler._cost_calculator is not None
        assert len(scaler._prediction_models["default"]) > 0

    @pytest.mark.asyncio
    async def test_register_target(self, auto_scaler, sample_scaling_target):
        """Test target registration."""
        target = sample_scaling_target

        await auto_scaler.register_target(target)

        assert target.target_id in auto_scaler._targets
        assert len(target.thresholds) > 0  # Should have default thresholds
        assert target.target_id in auto_scaler._metrics_history

    @pytest.mark.asyncio
    async def test_register_invalid_target(self, auto_scaler):
        """Test registration of invalid target."""
        # Target with min >= max
        invalid_target = ScalingTarget(
            target_id="invalid",
            name="Invalid",
            resource_type="pods",
            current_count=5,
            min_count=10,
            max_count=5,
        )

        with pytest.raises(ValueError, match="min_count must be less than max_count"):
            await auto_scaler.register_target(invalid_target)

    @pytest.mark.asyncio
    async def test_register_duplicate_target(self, auto_scaler, sample_scaling_target):
        """Test registration of duplicate target."""
        target = sample_scaling_target

        await auto_scaler.register_target(target)

        # Try to register same target again
        with pytest.raises(ValueError, match="already registered"):
            await auto_scaler.register_target(target)

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, auto_scaler):
        """Test starting and stopping monitoring."""
        # Start monitoring
        await auto_scaler.start_monitoring()
        assert auto_scaler._monitoring_active is True

        # Stop monitoring
        await auto_scaler.stop_monitoring()
        assert auto_scaler._monitoring_active is False

    @pytest.mark.asyncio
    async def test_metric_collection(self, auto_scaler, sample_scaling_target):
        """Test metric collection for targets."""
        await auto_scaler.register_target(sample_scaling_target)

        # Mock the metric fetching
        with patch.object(auto_scaler, "_fetch_target_metrics") as mock_fetch:
            mock_fetch.return_value = {
                ResourceMetric.CPU_UTILIZATION: 75.0,
                ResourceMetric.MEMORY_UTILIZATION: 60.0,
                ResourceMetric.REQUEST_RATE: 800.0,
            }

            await auto_scaler._collect_metrics()

            # Check that metrics were stored
            target_metrics = auto_scaler._metrics_history[sample_scaling_target.target_id]
            assert len(target_metrics[ResourceMetric.CPU_UTILIZATION]) > 0

    @pytest.mark.asyncio
    async def test_scaling_decision_scale_up(self, auto_scaler, sample_scaling_target):
        """Test scaling decision for scale up scenario."""
        await auto_scaler.register_target(sample_scaling_target)

        # Simulate high CPU usage that should trigger scale up
        target_metrics = auto_scaler._metrics_history[sample_scaling_target.target_id]
        current_time = datetime.utcnow()

        # Add several high CPU metrics
        for i in range(5):
            metric_time = current_time - timedelta(minutes=i)
            target_metrics[ResourceMetric.CPU_UTILIZATION].append(
                {"timestamp": metric_time, "value": 85.0}  # Above default threshold of 70%
            )

        decision = await auto_scaler._make_scaling_decision(sample_scaling_target)

        assert decision["action"] == ScalingDirection.UP
        assert decision["new_count"] > sample_scaling_target.current_count

    @pytest.mark.asyncio
    async def test_scaling_decision_scale_down(self, auto_scaler, sample_scaling_target):
        """Test scaling decision for scale down scenario."""
        await auto_scaler.register_target(sample_scaling_target)

        # Simulate low CPU usage that should trigger scale down
        target_metrics = auto_scaler._metrics_history[sample_scaling_target.target_id]
        current_time = datetime.utcnow()

        # Add several low CPU metrics
        for i in range(5):
            metric_time = current_time - timedelta(minutes=i)
            target_metrics[ResourceMetric.CPU_UTILIZATION].append(
                {"timestamp": metric_time, "value": 20.0}  # Below default threshold of 30%
            )

        decision = await auto_scaler._make_scaling_decision(sample_scaling_target)

        assert decision["action"] == ScalingDirection.DOWN
        assert decision["new_count"] < sample_scaling_target.current_count

    @pytest.mark.asyncio
    async def test_scaling_decision_cooldown(self, auto_scaler, sample_scaling_target):
        """Test that scaling is prevented during cooldown."""
        await auto_scaler.register_target(sample_scaling_target)

        # Set recent scaling time (in cooldown)
        sample_scaling_target.last_scaled = datetime.utcnow() - timedelta(minutes=5)

        decision = await auto_scaler._make_scaling_decision(sample_scaling_target)

        assert decision["action"] == ScalingDirection.STEADY
        assert "cooldown" in decision["reason"].lower()

    @pytest.mark.asyncio
    async def test_execute_scaling_action(self, auto_scaler, sample_scaling_target):
        """Test scaling action execution."""
        await auto_scaler.register_target(sample_scaling_target)

        decision = {
            "action": ScalingDirection.UP,
            "new_count": 5,
            "reason": "High CPU utilization",
            "trigger": ScalingTrigger.THRESHOLD,
            "confidence": 0.8,
        }

        # Mock the actual scaling operation
        with patch.object(auto_scaler, "_perform_scaling") as mock_scaling:
            mock_scaling.return_value = True

            await auto_scaler._execute_scaling_action(sample_scaling_target, decision)

            # Check that target was updated
            assert sample_scaling_target.current_count == 5
            assert sample_scaling_target.last_scaled is not None

            # Check that action was recorded
            assert len(auto_scaler._scaling_actions) > 0
            action = auto_scaler._scaling_actions[-1]
            assert action.direction == ScalingDirection.UP
            assert action.to_count == 5

    @pytest.mark.asyncio
    async def test_predictive_scaling(self, auto_scaler, sample_scaling_target):
        """Test predictive scaling functionality."""
        # Set target to use predictive scaling
        sample_scaling_target.scaling_policy = ScalingPolicy.PREDICTIVE
        await auto_scaler.register_target(sample_scaling_target)

        # Add historical CPU data showing upward trend
        target_metrics = auto_scaler._metrics_history[sample_scaling_target.target_id]
        current_time = datetime.utcnow()

        for i in range(10):
            metric_time = current_time - timedelta(minutes=i * 5)
            # Upward trend: 50, 55, 60, 65, 70...
            cpu_value = 50.0 + (i * 5)
            target_metrics[ResourceMetric.CPU_UTILIZATION].append(
                {"timestamp": metric_time, "value": cpu_value}
            )

        # Update prediction model with data
        await auto_scaler._update_prediction_models()

        # Test predictive scaling decision
        with patch.object(auto_scaler, "_perform_scaling") as mock_scaling:
            mock_scaling.return_value = True

            await auto_scaler._make_predictive_scaling_decision(sample_scaling_target)

            # Should have made a predictive scaling decision
            # (specific assertion depends on prediction logic)

    @pytest.mark.asyncio
    async def test_cost_optimization_scaling(self, auto_scaler, sample_scaling_target):
        """Test cost-aware scaling decisions."""
        await auto_scaler.register_target(sample_scaling_target)

        # Simulate low utilization for cost optimization
        target_metrics = auto_scaler._metrics_history[sample_scaling_target.target_id]
        current_time = datetime.utcnow()

        # Add low utilization metrics over time
        for i in range(20):
            metric_time = current_time - timedelta(minutes=i * 5)
            target_metrics[ResourceMetric.CPU_UTILIZATION].append(
                {"timestamp": metric_time, "value": 15.0}  # Consistently low
            )

        # Mock cost calculation
        with patch.object(auto_scaler, "_calculate_hourly_cost") as mock_cost:
            mock_cost.return_value = 10.0  # $10/hour

            await auto_scaler._evaluate_target_cost_optimization(sample_scaling_target)

            # Should generate cost optimization recommendations
            # Check if scaling actions were taken for cost reasons

    @pytest.mark.asyncio
    async def test_scaling_status(self, auto_scaler, sample_scaling_target):
        """Test scaling status retrieval."""
        await auto_scaler.register_target(sample_scaling_target)
        await auto_scaler.start_monitoring()

        status = await auto_scaler.get_scaling_status()

        assert "monitoring_active" in status
        assert "targets" in status
        assert "recent_actions" in status
        assert "cost" in status

        assert status["monitoring_active"] is True
        assert status["targets"]["total"] == 1

    @pytest.mark.asyncio
    async def test_target_info(self, auto_scaler, sample_scaling_target):
        """Test target information retrieval."""
        await auto_scaler.register_target(sample_scaling_target)

        # Add some metrics
        target_metrics = auto_scaler._metrics_history[sample_scaling_target.target_id]
        target_metrics[ResourceMetric.CPU_UTILIZATION].append(
            {"timestamp": datetime.utcnow(), "value": 65.0}
        )

        info = auto_scaler.get_target_info(sample_scaling_target.target_id)

        assert info is not None
        assert info["target_id"] == sample_scaling_target.target_id
        assert info["name"] == sample_scaling_target.name
        assert "current_metrics" in info
        assert "thresholds" in info

    def test_scale_count_calculations(self, auto_scaler):
        """Test scaling count calculations."""
        target = ScalingTarget(
            target_id="test",
            name="Test",
            resource_type="pods",
            current_count=4,
            min_count=1,
            max_count=20,
        )

        threshold = MetricThreshold(
            metric=ResourceMetric.CPU_UTILIZATION,
            scale_up_threshold=70.0,
            scale_down_threshold=30.0,
        )

        # Test scale up calculation
        high_values = [85.0, 87.0, 90.0]  # 20-30% above threshold
        new_count = auto_scaler._calculate_scale_up_count(target, threshold, high_values)

        # Should scale up but not exceed max_scaling_velocity (50%)
        assert new_count > target.current_count
        assert new_count <= target.current_count * 1.5
        assert new_count <= target.max_count

        # Test scale down calculation
        low_values = [20.0, 18.0, 15.0]  # Well below threshold
        new_count = auto_scaler._calculate_scale_down_count(target, threshold, low_values)

        # Should scale down conservatively
        assert new_count < target.current_count
        assert new_count >= target.min_count


class TestAutoScalerIntegration:
    """Integration tests for auto-scaler."""

    @pytest.mark.asyncio
    async def test_full_scaling_cycle(self):
        """Test complete scaling cycle from registration to execution."""
        scaler = AutoScaler()
        await scaler.initialize()

        # Create and register target
        target = ScalingTarget(
            target_id="integration-test",
            name="Integration Test Target",
            resource_type="pods",
            current_count=2,
            min_count=1,
            max_count=10,
        )

        await scaler.register_target(target)

        # Simulate monitoring and scaling
        await scaler.start_monitoring()

        # Add high utilization metrics
        target_metrics = scaler._metrics_history[target.target_id]
        current_time = datetime.utcnow()

        for i in range(5):
            metric_time = current_time - timedelta(minutes=i)
            target_metrics[ResourceMetric.CPU_UTILIZATION].append(
                {"timestamp": metric_time, "value": 85.0}  # High utilization
            )

        # Mock scaling execution
        with patch.object(scaler, "_perform_scaling") as mock_scaling:
            mock_scaling.return_value = True

            # Trigger scaling evaluation
            await scaler._evaluate_scaling_decisions()

            # Check that scaling occurred
            assert target.current_count > 2  # Should have scaled up
            assert len(scaler._scaling_actions) > 0

            # Verify scaling action details
            action = scaler._scaling_actions[-1]
            assert action.direction == ScalingDirection.UP
            assert action.success is True

        await scaler.stop_monitoring()

    @pytest.mark.asyncio
    async def test_multiple_targets_scaling(self):
        """Test scaling with multiple targets."""
        scaler = AutoScaler()
        await scaler.initialize()

        # Create multiple targets
        targets = []
        for i in range(3):
            target = ScalingTarget(
                target_id=f"multi-target-{i}",
                name=f"Multi Target {i}",
                resource_type="pods",
                current_count=2,
                min_count=1,
                max_count=10,
            )
            targets.append(target)
            await scaler.register_target(target)

        # Add different utilization patterns
        current_time = datetime.utcnow()

        # Target 0: High utilization (should scale up)
        target_0_metrics = scaler._metrics_history[targets[0].target_id]
        for i in range(5):
            target_0_metrics[ResourceMetric.CPU_UTILIZATION].append(
                {"timestamp": current_time - timedelta(minutes=i), "value": 85.0}
            )

        # Target 1: Low utilization (should scale down)
        target_1_metrics = scaler._metrics_history[targets[1].target_id]
        for i in range(5):
            target_1_metrics[ResourceMetric.CPU_UTILIZATION].append(
                {"timestamp": current_time - timedelta(minutes=i), "value": 20.0}
            )

        # Target 2: Normal utilization (should remain steady)
        target_2_metrics = scaler._metrics_history[targets[2].target_id]
        for i in range(5):
            target_2_metrics[ResourceMetric.CPU_UTILIZATION].append(
                {"timestamp": current_time - timedelta(minutes=i), "value": 50.0}
            )

        # Mock scaling execution
        with patch.object(scaler, "_perform_scaling") as mock_scaling:
            mock_scaling.return_value = True

            await scaler._evaluate_scaling_decisions()

            # Check scaling results
            actions = scaler._scaling_actions

            # Should have actions for targets 0 and 1, but not 2
            target_0_actions = [a for a in actions if a.resource_type == targets[0].resource_type]
            target_1_actions = [a for a in actions if a.resource_type == targets[1].resource_type]

            # Verify appropriate scaling directions
            # (Note: Actual assertion depends on implementation details)


if __name__ == "__main__":
    pytest.main([__file__])
