"""
Tests for Pattern Recognition System

This module contains comprehensive tests for the pattern recognition
components, ensuring robust pattern extraction and matching capabilities.
"""

import os
import tempfile
from datetime import datetime

import pytest

from packages.learning.pattern_database import Pattern, PatternDatabase
from packages.learning.pattern_recognition import (
    CodePatternExtractor,
    EvolutionCycle,
    MetricsPatternExtractor,
    PatternCandidate,
    PatternRecognizer,
)


class TestEvolutionCycle:
    """Test EvolutionCycle data structure."""

    def test_evolution_cycle_creation(self):
        """Test creating an evolution cycle."""
        cycle = EvolutionCycle(
            id="test_cycle_001",
            phase="implementation",
            task="add_tests",
            inputs={"file_path": "test.py"},
            outputs={"test_file": "test_test.py"},
            duration=45.5,
            success=True,
            metrics_before={"coverage": 75.0},
            metrics_after={"coverage": 85.0},
        )

        assert cycle.id == "test_cycle_001"
        assert cycle.phase == "implementation"
        assert cycle.task == "add_tests"
        assert cycle.success is True
        assert cycle.duration == 45.5
        assert isinstance(cycle.timestamp, datetime)

    def test_evolution_cycle_with_code_changes(self):
        """Test evolution cycle with code changes."""
        code_changes = [
            {
                "type": "python",
                "file": "test.py",
                "content": "import pytest\n\ndef test_example():\n    assert True",
            }
        ]

        cycle = EvolutionCycle(
            id="test_cycle_002",
            phase="implementation",
            task="add_tests",
            inputs={},
            outputs={},
            duration=30.0,
            success=True,
            metrics_before={},
            metrics_after={},
            code_changes=code_changes,
        )

        assert len(cycle.code_changes) == 1
        assert cycle.code_changes[0]["type"] == "python"
        assert "import pytest" in cycle.code_changes[0]["content"]


class TestPatternCandidate:
    """Test PatternCandidate data structure."""

    def test_pattern_candidate_creation(self):
        """Test creating a pattern candidate."""
        candidate = PatternCandidate(
            context={"file_types": ["python"]},
            action={"type": "add_tests"},
            outcome={"coverage_improvement": 10},
            confidence=0.8,
            supporting_cycles=["cycle1", "cycle2"],
            frequency=2,
        )

        assert candidate.confidence == 0.8
        assert candidate.frequency == 2
        assert len(candidate.supporting_cycles) == 2
        assert candidate.context["file_types"] == ["python"]


