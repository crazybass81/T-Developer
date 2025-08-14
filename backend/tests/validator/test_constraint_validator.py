"""
ConstraintValidator Tests - Day 31
Tests for constraint validation in services
"""

import pytest

from src.validator.constraint_validator import ConstraintValidator


class TestConstraintValidator:
    """Tests for ConstraintValidator"""

    @pytest.fixture
    def validator(self):
        """Create ConstraintValidator instance"""
        return ConstraintValidator()

    @pytest.fixture
    def sample_service(self):
        """Sample service with constraints"""
        return {
            "agents": [
                {"name": "agent1", "size_kb": 5.2, "instantiation_us": 0.8},
                {"name": "agent2", "size_kb": 4.8, "instantiation_us": 1.2},
            ],
            "constraints": {
                "max_size_kb": 6.5,
                "max_instantiation_us": 3.0,
                "min_test_coverage": 0.85,
                "max_total_memory_mb": 50,
                "max_agents": 10,
                "min_performance_score": 0.8,
            },
            "metrics": {"test_coverage": 0.92, "performance_score": 0.85},
        }

    def test_validator_initialization(self, validator):
        """Test ConstraintValidator initialization"""
        assert validator is not None
        assert hasattr(validator, "validate")
        assert hasattr(validator, "constraints")

    def test_validate_size_constraint(self, validator, sample_service):
        """Test size constraint validation"""
        result = validator.validate_size(
            sample_service["agents"], sample_service["constraints"]["max_size_kb"]
        )

        assert result["valid"] is True
        assert result["max_size"] == 5.2
        assert result["constraint"] == 6.5

    def test_validate_size_violation(self, validator):
        """Test size constraint violation"""
        agents = [{"size_kb": 7.0}]
        result = validator.validate_size(agents, 6.5)

        assert result["valid"] is False
        assert "exceeds" in result["violation"]

    def test_validate_speed_constraint(self, validator, sample_service):
        """Test instantiation speed constraint"""
        result = validator.validate_speed(
            sample_service["agents"], sample_service["constraints"]["max_instantiation_us"]
        )

        assert result["valid"] is True
        assert result["max_time"] == 1.2

    def test_validate_coverage_constraint(self, validator, sample_service):
        """Test test coverage constraint"""
        result = validator.validate_coverage(
            sample_service["metrics"]["test_coverage"],
            sample_service["constraints"]["min_test_coverage"],
        )

        assert result["valid"] is True
        assert result["actual"] == 0.92
        assert result["required"] == 0.85

    def test_validate_coverage_violation(self, validator):
        """Test coverage constraint violation"""
        result = validator.validate_coverage(0.70, 0.85)

        assert result["valid"] is False
        assert "below minimum" in result["violation"]

    def test_validate_memory_constraint(self, validator, sample_service):
        """Test memory constraint validation"""
        result = validator.validate_memory(
            sample_service["agents"], sample_service["constraints"]["max_total_memory_mb"]
        )

        assert result["valid"] is True
        assert result["total_memory_mb"] < 50

    def test_validate_agent_count(self, validator, sample_service):
        """Test agent count constraint"""
        result = validator.validate_agent_count(
            sample_service["agents"], sample_service["constraints"]["max_agents"]
        )

        assert result["valid"] is True
        assert result["agent_count"] == 2
        assert result["max_allowed"] == 10

    def test_validate_performance_score(self, validator, sample_service):
        """Test performance score constraint"""
        result = validator.validate_performance(
            sample_service["metrics"]["performance_score"],
            sample_service["constraints"]["min_performance_score"],
        )

        assert result["valid"] is True
        assert result["score"] == 0.85

    def test_validate_all_constraints(self, validator, sample_service):
        """Test complete constraint validation"""
        result = validator.validate(sample_service)

        assert result["valid"] is True
        assert result["constraints_met"] is True
        assert len(result["violations"]) == 0

    def test_validate_with_violations(self, validator):
        """Test validation with multiple violations"""
        service = {
            "agents": [{"size_kb": 8.0, "instantiation_us": 5.0}],  # Both exceed limits
            "constraints": {"max_size_kb": 6.5, "max_instantiation_us": 3.0},
            "metrics": {},
        }

        result = validator.validate(service)

        assert result["valid"] is False
        assert result["constraints_met"] is False
        assert len(result["violations"]) >= 2

    def test_custom_constraint(self, validator):
        """Test adding custom constraints"""

        def custom_check(service):
            return len(service.get("agents", [])) % 2 == 0  # Even number of agents

        validator.add_constraint("even_agents", custom_check)

        service = {"agents": [1, 2]}
        result = validator.check_custom_constraint(service, "even_agents")

        assert result["valid"] is True

    def test_constraint_priority(self, validator):
        """Test constraint evaluation priority"""
        constraints = [("critical", lambda s: False), ("normal", lambda s: True)]  # Always fails

        result = validator.evaluate_with_priority(constraints, {})

        assert result["critical_passed"] is False
        assert result["should_block"] is True

    def test_soft_constraints(self, validator, sample_service):
        """Test soft vs hard constraints"""
        sample_service["constraints"]["soft_max_size_kb"] = 6.0
        sample_service["agents"][0]["size_kb"] = 6.2  # Exceeds soft limit

        result = validator.validate_soft_constraints(sample_service)

        assert result["hard_constraints_met"] is True
        assert result["soft_constraints_met"] is False
        assert len(result["warnings"]) > 0

    def test_constraint_groups(self, validator):
        """Test grouped constraint validation"""
        service = {
            "constraints": {
                "group1": {"max_size_kb": 6.5, "max_agents": 5},
                "group2": {"min_coverage": 0.85, "min_score": 0.8},
            }
        }

        result = validator.validate_groups(service)

        assert "group1" in result
        assert "group2" in result

    def test_dynamic_constraints(self, validator):
        """Test dynamic constraint calculation"""
        service = {
            "agents": [{"size_kb": 3.0}, {"size_kb": 3.0}],
            "constraints": {"max_size_kb": "dynamic:agent_count * 3.5"},
        }

        result = validator.validate_dynamic(service)

        assert result["valid"] is True
        assert result["calculated_limit"] == 7.0  # 2 agents * 3.5

    def test_constraint_relaxation(self, validator):
        """Test constraint relaxation for development"""
        validator.set_mode("development")

        service = {
            "agents": [{"size_kb": 7.0}],  # Exceeds production limit
            "constraints": {"max_size_kb": 6.5},
        }

        result = validator.validate(service)

        # In dev mode, should warn but not fail
        assert result["valid"] is True
        assert len(result["warnings"]) > 0

    def test_constraint_reporting(self, validator, sample_service):
        """Test constraint validation report"""
        result = validator.validate(sample_service)
        report = validator.generate_report(result)

        assert isinstance(report, str)
        assert "Constraint Validation Report" in report
        assert "✅" in report

    def test_export_constraints(self, validator, tmp_path):
        """Test exporting constraint definitions"""
        export_file = tmp_path / "constraints.json"
        validator.export_constraints(export_file)

        assert export_file.exists()

        import json

        with open(export_file) as f:
            exported = json.load(f)
        assert "constraints" in exported
