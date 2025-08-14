"""
ServiceValidator Tests - Day 31
Tests for validating services built by ServiceBuilder
"""

import json

import pytest

from src.validator.service_validator import ServiceValidator


class TestServiceValidator:
    """Tests for ServiceValidator"""

    @pytest.fixture
    def validator(self):
        """Create ServiceValidator instance"""
        return ServiceValidator()

    @pytest.fixture
    def sample_service(self):
        """Sample service specification"""
        return {
            "name": "DataProcessor",
            "agents": [
                {
                    "name": "parser",
                    "size_kb": 5.2,
                    "instantiation_us": 0.8,
                    "methods": ["parse", "validate"],
                    "dependencies": ["json", "typing"],
                },
                {
                    "name": "transformer",
                    "size_kb": 6.1,
                    "instantiation_us": 1.2,
                    "methods": ["transform", "normalize"],
                    "dependencies": ["pandas", "numpy"],
                },
            ],
            "workflow": {
                "steps": [
                    {"agent": "parser", "method": "parse"},
                    {"agent": "transformer", "method": "transform"},
                ],
                "parallel": False,
            },
            "constraints": {
                "max_size_kb": 6.5,
                "max_instantiation_us": 3.0,
                "min_test_coverage": 0.85,
            },
        }

    def test_validator_initialization(self, validator):
        """Test ServiceValidator initialization"""
        assert validator is not None
        assert hasattr(validator, "type_checker")
        assert hasattr(validator, "constraint_validator")
        assert validator.validation_results == []

    def test_validate_service_structure(self, validator, sample_service):
        """Test service structure validation"""
        result = validator.validate_structure(sample_service)

        assert result["valid"] is True
        assert "errors" in result
        assert len(result["errors"]) == 0
        assert result["service_name"] == "DataProcessor"

    def test_validate_invalid_structure(self, validator):
        """Test validation with invalid structure"""
        invalid_service = {
            "name": "InvalidService"
            # Missing required fields
        }

        result = validator.validate_structure(invalid_service)

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("agents" in err for err in result["errors"])

    def test_validate_agent_constraints(self, validator, sample_service):
        """Test agent constraint validation"""
        result = validator.validate_agents(sample_service["agents"], sample_service["constraints"])

        assert result["valid"] is True
        assert result["total_agents"] == 2
        assert all(agent["size_valid"] for agent in result["agents"])
        assert all(agent["speed_valid"] for agent in result["agents"])

    def test_validate_oversized_agent(self, validator):
        """Test validation with oversized agent"""
        agents = [
            {
                "name": "oversized",
                "size_kb": 8.5,  # Exceeds 6.5KB limit
                "instantiation_us": 1.0,
                "methods": ["process"],
            }
        ]
        constraints = {"max_size_kb": 6.5}

        result = validator.validate_agents(agents, constraints)

        assert result["valid"] is False
        assert not result["agents"][0]["size_valid"]
        assert "exceeds maximum" in result["agents"][0]["error"]

    def test_validate_workflow(self, validator, sample_service):
        """Test workflow validation"""
        result = validator.validate_workflow(sample_service["workflow"], sample_service["agents"])

        assert result["valid"] is True
        assert result["steps_count"] == 2
        assert all(step["valid"] for step in result["steps"])

    def test_validate_invalid_workflow(self, validator):
        """Test validation with invalid workflow"""
        workflow = {"steps": [{"agent": "nonexistent", "method": "process"}]}
        agents = [{"name": "parser"}]

        result = validator.validate_workflow(workflow, agents)

        assert result["valid"] is False
        assert not result["steps"][0]["valid"]
        assert "not found" in result["steps"][0]["error"]

    def test_type_validation(self, validator, sample_service):
        """Test type checking functionality"""
        result = validator.check_types(sample_service)

        assert result["valid"] is True
        assert result["type_errors"] == []
        assert "checked_fields" in result

    def test_constraint_validation(self, validator, sample_service):
        """Test constraint validation"""
        result = validator.check_constraints(sample_service)

        assert result["valid"] is True
        assert result["constraints_met"] is True
        assert "violations" in result
        assert len(result["violations"]) == 0

    def test_full_validation(self, validator, sample_service):
        """Test complete service validation"""
        result = validator.validate(sample_service)

        assert result["valid"] is True
        assert result["service_name"] == "DataProcessor"
        assert "structure" in result
        assert "agents" in result
        assert "workflow" in result
        assert "types" in result
        assert "constraints" in result

    def test_validation_with_warnings(self, validator, sample_service):
        """Test validation that passes with warnings"""
        # Agent close to size limit
        sample_service["agents"][0]["size_kb"] = 6.4

        result = validator.validate(sample_service)

        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert "close to limit" in result["warnings"][0]

    def test_performance_validation(self, validator, sample_service):
        """Test performance metric validation"""
        result = validator.validate_performance(sample_service)

        assert result["valid"] is True
        assert "total_instantiation_time" in result
        assert "total_memory" in result
        assert result["total_instantiation_time"] < 3.0

    def test_dependency_validation(self, validator, sample_service):
        """Test dependency checking"""
        result = validator.validate_dependencies(sample_service["agents"])

        assert result["valid"] is True
        assert "total_dependencies" in result
        assert result["total_dependencies"] == 4
        assert "conflicts" in result
        assert len(result["conflicts"]) == 0

    def test_validation_report_generation(self, validator, sample_service):
        """Test validation report generation"""
        validation_result = validator.validate(sample_service)
        report = validator.generate_report(validation_result)

        assert isinstance(report, str)
        assert "ServiceValidator Report" in report
        assert "DataProcessor" in report
        assert "✅" in report or "❌" in report

    def test_batch_validation(self, validator, sample_service):
        """Test validating multiple services"""
        # Create different services to avoid cache
        service1 = sample_service.copy()
        service2 = sample_service.copy()
        service2["name"] = "DataProcessor2"  # Make it different

        services = [service1, service2]
        results = validator.validate_batch(services)

        assert len(results) == 2
        assert all(r["valid"] for r in results)
        assert validator.get_stats()["total_validated"] == 2

    def test_validation_caching(self, validator, sample_service):
        """Test validation result caching"""
        # First validation
        result1 = validator.validate(sample_service)

        # Second validation (should use cache)
        result2 = validator.validate(sample_service)

        assert result1 == result2
        assert validator.cache_hits == 1

    def test_custom_rules(self, validator):
        """Test adding custom validation rules"""

        def custom_rule(service):
            return "test" in service.get("name", "").lower()

        validator.add_rule("name_contains_test", custom_rule)

        service = {"name": "TestService"}
        result = validator.apply_custom_rules(service)

        assert result["custom_rules"]["name_contains_test"] is True

    def test_export_validation_results(self, validator, sample_service, tmp_path):
        """Test exporting validation results"""
        result = validator.validate(sample_service)

        export_file = tmp_path / "validation_results.json"
        validator.export_results(result, export_file)

        assert export_file.exists()

        with open(export_file) as f:
            exported = json.load(f)
        assert exported["service_name"] == "DataProcessor"