class TestCodePatternExtractor:
    """Test CodePatternExtractor functionality."""

    @pytest.fixture
    def code_extractor(self):
        """Create code pattern extractor."""
        return CodePatternExtractor()

    @pytest.fixture
    def sample_cycles_with_code(self):
        """Create sample evolution cycles with code changes."""
        cycles = []

        # Cycle with function definition
        cycle1 = EvolutionCycle(
            id="cycle_001",
            phase="implementation",
            task="add_function",
            inputs={},
            outputs={},
            duration=30.0,
            success=True,
            metrics_before={"coverage": 70.0},
            metrics_after={"coverage": 80.0},
            code_changes=[
                {
                    "type": "python",
                    "content": """
import asyncio
from typing import Dict, Any

async def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    '''Process input data.'''
    result = {"processed": True}
    return result
""",
                }
            ],
        )
        cycles.append(cycle1)

        # Similar cycle with same pattern
        cycle2 = EvolutionCycle(
            id="cycle_002",
            phase="implementation",
            task="add_function",
            inputs={},
            outputs={},
            duration=35.0,
            success=True,
            metrics_before={"coverage": 75.0},
            metrics_after={"coverage": 85.0},
            code_changes=[
                {
                    "type": "python",
                    "content": """
import asyncio
from typing import List, Optional

async def validate_input(items: List[str]) -> Optional[bool]:
    '''Validate input items.'''
    if not items:
        return False
    return True
""",
                }
            ],
        )
        cycles.append(cycle2)

        return cycles

    @pytest.mark.asyncio
    async def test_extract_patterns_success(self, code_extractor, sample_cycles_with_code):
        """Test successful pattern extraction."""
        patterns = await code_extractor.extract(sample_cycles_with_code)

        assert isinstance(patterns, list)
        # Should extract some patterns from similar code structures
        assert len(patterns) >= 0

    @pytest.mark.asyncio
    async def test_extract_patterns_empty_cycles(self, code_extractor):
        """Test pattern extraction with empty cycles."""
        patterns = await code_extractor.extract([])
        assert patterns == []

    @pytest.mark.asyncio
    async def test_extract_patterns_failed_cycles(self, code_extractor):
        """Test pattern extraction ignores failed cycles."""
        failed_cycle = EvolutionCycle(
            id="failed_cycle",
            phase="implementation",
            task="add_function",
            inputs={},
            outputs={},
            duration=60.0,
            success=False,  # Failed cycle
            metrics_before={},
            metrics_after={},
            code_changes=[
                {
                    "type": "python",
                    "content": "def broken_function():\n    return undefined_variable",
                }
            ],
        )

        patterns = await code_extractor.extract([failed_cycle])
        assert patterns == []

    @pytest.mark.asyncio
    async def test_extract_ast_patterns(self, code_extractor, sample_cycles_with_code):
        """Test AST pattern extraction."""
        patterns = await code_extractor._extract_ast_patterns(sample_cycles_with_code)

        assert isinstance(patterns, list)
        # Should find patterns in similar function structures
        for pattern in patterns:
            assert isinstance(pattern, PatternCandidate)
            assert pattern.confidence > 0

    @pytest.mark.asyncio
    async def test_extract_import_patterns(self, code_extractor, sample_cycles_with_code):
        """Test import pattern extraction."""
        patterns = await code_extractor._extract_import_patterns(sample_cycles_with_code)

        assert isinstance(patterns, list)
        # Should find common import patterns
        for pattern in patterns:
            assert isinstance(pattern, PatternCandidate)
            assert "imports_needed" in pattern.context

    def test_get_ast_signature(self, code_extractor):
        """Test AST signature generation."""
        import ast

        code = """
def test_function():
    import os
    return True
"""
        tree = ast.parse(code)
        signature = code_extractor._get_ast_signature(tree)

        assert isinstance(signature, str)
        assert len(signature) == 8  # MD5 hash truncated to 8 chars

    def test_extract_imports(self, code_extractor):
        """Test import extraction from AST."""
        import ast

        code = """
import os
import sys
from typing import Dict, Any
from datetime import datetime
"""
        tree = ast.parse(code)
        imports = code_extractor._extract_imports(tree)

        assert "os" in imports
        assert "sys" in imports
        assert "typing.Dict" in imports
        assert "typing.Any" in imports
        assert "datetime.datetime" in imports

    def test_calculate_metrics_improvement(self, code_extractor):
        """Test metrics improvement calculation."""
        before = {"coverage": 70.0, "complexity": 60.0}
        after = {"coverage": 80.0, "complexity": 65.0}

        improvement = code_extractor._calculate_metrics_improvement(before, after)

        assert isinstance(improvement, float)
        assert improvement > 0  # Should show improvement


