"""
Test suite for ServiceImprover Integration
Day 30: Phase 2 - ServiceImproverAgent Integration Tests
"""

import asyncio
from typing import Dict, List

import pytest

from src.agents.meta.service_improver import (
    ImprovementSuggestion,
    ServiceAnalysis,
    ServiceImprover,
    get_improver,
)


class TestServiceImprover:
    """Test ServiceImprover orchestrator"""
    
    @pytest.fixture
    def improver(self):
        """Get improver instance"""
        return get_improver()
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self, improver):
        """Test complete service analysis"""
        
        test_code = """
def inefficient_function(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

password = "weak123"  # Security issue
eval(user_input)  # Critical vulnerability
"""
        
        test_metrics = {
            "performance": 0.6,
            "reliability": 0.8,
            "users": 1000,
            "response_time": 300,
            "uptime": 0.95,
            "error_rate": 0.05
        }
        
        test_feedback = [
            {"rating": 3.0, "category": "performance"},
            {"rating": 4.0, "category": "usability"}
        ]
        
        analysis = await improver.analyze_service(test_code, test_metrics, test_feedback)
        
        assert isinstance(analysis, ServiceAnalysis)
        assert 0 <= analysis.quality_score <= 100
        assert 0 <= analysis.performance_score <= 100
        assert 0 <= analysis.security_score <= 100
        assert analysis.business_value >= 0
        assert 0 <= analysis.user_satisfaction <= 100
        assert len(analysis.improvement_opportunities) > 0
        assert analysis.total_improvement_potential > 0
    
    @pytest.mark.asyncio
    async def test_quality_analysis_integration(self, improver):
        """Test quality analysis integration"""
        
        code = """
def complex_function(a, b, c, d, e, f):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return f * 2
    return 0
"""
        
        result = await improver._analyze_code_quality(code)
        
        assert "score" in result
        assert "issues" in result
        assert "recommendations" in result
        assert result["score"] < 80  # Should detect complexity
    
    @pytest.mark.asyncio
    async def test_performance_analysis_integration(self, improver):
        """Test performance analysis integration"""
        
        code = """
def slow_function(n):
    result = []
    for i in range(n):
        for j in range(n):
            result.append(i * j)
    return result
"""
        
        result = await improver._analyze_performance(code)
        
        assert "score" in result
        assert "bottlenecks" in result
        assert "optimizations" in result
        assert isinstance(result["score"], (int, float))
    
    @pytest.mark.asyncio
    async def test_security_analysis_integration(self, improver):
        """Test security analysis integration"""
        
        vulnerable_code = """
import os
password = "admin123"
def execute(cmd):
    os.system(cmd)
    eval(cmd)
"""
        
        result = await improver._analyze_security(vulnerable_code)
        
        assert "risk_score" in result
        assert "vulnerabilities" in result
        assert "compliance" in result
        assert "recommendations" in result
        assert result["risk_score"] > 30  # Should detect vulnerabilities
        assert len(result["vulnerabilities"]) > 0
    
    @pytest.mark.asyncio
    async def test_bottleneck_detection_integration(self, improver):
        """Test bottleneck detection integration"""
        
        bottlenecks = await improver._analyze_bottlenecks()
        
        assert isinstance(bottlenecks, list)
        for bottleneck in bottlenecks:
            assert "type" in bottleneck
            assert "severity" in bottleneck
            assert "component" in bottleneck
            assert "description" in bottleneck
            assert "action" in bottleneck
    
    @pytest.mark.asyncio
    async def test_business_value_integration(self, improver):
        """Test business value analysis integration"""
        
        metrics = {
            "performance": 0.7,
            "reliability": 0.85,
            "users": 5000,
            "revenue_per_user": 15
        }
        
        result = await improver._analyze_business_value(metrics)
        
        assert "roi" in result
        assert "cost_reduction" in result
        assert "efficiency_gain" in result
        assert all(isinstance(v, (int, float)) for v in result.values())
    
    @pytest.mark.asyncio
    async def test_satisfaction_analysis_integration(self, improver):
        """Test user satisfaction analysis integration"""
        
        metrics = {
            "response_time": 150,
            "uptime": 0.99,
            "error_rate": 0.005
        }
        
        feedback = [
            {"rating": 4.5, "category": "performance"},
            {"rating": 4.0, "category": "reliability"},
            {"rating": 3.5, "category": "usability"}
        ]
        
        result = await improver._analyze_satisfaction(metrics, feedback)
        
        assert "score" in result
        assert "nps" in result
        assert "trend" in result
        assert "improvements" in result
        assert 0 <= result["score"] <= 100
    
    @pytest.mark.asyncio
    async def test_suggestion_generation(self, improver):
        """Test improvement suggestion generation"""
        
        # Mock analysis results
        quality = {"score": 60, "issues": []}
        performance = {"score": 70, "optimizations": [{"type": "caching", "improvement": 0.3, "risk": "low"}]}
        security = {"risk_score": 50, "vulnerabilities": [], "recommendations": ["Fix injection"]}
        business = {"roi": 1.5}
        bottlenecks = []
        
        suggestions = await improver._generate_suggestions(
            quality, performance, security, business, bottlenecks
        )
        
        assert isinstance(suggestions, list)
        assert all(isinstance(s, ImprovementSuggestion) for s in suggestions)
        
        # Should generate suggestions for low scores
        assert len(suggestions) > 0
        
        for suggestion in suggestions:
            assert suggestion.id
            assert suggestion.category in ["quality", "performance", "security", "business"]
            assert 1 <= suggestion.priority <= 10
            assert suggestion.estimated_roi > 0
            assert suggestion.risk_level in ["low", "medium", "high"]
            assert len(suggestion.implementation_steps) > 0
            assert isinstance(suggestion.expected_outcomes, dict)
    
    @pytest.mark.asyncio
    async def test_improvement_execution(self, improver):
        """Test improvement execution"""
        
        suggestion = ImprovementSuggestion(
            id="test_001",
            category="performance",
            description="Test improvement",
            priority=8,
            estimated_roi=2.0,
            risk_level="low",
            implementation_steps=["Step 1", "Step 2"],
            expected_outcomes={"performance": 1.2}
        )
        
        result = await improver.execute_improvement(suggestion, enable_ab_test=False)
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "actual_impact" in result
        assert "rollback_performed" in result
        assert "execution_time" in result
        assert isinstance(result["execution_time"], float)
        assert result["execution_time"] > 0
    
    def test_total_potential_calculation(self, improver):
        """Test total improvement potential calculation"""
        
        suggestions = [
            ImprovementSuggestion(
                id="s1", category="quality", description="Test",
                priority=5, estimated_roi=1.5, risk_level="low",
                implementation_steps=[], expected_outcomes={}
            ),
            ImprovementSuggestion(
                id="s2", category="performance", description="Test",
                priority=7, estimated_roi=2.0, risk_level="medium",
                implementation_steps=[], expected_outcomes={}
            )
        ]
        
        potential = improver._calculate_total_potential(suggestions)
        
        assert potential == 175.0  # (1.5 + 2.0) / 2 * 100
    
    def test_metrics_reporting(self, improver):
        """Test metrics reporting"""
        
        metrics = improver.get_metrics()
        
        assert "components_active" in metrics
        assert "analyses_available" in metrics
        assert "improvement_categories" in metrics
        assert "execution_history" in metrics
        
        assert metrics["components_active"] == 11
        assert metrics["analyses_available"] == 6
        assert metrics["improvement_categories"] == 4


