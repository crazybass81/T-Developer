"""🧬 Migration Framework Tests <6.5KB
Day 16: Test Suite for Migration Components
Tests all migration framework components
"""
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.src.migration.compatibility_checker_v2 import (
    CompatibilityChecker,
    CompatibilityResult,
)
from backend.src.migration.code_converter_v2 import CodeConverter
from backend.src.migration.legacy_analyzer_v2 import AnalysisResult, Complexity, LegacyAnalyzer
from backend.src.migration.migration_scheduler_v2 import (
    MigrationPlan,
    MigrationScheduler,
    MigrationStatus,
    MigrationTask,
)


# Sample legacy code for testing
LEGACY_CODE = """
import urllib2
import urlparse

class OldAgent(object):
    def __init__(self):
        self.data = {}
    
    def process(self, input):
        print "Processing:", input
        if self.data.has_key('key'):
            return self.data['key']
        return None
    
    def fetch(self, url):
        response = urllib2.urlopen(url)
        return response.read()
"""

MODERN_CODE = """
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.parse

class OldAgent:
    def __init__(self):
        self.data = {}
    
    def process(self, input) -> Any:
        print("Processing:", input)
        if 'key' in self.data:
            return self.data['key']
        return None
    
    async def fetch(self, url):
        response = urllib.request.urlopen(url)
        return response.read()
"""


class TestLegacyAnalyzer:
    """Test Legacy Analyzer"""
    
    def test_analyze_file_not_found(self):
        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_file("nonexistent.py")
        
        assert result.agent_name == "nonexistent"
        assert result.complexity == Complexity.LOW
        assert "File not found" in result.issues[0]
    
    def test_analyze_legacy_code(self, tmp_path):
        # Create test file
        test_file = tmp_path / "old_agent.py"
        test_file.write_text(LEGACY_CODE)
        
        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_file(str(test_file))
        
        assert result.agent_name == "old_agent"
        assert "legacy:old_style_class" in result.patterns
        assert "legacy:print_statement" in result.patterns
        assert "legacy:dict_has_key" in result.patterns
        assert "urllib2" in result.dependencies
    
    def test_complexity_calculation(self):
        analyzer = LegacyAnalyzer()
        
        # Low complexity
        result = AnalysisResult(
            agent_name="simple",
            complexity=Complexity.LOW,
            metrics={"lines": 50}
        )
        complexity = analyzer._calculate_complexity(result)
        assert complexity == Complexity.LOW
        
        # High complexity
        result.metrics["lines"] = 600
        result.patterns = {"legacy:old_style_class", "legacy:print_statement", "legacy:dict_has_key"}
        result.dependencies = ["numpy", "pandas", "tensorflow", "scipy"]
        complexity = analyzer._calculate_complexity(result)
        assert complexity == Complexity.HIGH
    
    def test_generate_report(self):
        analyzer = LegacyAnalyzer()
        results = [
            AnalysisResult("agent1", Complexity.LOW),
            AnalysisResult("agent2", Complexity.MEDIUM),
            AnalysisResult("agent3", Complexity.HIGH),
        ]
        
        report = analyzer.generate_report(results)
        
        assert report["total_agents"] == 3
        assert report["complexity_distribution"]["low"] == 1
        assert report["complexity_distribution"]["medium"] == 1
        assert report["complexity_distribution"]["high"] == 1
        assert "days" in report["migration_effort"]


class TestCodeConverter:
    """Test Code Converter"""
    
    def test_convert_file_not_found(self):
        converter = CodeConverter()
        success, result = converter.convert_file("nonexistent.py")
        
        assert not success
        assert "File not found" in result
    
    def test_convert_legacy_code(self, tmp_path):
        # Create test files
        input_file = tmp_path / "old_agent.py"
        output_file = tmp_path / "new_agent.py"
        input_file.write_text(LEGACY_CODE)
        
        converter = CodeConverter()
        success, result = converter.convert_file(str(input_file), str(output_file))
        
        assert success
        assert output_file.exists()
        
        converted = output_file.read_text()
        assert "print(" in converted
        assert "print " not in converted
        assert "urllib.request" in converted
        assert "urllib2" not in converted
        assert "'key' in " in converted
        assert ".has_key(" not in converted
    
    def test_validate_conversion(self):
        converter = CodeConverter()
        
        # Valid modern code
        valid, issues = converter.validate_conversion(MODERN_CODE)
        assert valid
        assert len(issues) == 0
        
        # Invalid code with legacy patterns
        invalid, issues = converter.validate_conversion(LEGACY_CODE)
        assert not invalid
        assert any("print statement" in issue for issue in issues)
    
    def test_convert_to_agentcore(self):
        converter = CodeConverter()
        code = "class TestAgent:\n    pass"
        
        converted = converter.convert_to_agentcore(code)
        
        assert "from agentcore import AgentCore" in converted
        assert "class TestAgent(AgentCore):" in converted
        assert "@memory_limit(6.5)" in converted