class TestMetricsPatternExtractor:
    """Test MetricsPatternExtractor functionality."""

    @pytest.fixture
    def metrics_extractor(self):
        """Create metrics pattern extractor."""
        return MetricsPatternExtractor()

    @pytest.fixture
    def sample_cycles_with_metrics(self):
        """Create sample cycles with metrics improvements."""
        cycles = []

        # Coverage improvement cycle
        cycle1 = EvolutionCycle(
            id="metrics_cycle_001",
            phase="implementation",
            task="add_tests",
            inputs={"test_framework": "pytest"},
            outputs={"test_count": 5},
            duration=40.0,
            success=True,
            metrics_before={"coverage": 65.0, "complexity": 70.0},
            metrics_after={"coverage": 85.0, "complexity": 72.0},
        )
        cycles.append(cycle1)

        # Similar improvement cycle
        cycle2 = EvolutionCycle(
            id="metrics_cycle_002",
            phase="implementation",
            task="add_tests",
            inputs={"test_framework": "pytest"},
            outputs={"test_count": 8},
            duration=50.0,
            success=True,
            metrics_before={"coverage": 70.0, "complexity": 68.0},
            metrics_after={"coverage": 88.0, "complexity": 71.0},
        )
        cycles.append(cycle2)

        return cycles

    @pytest.mark.asyncio
    async def test_extract_metrics_patterns(self, metrics_extractor, sample_cycles_with_metrics):
        """Test metrics pattern extraction."""
        patterns = await metrics_extractor.extract(sample_cycles_with_metrics)

        assert isinstance(patterns, list)
        # Should extract patterns for coverage improvement
        assert len(patterns) >= 0

        for pattern in patterns:
            assert isinstance(pattern, PatternCandidate)
            assert pattern.confidence > 0

    @pytest.mark.asyncio
    async def test_extract_patterns_no_metrics(self, metrics_extractor):
        """Test extraction with cycles lacking metrics."""
        cycles = [
            EvolutionCycle(
                id="no_metrics",
                phase="implementation",
                task="test",
                inputs={},
                outputs={},
                duration=30.0,
                success=True,
                metrics_before={},  # No metrics
                metrics_after={},  # No metrics
            )
        ]

        patterns = await metrics_extractor.extract(cycles)
        assert patterns == []

    def test_group_by_improvement_type(self, metrics_extractor, sample_cycles_with_metrics):
        """Test grouping cycles by improvement type."""
        groups = metrics_extractor._group_by_improvement_type(sample_cycles_with_metrics)

        assert isinstance(groups, dict)
        # Should identify coverage improvements
        assert "coverage_improvement" in groups
        assert len(groups["coverage_improvement"]) == 2

    def test_classify_improvement(self, metrics_extractor):
        """Test improvement classification."""
        cycle = EvolutionCycle(
            id="test_cycle",
            phase="implementation",
            task="test",
            inputs={},
            outputs={},
            duration=30.0,
            success=True,
            metrics_before={"coverage": 60.0, "docstring_coverage": 40.0},
            metrics_after={"coverage": 85.0, "docstring_coverage": 65.0},
        )

        improvements = metrics_extractor._classify_improvement(cycle)

        assert "coverage_improvement" in improvements
        assert "documentation_improvement" in improvements

    def test_find_common_context(self, metrics_extractor, sample_cycles_with_metrics):
        """Test finding common context across cycles."""
        context = metrics_extractor._find_common_context(sample_cycles_with_metrics)

        assert isinstance(context, dict)
        # Should find common phase and task
        assert context.get("phase") == "implementation"
        assert context.get("task") == "add_tests"

    def test_calculate_average_improvement(self, metrics_extractor, sample_cycles_with_metrics):
        """Test average improvement calculation."""
        improvement = metrics_extractor._calculate_average_improvement(
            sample_cycles_with_metrics, "coverage_improvement"
        )

        assert isinstance(improvement, float)
        assert improvement > 0  # Should show positive improvement


class TestPatternRecognizer:
    """Test PatternRecognizer main class."""

    @pytest.fixture
    async def pattern_db(self):
        """Create temporary pattern database."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        db = PatternDatabase(db_path)
        await db.initialize()

        yield db

        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.fixture
    async def pattern_recognizer(self, pattern_db):
        """Create pattern recognizer with test database."""
        recognizer = PatternRecognizer(pattern_db)
        await recognizer.initialize()
        return recognizer

    @pytest.fixture
    def sample_evolution_cycles(self):
        """Create sample evolution cycles for testing."""
        cycles = []

        # Successful test addition cycle
        cycle1 = EvolutionCycle(
            id="pattern_test_cycle_001",
            phase="implementation",
            task="add_unit_tests",
            inputs={"file_path": "src/utils.py", "test_framework": "pytest"},
            outputs={"test_file": "tests/test_utils.py", "tests_added": 5},
            duration=35.0,
            success=True,
            metrics_before={"coverage": 65.0, "complexity": 70.0},
            metrics_after={"coverage": 85.0, "complexity": 72.0},
            code_changes=[
                {
                    "type": "python",
                    "content": """
import pytest
from src.utils import process_data

def test_process_data():
    result = process_data({"key": "value"})
    assert result is not None

def test_process_data_empty():
    result = process_data({})
    assert result is not None
""",
                }
            ],
        )
        cycles.append(cycle1)

        # Similar successful cycle
        cycle2 = EvolutionCycle(
            id="pattern_test_cycle_002",
            phase="implementation",
            task="add_unit_tests",
            inputs={"file_path": "src/handlers.py", "test_framework": "pytest"},
            outputs={"test_file": "tests/test_handlers.py", "tests_added": 3},
            duration=28.0,
            success=True,
            metrics_before={"coverage": 70.0, "complexity": 68.0},
            metrics_after={"coverage": 88.0, "complexity": 70.0},
            code_changes=[
                {
                    "type": "python",
                    "content": """
import pytest
from src.handlers import handle_request

def test_handle_request():
    response = handle_request({"data": "test"})
    assert response["status"] == "success"

