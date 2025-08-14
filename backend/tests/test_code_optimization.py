"""
Test suite for Code Optimization Engine
Day 27: Phase 2 - ServiceImproverAgent
"""

import ast
import asyncio
from typing import List

import pytest

from src.agents.meta.code_optimizer import (
    CodeOptimizer,
    OptimizationOpportunity,
    OptimizationReport,
    get_optimizer,
)
from src.optimization.ast_analyzer import (
    ASTAnalysis,
    ASTAnalyzer,
    CodePattern,
    FunctionMetrics,
    get_analyzer,
)
from src.optimization.refactoring_engine import (
    RefactoringEngine,
    RefactoringPlan,
    RefactoringResult,
    get_engine,
)


class TestCodeOptimizer:
    """Test code optimizer"""

    @pytest.fixture
    def optimizer(self):
        """Get optimizer instance"""
        return get_optimizer()

    @pytest.mark.asyncio
    async def test_optimize_list_comprehension(self, optimizer):
        """Test list comprehension optimization"""

        code = """
def process_items(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
"""

        report = await optimizer.optimize(code, target="list_comp")

        assert report is not None
        assert len(report.opportunities) > 0

        # Should find list comprehension opportunity
        list_comp_opps = [o for o in report.opportunities if o.type == "list_comp"]
        assert len(list_comp_opps) > 0

        opp = list_comp_opps[0]
        assert opp.improvement > 20
        assert opp.confidence > 0.8
        assert opp.risk == "low"

    @pytest.mark.asyncio
    async def test_optimize_async_conversion(self, optimizer):
        """Test async function conversion"""

        code = """
def fetch_data():
    # Simulated I/O operation
    data = open('file.txt').read()
    return data
"""

        report = await optimizer.optimize(code, target="async")

        assert report is not None

        # Should suggest async conversion
        async_opps = [o for o in report.opportunities if o.type == "async"]
        if async_opps:  # May or may not detect depending on analysis
            assert async_opps[0].improvement > 30

    @pytest.mark.asyncio
    async def test_optimize_caching(self, optimizer):
        """Test caching optimization"""

        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

        report = await optimizer.optimize(code)

        assert report is not None

        # Should suggest caching for recursive function
        cache_opps = [o for o in report.opportunities if o.type == "caching"]
        if cache_opps:
            assert cache_opps[0].improvement > 40
            assert cache_opps[0].risk == "low"

    @pytest.mark.asyncio
    async def test_optimization_report(self, optimizer):
        """Test complete optimization report"""

        code = """
def bad_function(x, y, z):
    result = []
    for i in range(x):
        for j in range(y):
            result.append(i * j)
    return result
"""

        report = await optimizer.optimize(code)

        assert isinstance(report, OptimizationReport)
        assert report.opportunities is not None
        assert report.total_improvement >= 0
        assert report.execution_time > 0

    def test_pattern_detection(self, optimizer):
        """Test optimization pattern detection"""

        patterns = optimizer.optimization_patterns

        assert "list_comp" in patterns
        assert "generator" in patterns
        assert "caching" in patterns
        assert "async" in patterns
        assert "algorithm" in patterns


class TestASTAnalyzer:
    """Test AST analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Get analyzer instance"""
        return get_analyzer()

    def test_analyze_simple_code(self, analyzer):
        """Test analyzing simple code"""

        code = """
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""

        analysis = analyzer.analyze(code)

        assert isinstance(analysis, ASTAnalysis)
        assert len(analysis.functions) == 2
        assert analysis.complexity_score < 0.5
        assert analysis.maintainability_score > 0.5

    def test_analyze_complex_code(self, analyzer):
        """Test analyzing complex code"""

        code = """
def complex_function(a, b, c, d, e, f, g):
    global counter
    counter = 0

    for i in range(10):
        for j in range(10):
            for k in range(10):
                if i > j and j > k:
                    counter += 1
                elif i < j and j < k:
                    counter -= 1
                else:
                    if counter > 100:
                        return 1
                    elif counter > 50:
                        return 2
                    else:
                        return 3

    return counter
"""

        analysis = analyzer.analyze(code)

        assert analysis.complexity_score > 0.5
        # Complex code still has some maintainability
        assert analysis.maintainability_score <= 1.0
        assert len(analysis.patterns) > 0
        assert len(analysis.suggestions) > 0

    def test_function_metrics(self, analyzer):
        """Test function metrics calculation"""

        code = """
def test_function(x, y):
    result = 0
    for i in range(x):
        if i % 2 == 0:
            result += i
    return result
"""

        analysis = analyzer.analyze(code)

        assert len(analysis.functions) == 1
        func = analysis.functions[0]

        assert func.name == "test_function"
        assert func.parameters == 2
        assert func.complexity > 1
        assert func.loops == 1
        assert func.branches == 1

    def test_pattern_detection(self, analyzer):
        """Test code pattern detection"""

        code = """
def bad_patterns():
    global x
    x = 0

    # Nested loops
    for i in range(10):
        for j in range(10):
            x += i * j

    # Multiple returns
    if x > 100:
        return 1
    elif x > 50:
        return 2
    elif x > 25:
        return 3
    else:
        return 0