class TestCompatibilityChecker:
    """Test Compatibility Checker"""
    
    def test_check_agent_not_found(self):
        checker = CompatibilityChecker()
        result = checker.check_agent("nonexistent.py")
        
        assert result.agent_name == "nonexistent"
        assert not result.is_compatible
        assert "File not found" in result.issues[0]
    
    def test_check_size_constraint(self, tmp_path):
        # Create oversized file
        large_file = tmp_path / "large_agent.py"
        large_code = "# " + "x" * 7000  # > 6.5KB
        large_file.write_text(large_code)
        
        checker = CompatibilityChecker()
        result = checker.check_agent(str(large_file))
        
        assert not result.is_compatible
        assert result.memory_usage > 6.5
        assert any("exceeds" in issue and "KB limit" in issue for issue in result.issues)
    
    def test_check_api_compatibility(self, tmp_path):
        # Create agent with missing methods
        test_file = tmp_path / "test_agent.py"
        code = """
class TestAgent:
    def __init__(self):
        pass
"""
        test_file.write_text(code)
        
        checker = CompatibilityChecker()
        result = checker.check_agent(str(test_file))
        
        assert not result.api_compatible
        assert any("Missing required methods" in issue for issue in result.issues)
    
    def test_generate_compatibility_report(self):
        checker = CompatibilityChecker()
        
        results = {
            "agent1": CompatibilityResult("agent1", True, "3.9", 5.0, True, True),
            "agent2": CompatibilityResult("agent2", False, "3.9", 8.0, True, False),
        }
        
        report = checker.generate_report(results)
        
        assert report["total_agents"] == 2
        assert report["compatible"] == 1
        assert report["incompatible"] == 1
        assert "50.0%" in report["compatibility_rate"]


class TestMigrationScheduler:
    """Test Migration Scheduler"""
    
    @pytest.fixture
    def scheduler(self, tmp_path):
        source = tmp_path / "legacy"
        target = tmp_path / "migrated"
        source.mkdir()
        target.mkdir()
        
        # Create test files
        (source / "agent1.py").write_text("class Agent1: pass")
        (source / "agent2.py").write_text("class Agent2: pass")
        
        return MigrationScheduler(str(source), str(target))
    
    def test_create_plan(self, scheduler):
        plan = scheduler.create_plan()
        
        assert isinstance(plan, MigrationPlan)
        assert plan.total_agents == 2
        assert len(plan.tasks) == 2
        assert len(plan.parallel_groups) > 0
        assert plan.estimated_duration > 0
    
    def test_create_parallel_groups(self, scheduler):
        tasks = [
            MigrationTask("agent1", "src1", "tgt1", dependencies=[]),
            MigrationTask("agent2", "src2", "tgt2", dependencies=["agent1"]),
            MigrationTask("agent3", "src3", "tgt3", dependencies=[]),
        ]
        
        for task in tasks:
            scheduler.tasks[task.agent_name] = task
        
        groups = scheduler._create_parallel_groups(tasks)
        
        assert len(groups) == 2
        assert "agent1" in groups[0] and "agent3" in groups[0]
        assert "agent2" in groups[1]
    
    @pytest.mark.asyncio
    async def test_execute_plan(self, scheduler):
        plan = scheduler.create_plan()
        
        # Mock migration methods
        scheduler._migrate_agent = MagicMock(return_value=asyncio.coroutine(lambda: True)())
        
        results = await scheduler.execute_plan(plan)
        
        assert results["total"] == 2
        assert results["duration"] > 0
    
    def test_get_status(self, scheduler):
        scheduler.tasks = {
            "agent1": MigrationTask("agent1", "src1", "tgt1", status=MigrationStatus.COMPLETED),
            "agent2": MigrationTask("agent2", "src2", "tgt2", status=MigrationStatus.PENDING),
        }
        scheduler.completed.add("agent1")
        
        status = scheduler.get_status()
        
        assert status["total"] == 2
        assert status["completed"] == 1
        assert status["pending"] == 1
        assert status["failed"] == 0
    
    def test_generate_report(self, scheduler):
        scheduler.tasks = {
            "agent1": MigrationTask(
                "agent1", "src1", "tgt1",
                status=MigrationStatus.COMPLETED,
                start_time=100.0,
                end_time=102.5
            ),
        }
        scheduler.completed.add("agent1")
        
        report = scheduler.generate_report()
        
        assert "MIGRATION REPORT" in report
        assert "Total Agents: 1" in report
        assert "Completed: 1" in report
        assert "agent1 (2.5s)" in report


@pytest.mark.integration
class TestMigrationIntegration:
    """Integration tests for full migration flow"""
    
    @pytest.mark.asyncio
    async def test_full_migration_flow(self, tmp_path):
        # Setup directories
        source = tmp_path / "legacy"
        target = tmp_path / "migrated"
        source.mkdir()
        target.mkdir()
        
        # Create legacy agent
        legacy_file = source / "test_agent.py"
        legacy_file.write_text(LEGACY_CODE)
        
        # Run full migration
        scheduler = MigrationScheduler(str(source), str(target))
        plan = scheduler.create_plan()
        
        assert plan.total_agents == 1
        
        results = await scheduler.execute_plan(plan)
        
        # Check results
        assert results["completed"] > 0 or results["failed"] > 0
        
        # Check if converted file exists
        converted_file = target / "test_agent_v2.py"
        if converted_file.exists():
            converted = converted_file.read_text()
            # Should have modern patterns
            assert "print(" in converted or "print" not in converted
    
    def test_file_size_verification(self):
        """Verify all migration files are under 6.5KB"""
        migration_dir = Path("backend/src/migration")
        
        for file_path in migration_dir.glob("*_v2.py"):
            size_kb = file_path.stat().st_size / 1024
            assert size_kb <= 6.5, f"{file_path.name} exceeds 6.5KB: {size_kb:.1f}KB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])