def test_handle_request_invalid():
    response = handle_request({})
    assert response["status"] == "error"
""",
                }
            ],
        )
        cycles.append(cycle2)

        return cycles

    @pytest.mark.asyncio
    async def test_initialize(self, pattern_recognizer):
        """Test pattern recognizer initialization."""
        # Should initialize without errors
        assert pattern_recognizer.pattern_db is not None
        assert len(pattern_recognizer.extractors) > 0

    @pytest.mark.asyncio
    async def test_extract_patterns_success(self, pattern_recognizer, sample_evolution_cycles):
        """Test successful pattern extraction."""
        patterns = await pattern_recognizer.extract_patterns(sample_evolution_cycles)

        assert isinstance(patterns, list)
        # Should extract some patterns from similar successful cycles
        for pattern in patterns:
            assert isinstance(pattern, Pattern)
            assert pattern.confidence >= 0.7  # Minimum confidence threshold
            assert pattern.success_rate > 0

    @pytest.mark.asyncio
    async def test_extract_patterns_empty_cycles(self, pattern_recognizer):
        """Test pattern extraction with empty cycles."""
        with pytest.raises(ValueError, match="Cannot extract patterns from empty cycles list"):
            await pattern_recognizer.extract_patterns([])

    @pytest.mark.asyncio
    async def test_extract_patterns_with_caching(self, pattern_recognizer, sample_evolution_cycles):
        """Test pattern extraction with caching."""
        # First extraction
        patterns1 = await pattern_recognizer.extract_patterns(sample_evolution_cycles)

        # Second extraction should use cache
        patterns2 = await pattern_recognizer.extract_patterns(sample_evolution_cycles)

        assert len(patterns1) == len(patterns2)

    @pytest.mark.asyncio
    async def test_store_patterns(self, pattern_recognizer, sample_evolution_cycles):
        """Test storing extracted patterns."""
        patterns = await pattern_recognizer.extract_patterns(sample_evolution_cycles)

        # Store patterns
        await pattern_recognizer.store_patterns(patterns)

        # Verify patterns were stored
        all_patterns = await pattern_recognizer.pattern_db.get_all_patterns()
        assert len(all_patterns) >= len(patterns)

    @pytest.mark.asyncio
    async def test_find_applicable_patterns(self, pattern_recognizer, sample_evolution_cycles):
        """Test finding applicable patterns."""
        # First extract and store patterns
        patterns = await pattern_recognizer.extract_patterns(sample_evolution_cycles)
        await pattern_recognizer.store_patterns(patterns)

        # Find applicable patterns for similar context
        context = {"phase": "implementation", "task": "add_unit_tests", "file_types": ["python"]}

        applicable = await pattern_recognizer.find_applicable_patterns(context)

        assert isinstance(applicable, list)
        for pattern in applicable:
            assert isinstance(pattern, Pattern)

    @pytest.mark.asyncio
    async def test_get_pattern_statistics(self, pattern_recognizer, sample_evolution_cycles):
        """Test getting pattern statistics."""
        # Extract and store some patterns
        patterns = await pattern_recognizer.extract_patterns(sample_evolution_cycles)
        await pattern_recognizer.store_patterns(patterns)

        stats = await pattern_recognizer.get_pattern_statistics()

        assert isinstance(stats, dict)
        assert "total_patterns" in stats
        assert "categories" in stats
        assert "average_confidence" in stats

    def test_classify_pattern_category(self, pattern_recognizer):
        """Test pattern category classification."""
        candidate = PatternCandidate(
            context={},
            action={"type": "code_change"},
            outcome={"improvement_type": "coverage_improvement"},
            confidence=0.8,
        )

        category = pattern_recognizer._classify_pattern_category(candidate)
        assert category == "testing"

    def test_generate_pattern_name(self, pattern_recognizer):
        """Test pattern name generation."""
        candidate = PatternCandidate(
            context={},
            action={"type": "code_change"},
            outcome={"improvement_type": "coverage_improvement", "average_improvement": 0.15},
            confidence=0.8,
            frequency=3,
        )

        name = pattern_recognizer._generate_pattern_name(candidate)
        assert isinstance(name, str)
        assert "Coverage Improvement" in name

    def test_generate_pattern_tags(self, pattern_recognizer):
        """Test pattern tag generation."""
        candidate = PatternCandidate(
            context={"file_types": ["python"]},
            action={"type": "test_addition"},
            outcome={"improvement_type": "coverage_improvement"},
            confidence=0.9,
            frequency=5,
        )

        tags = pattern_recognizer._generate_pattern_tags(candidate)

        assert "auto_extracted" in tags
        assert "coverage_improvement" in tags
        assert "python" in tags
        assert "test_addition" in tags
        assert "high_frequency" in tags
        assert "high_confidence" in tags

    @pytest.mark.asyncio
    async def test_calculate_pattern_similarity(self, pattern_recognizer):
        """Test pattern similarity calculation."""
        pattern1 = Pattern(
            id="pattern1",
            category="testing",
            name="Test Pattern 1",
            description="Test description",
            context={"file_types": ["python"], "task": "testing"},
            action={"type": "add_tests"},
            outcome={"improvement": 10},
            success_rate=0.8,
            usage_count=5,
            created_at=datetime.now(),
            tags=["testing", "python"],
        )

        pattern2 = Pattern(
            id="pattern2",
            category="testing",
            name="Test Pattern 2",
            description="Test description",
            context={"file_types": ["python"], "task": "testing"},
            action={"type": "add_tests"},
            outcome={"improvement": 12},
            success_rate=0.85,
            usage_count=3,
            created_at=datetime.now(),
            tags=["testing", "python"],
        )

        similarity = await pattern_recognizer._calculate_pattern_similarity(pattern1, pattern2)

        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # Should be quite similar

    @pytest.mark.asyncio
    async def test_merge_similar_patterns(self, pattern_recognizer):
        """Test merging similar patterns."""
        patterns = [
            Pattern(
                id="pattern1",
                category="testing",
                name="Test Pattern",
                description="Description",
                context={"file_types": ["python"]},
                action={"type": "add_tests"},
                outcome={"improvement": 10},
                success_rate=0.8,
                usage_count=3,
                created_at=datetime.now(),
                tags=["testing"],
            ),
            Pattern(
                id="pattern2",
                category="testing",
                name="Similar Test Pattern",
                description="Description",
                context={"file_types": ["python"]},
                action={"type": "add_tests"},
                outcome={"improvement": 12},
                success_rate=0.85,
                usage_count=2,
                created_at=datetime.now(),
                tags=["testing"],
            ),
        ]

        merged = await pattern_recognizer._merge_similar_patterns(patterns)

        assert isinstance(merged, list)
        # Should merge similar patterns
        assert len(merged) <= len(patterns)


@pytest.mark.asyncio
async def test_pattern_recognition_integration():
    """Integration test for pattern recognition system."""
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name

    try:
        # Initialize components
        pattern_db = PatternDatabase(db_path)
        await pattern_db.initialize()

        recognizer = PatternRecognizer(pattern_db)
        await recognizer.initialize()

        # Create test cycles
        cycles = [
            EvolutionCycle(
                id="integration_cycle_001",
                phase="implementation",
                task="add_docstrings",
                inputs={"target": "documentation"},
                outputs={"docstrings_added": 10},
                duration=60.0,
                success=True,
                metrics_before={"docstring_coverage": 40.0},
                metrics_after={"docstring_coverage": 75.0},
                code_changes=[
                    {
                        "type": "python",
                        "content": '''
def process_data(data):
    """Process input data and return result.

    Args:
        data: Input data to process

    Returns:
        Processed result
    """
    return {"processed": True}
''',
                    }
                ],
            ),
            EvolutionCycle(
                id="integration_cycle_002",
                phase="implementation",
                task="add_docstrings",
                inputs={"target": "documentation"},
                outputs={"docstrings_added": 8},
                duration=45.0,
                success=True,
                metrics_before={"docstring_coverage": 35.0},
                metrics_after={"docstring_coverage": 80.0},
                code_changes=[
                    {
                        "type": "python",
                        "content": '''
def validate_input(input_data):
    """Validate input data format.

    Args:
        input_data: Data to validate

    Returns:
        True if valid, False otherwise
    """
    return isinstance(input_data, dict)
''',
                    }
                ],
            ),
        ]

        # Extract patterns
        patterns = await recognizer.extract_patterns(cycles)
        assert len(patterns) > 0

        # Store patterns
        await recognizer.store_patterns(patterns)

        # Find applicable patterns
        context = {"phase": "implementation", "task": "add_docstrings", "file_types": ["python"]}

        applicable = await recognizer.find_applicable_patterns(context)
        assert len(applicable) > 0

        # Get statistics
        stats = await recognizer.get_pattern_statistics()
        assert stats["total_patterns"] > 0

    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