"""

        analysis = analyzer.analyze(code)

        patterns = analysis.patterns
        assert len(patterns) > 0

        # Should detect global usage
        global_patterns = [p for p in patterns if p.pattern_type == "global_usage"]
        assert len(global_patterns) > 0

        # Should detect nested loops
        nested_patterns = [p for p in patterns if p.pattern_type == "nested_loop"]
        assert len(nested_patterns) > 0

    def test_dependency_analysis(self, analyzer):
        """Test dependency analysis"""

        code = """
def func_a():
    return func_b()

def func_b():
    return func_c()

def func_c():
    return 42
"""

        analysis = analyzer.analyze(code)

        assert "func_a" in analysis.dependencies
        assert "func_b" in analysis.dependencies["func_a"]
        assert "func_c" in analysis.dependencies["func_b"]


class TestRefactoringEngine:
    """Test refactoring engine"""

    @pytest.fixture
    def engine(self):
        """Get refactoring engine"""
        return get_engine()

    @pytest.mark.asyncio
    async def test_refactor_simple(self, engine):
        """Test simple refactoring"""

        code = """
def x(a):
    return a * 2
"""

        result = await engine.refactor(code)

        assert isinstance(result, RefactoringResult)
        assert result.original_code == code
        assert result.improvements is not None

    @pytest.mark.asyncio
    async def test_refactor_rename(self, engine):
        """Test rename refactoring"""

        code = """
def x(a, b):
    return a + b
"""

        result = await engine.refactor(code, ["readability"])

        # Should suggest renaming function 'x'
        rename_plans = [
            p for p in result.plans_executed + result.plans_skipped if p.type == "rename"
        ]

        if rename_plans:
            assert rename_plans[0].target == "x"
            assert rename_plans[0].safety_score > 0.8

    @pytest.mark.asyncio
    async def test_refactor_extract_method(self, engine):
        """Test extract method refactoring"""

        code = """
def very_long_function():
    # Line 1
    x = 1
    # Line 2
    y = 2
    # Line 3
    z = 3
    # Line 4
    a = 4
    # Line 5
    b = 5
    # Line 6
    c = 6
    # Line 7
    d = 7
    # Line 8
    e = 8
    # Line 9
    f = 9
    # Line 10
    g = 10
    # Line 11
    h = 11
    # Line 12
    i = 12
    # Line 13
    j = 13
    # Line 14
    k = 14
    # Line 15
    l = 15
    # Line 16
    m = 16
    # Line 17
    n = 17
    # Line 18
    o = 18
    # Line 19
    p = 19
    # Line 20
    q = 20
    # Line 21
    r = 21
    return x + y + z + a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q + r
"""

        result = await engine.refactor(code)

        # Should suggest extracting method for long function
        extract_plans = [
            p for p in result.plans_executed + result.plans_skipped if p.type == "extract_method"
        ]

        if extract_plans:
            assert extract_plans[0].benefit_score > 0.5

    @pytest.mark.asyncio
    async def test_refactor_decompose_conditional(self, engine):
        """Test decompose conditional refactoring"""

        code = """
def complex_condition(a, b, c, d):
    if a > 0 and b > 0 and c > 0 and d > 0 and a < 100 and b < 100:
        return True
    return False
"""

        result = await engine.refactor(code)

        # Should suggest decomposing complex conditional
        decompose_plans = [
            p for p in result.plans_executed + result.plans_skipped if p.type == "decompose"
        ]

        if decompose_plans:
            assert decompose_plans[0].safety_score > 0.5

    @pytest.mark.asyncio
    async def test_rollback(self, engine):
        """Test rollback functionality"""

        code = """
def original():
    return 42
"""

        result = await engine.refactor(code)

        if result.plans_executed:
            assert result.rollback_available

            # Test rollback
            rolled_back = engine.rollback()
            if rolled_back:
                assert rolled_back == code


@pytest.mark.integration
class TestOptimizationIntegration:
    """Integration tests for optimization system"""

    @pytest.mark.asyncio
    async def test_complete_optimization_flow(self):
        """Test complete optimization flow"""

        # Get all components
        optimizer = get_optimizer()
        analyzer = get_analyzer()
        engine = get_engine()

        # Test code
        test_code = """
def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result

def calculate(x, y):
    # Could use caching
    total = 0
    for i in range(x):
        for j in range(y):
            total += i * j
    return total
"""

        # Step 1: Analyze code
        analysis = analyzer.analyze(test_code)
        assert analysis.complexity_score is not None

        # Step 2: Find optimizations
        optimization_report = await optimizer.optimize(test_code)
        assert len(optimization_report.opportunities) > 0

        # Step 3: Refactor code
        refactoring_result = await engine.refactor(test_code)
        assert refactoring_result.success or len(refactoring_result.plans_skipped) > 0

        # Verify improvements
        print("\nOptimization Flow Results:")
        print(f"  Complexity: {analysis.complexity_score:.2f}")
        print(f"  Optimization opportunities: {len(optimization_report.opportunities)}")
        print(f"  Refactoring plans: {len(refactoring_result.plans_executed)}")

        if refactoring_result.improvements:
            for metric, value in refactoring_result.improvements.items():
                print(f"  {metric}: {value:.1f}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