@pytest.mark.integration
class TestServiceImproverE2E:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_improvement_workflow(self):
        """Test complete improvement workflow"""
        
        improver = get_improver()
        
        # Complex code with multiple issues
        problematic_code = """
# Performance issues
def inefficient_sort(data):
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] < data[j]:
                data[i], data[j] = data[j], data[i]
    return data

# Security issues
import pickle
password = "12345"
SECRET_KEY = "my-secret"

def unsafe_load(data):
    return pickle.loads(data)
    
def unsafe_exec(code):
    eval(code)
    exec(code)

# Quality issues
def complex_function(a,b,c,d,e,f,g,h,i,j):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            if g:
                                if h:
                                    if i:
                                        return j
    return None
"""
        
        metrics = {
            "performance": 0.5,
            "reliability": 0.7,
            "users": 10000,
            "revenue_per_user": 20,
            "response_time": 500,
            "uptime": 0.9,
            "error_rate": 0.1
        }
        
        feedback = [
            {"rating": 2.0, "category": "performance", "comment": "Too slow"},
            {"rating": 3.0, "category": "reliability", "comment": "Crashes often"},
            {"rating": 2.5, "category": "usability", "comment": "Hard to use"}
        ]
        
        # Analyze service
        analysis = await improver.analyze_service(problematic_code, metrics, feedback)
        
        # Verify comprehensive analysis
        assert analysis.quality_score < 60  # Should detect quality issues
        assert analysis.security_score < 70  # Should detect security issues
        assert analysis.user_satisfaction < 60  # Low feedback scores
        assert len(analysis.vulnerabilities) > 0
        assert len(analysis.improvement_opportunities) > 0
        
        # Get top improvement
        if analysis.improvement_opportunities:
            top_improvement = analysis.improvement_opportunities[0]
            
            # Should prioritize critical issues
            assert top_improvement.priority >= 7
            
            # Execute improvement
            execution_result = await improver.execute_improvement(
                top_improvement,
                enable_ab_test=True
            )
            
            assert "success" in execution_result
            assert "ab_test_results" in execution_result
            
            # If A/B test was performed
            if execution_result["ab_test_results"]:
                assert "winner" in execution_result["ab_test_results"]
                assert "statistical_significance" in execution_result["ab_test_results"]
    
    @pytest.mark.asyncio
    async def test_parallel_analysis_performance(self):
        """Test parallel analysis performance"""
        
        improver = get_improver()
        
        code = "def test(): return 'test'"
        metrics = {"performance": 0.8}
        
        # Time the analysis
        import time
        start = time.time()
        
        analysis = await improver.analyze_service(code, metrics)
        
        elapsed = time.time() - start
        
        # Should complete quickly due to parallel execution
        assert elapsed < 5.0  # 5 seconds max
        assert analysis is not None
    
    @pytest.mark.asyncio 
    async def test_error_handling(self):
        """Test error handling in integration"""
        
        improver = get_improver()
        
        # Invalid code
        invalid_code = "This is not valid Python code {"
        
        metrics = {"performance": 0.5}
        
        # Should handle syntax errors gracefully
        analysis = await improver.analyze_service(invalid_code, metrics)
        
        assert isinstance(analysis, ServiceAnalysis)
        # Should still provide some analysis
        assert analysis.quality_score >= 0
    
    @pytest.mark.asyncio
    async def test_improvement_prioritization(self):
        """Test improvement prioritization"""
        
        improver = get_improver()
        
        # Code with security and performance issues
        code = """
eval(user_input)  # Critical security
password = "weak"  # Security

def slow():
    result = []
    for i in range(10000):
        result.append(i)
    return result
"""
        
        metrics = {"performance": 0.8}
        
        analysis = await improver.analyze_service(code, metrics)
        
        # Security improvements should be prioritized
        if len(analysis.improvement_opportunities) > 1:
            top_priority = analysis.improvement_opportunities[0]
            assert top_priority.category == "security" or top_priority.priority >= 9
    
    @pytest.mark.asyncio
    async def test_rollback_scenario(self):
        """Test rollback on failed improvement"""
        
        improver = get_improver()
        
        # Create high-risk improvement that might fail
        suggestion = ImprovementSuggestion(
            id="high_risk_001",
            category="performance",
            description="High risk optimization",
            priority=8,
            estimated_roi=5.0,  # Very high expectation
            risk_level="high",
            implementation_steps=["Risky change"],
            expected_outcomes={"performance": 5.0}
        )
        
        result = await improver.execute_improvement(suggestion, enable_ab_test=False)
        
        # With such high expectations, actual impact will likely be lower
        # This should trigger rollback
        assert "rollback_performed" in result
        
    def test_component_integration(self):
        """Test all components are properly integrated"""
        
        improver = get_improver()
        
        # Verify all components are initialized
        assert improver.quality_analyzer is not None
        assert improver.performance_analyzer is not None
        assert improver.code_optimizer is not None
        assert improver.ast_analyzer is not None
        assert improver.refactoring_engine is not None
        assert improver.bottleneck_detector is not None
        assert improver.vulnerability_scanner is not None
        assert improver.business_analyzer is not None
        assert improver.roi_calculator is not None
        assert improver.satisfaction_scorer is not None
        assert improver.improvement_executor is not None
        
        # Verify metrics
        metrics = improver.get_metrics()
        assert metrics["components_active"] == 11


class TestServiceImproverPerformance:
    """Performance tests"""
    
    @pytest.mark.asyncio
    async def test_analysis_performance(self):
        """Test analysis performance"""
        
        improver = get_improver()
        
        test_code = "def test(): return 42"
        test_metrics = {"performance": 0.9}
        
        import time
        start = time.time()
        
        result = await improver.analyze_service(test_code, test_metrics)
        
        elapsed = time.time() - start
        
        assert isinstance(result, ServiceAnalysis)
        assert elapsed < 10.0  # Should complete within 10 seconds
    
    def test_initialization_performance(self):
        """Test initialization performance"""
        
        import time
        start = time.time()
        
        improver = ServiceImprover()
        
        elapsed = time.time() - start
        
        assert improver is not None
        assert improver.quality_analyzer is not None
        assert elapsed < 1.0  # Should initialize within 1 second


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])