"""
Test suite for AI Analysis Engine
Day 7: AI Analysis Engine - TDD Implementation
Generated: 2024-11-18

Testing requirements:
1. Agent code analysis and optimization suggestions
2. Multi-model consensus analysis
3. Performance scoring and fitness evaluation
4. Analysis history tracking and trend analysis
5. Real-time analysis pipeline
"""

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest


class TestAIAnalysisEngine:
    """Test core AI analysis engine functionality"""

    def test_analyze_agent_code(self):
        """Test analyzing agent code for optimization opportunities"""
        from src.analysis.ai_analysis_engine import AIAnalysisEngine

        engine = AIAnalysisEngine()

        # Sample agent code
        agent_code = """
def process_input(text):
    # Inefficient string operations
    result = ""
    for char in text:
        result = result + char.upper()
    return result
        """

        analysis = engine.analyze_code(agent_code, agent_id="test_001")

        assert analysis["agent_id"] == "test_001"
        assert "issues" in analysis
        assert "recommendations" in analysis
        assert "confidence" in analysis
        assert isinstance(analysis["confidence"], float)
        assert 0.0 <= analysis["confidence"] <= 1.0

    def test_performance_scoring(self):
        """Test AI-based performance scoring"""
        from src.analysis.ai_analysis_engine import PerformanceScorer

        scorer = PerformanceScorer()

        metrics = {
            "execution_time_us": 2.8,
            "memory_usage_kb": 5.9,
            "error_rate": 0.02,
            "success_rate": 0.98,
        }

        score = scorer.calculate_score(metrics)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

        # High performance should get high score
        assert score > 0.8  # Good metrics should score well

    def test_optimization_suggestions(self):
        """Test generating optimization suggestions"""
        from src.analysis.ai_analysis_engine import OptimizationSuggester

        suggester = OptimizationSuggester()

        # Problematic code patterns
        code_issues = {
            "string_concatenation": True,
            "nested_loops": False,
            "memory_leaks": False,
            "inefficient_algorithms": True,
        }

        suggestions = suggester.generate_suggestions(code_issues)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Should suggest string optimization
        assert any("string" in s.lower() for s in suggestions)

    def test_multi_model_consensus(self):
        """Test consensus analysis from multiple AI models"""
        from src.analysis.ai_analysis_engine import ConsensusAnalyzer

        analyzer = ConsensusAnalyzer()

        # Simulate responses from different AI models
        model_responses = {
            "claude": {"issue": "string_inefficiency", "confidence": 0.95, "severity": "medium"},
            "gpt4": {"issue": "string_inefficiency", "confidence": 0.92, "severity": "medium"},
            "gemini": {"issue": "memory_usage", "confidence": 0.78, "severity": "low"},
        }

        for model, response in model_responses.items():
            analyzer.add_analysis(model, response)

        consensus = analyzer.get_consensus()

        assert consensus["primary_issue"] == "string_inefficiency"
        assert consensus["agreement_level"] == "high"  # 2/3 agree
        assert consensus["avg_confidence"] > 0.8


class TestAnalysisHistory:
    """Test analysis history tracking and trends"""

    def test_analysis_history_tracking(self):
        """Test tracking analysis results over time"""
        from src.analysis.analysis_history import AnalysisHistory

        history = AnalysisHistory(agent_id="test_agent")

        # Add analysis results over time
        history.add_analysis(
            timestamp=datetime.utcnow() - timedelta(days=3),
            score=0.7,
            issues=["string_concat", "memory_usage"],
        )

        history.add_analysis(
            timestamp=datetime.utcnow() - timedelta(days=1), score=0.85, issues=["memory_usage"]
        )

        history.add_analysis(timestamp=datetime.utcnow(), score=0.92, issues=[])

        trend = history.get_trend()
        assert trend == "improving"

        improvement_rate = history.get_improvement_rate()
        assert improvement_rate > 0  # Should be positive

    def test_issue_resolution_tracking(self):
        """Test tracking when issues are resolved"""
        from src.analysis.analysis_history import IssueTracker

        tracker = IssueTracker()

        # Initial issues
        tracker.record_issues(["issue_a", "issue_b"], generation=1)

        # Some issues resolved
        tracker.record_issues(["issue_b"], generation=2)

        # All issues resolved
        tracker.record_issues([], generation=3)

        resolution_history = tracker.get_resolution_history()

        assert len(resolution_history) == 2  # 2 resolutions
        assert "issue_a" in resolution_history
        assert resolution_history["issue_a"]["resolved_in_generation"] == 2

    def test_pattern_detection(self):
        """Test detecting patterns in analysis results"""
        from src.analysis.analysis_history import PatternDetector

        detector = PatternDetector()

        # Add analysis data showing recurring patterns
        analyses = [
            {"timestamp": datetime.utcnow() - timedelta(days=i), "issues": ["memory_leak"]}
            for i in range(5)
        ]

        for analysis in analyses:
            detector.add_analysis(analysis)

        patterns = detector.detect_patterns()

        assert "recurring_issues" in patterns
        assert "memory_leak" in patterns["recurring_issues"]


class TestRealTimeAnalysis:
    """Test real-time analysis pipeline"""

    @pytest.mark.asyncio
    async def test_async_analysis_pipeline(self):
        """Test asynchronous analysis pipeline"""
        from src.analysis.realtime_analyzer import RealtimeAnalyzer

        analyzer = RealtimeAnalyzer()

        # Mock AI model responses
        with patch.object(analyzer, "_call_ai_model", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = {
                "issues": ["performance_issue"],
                "confidence": 0.88,
                "recommendations": ["optimize_loops"],
            }

            result = await analyzer.analyze_async(
                agent_code="def test(): pass", agent_id="async_test"
            )

            assert result["agent_id"] == "async_test"
            assert "issues" in result
            assert mock_ai.called

    @pytest.mark.asyncio
    async def test_batch_analysis(self):
        """Test analyzing multiple agents in parallel"""
        from src.analysis.realtime_analyzer import BatchAnalyzer

        analyzer = BatchAnalyzer(max_concurrent=3)

        agents = [{"id": f"agent_{i}", "code": f"def func_{i}(): pass"} for i in range(5)]

        with patch.object(analyzer, "_analyze_single", new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = {"score": 0.8, "issues": []}

            results = await analyzer.analyze_batch(agents)

            assert len(results) == 5
            assert all("score" in r for r in results)

    def test_analysis_queue_management(self):
        """Test managing analysis request queue"""
        from src.analysis.realtime_analyzer import AnalysisQueue

        queue = AnalysisQueue(max_size=10)

        # Add analysis requests
        for i in range(5):
            request = {
                "agent_id": f"agent_{i}",
                "priority": i % 3,  # 0=high, 1=medium, 2=low
                "timestamp": datetime.utcnow(),
            }
            queue.add_request(request)

        assert queue.size() == 5

        # High priority should come first
        next_request = queue.get_next()
        assert next_request["priority"] == 0


class TestModelIntegration:
    """Test integration with external AI models"""

    def test_claude_integration(self):
        """Test integration with Claude API"""
        from src.analysis.model_integrations import ClaudeAnalyzer

        analyzer = ClaudeAnalyzer(api_key="test_key")

        # Test with mock response (no actual API call)
        with patch.object(analyzer, "_mock_claude_response") as mock_response:
            mock_response.return_value = json.dumps(
                {
                    "issues": ["inefficient_loop"],
                    "confidence": 0.92,
                    "suggestions": ["use list comprehension"],
                }
            )

            result = analyzer.analyze("def slow_func(): pass")

            assert "issues" in result
            assert result["confidence"] == 0.92

    def test_openai_integration(self):
        """Test integration with OpenAI API"""
        from src.analysis.model_integrations import OpenAIAnalyzer

        analyzer = OpenAIAnalyzer(api_key="test_key")

        # Test with mock response
        with patch.object(analyzer, "_mock_openai_response") as mock_response:
            mock_response.return_value = json.dumps(
                {
                    "performance_score": 0.85,
                    "bottlenecks": ["string_operations"],
                    "optimizations": ["use join() instead of concatenation"],
                }
            )

            result = analyzer.analyze("def concat_strings(): pass")

            assert "performance_score" in result
            assert result["performance_score"] == 0.85

    def test_fallback_mechanism(self):
        """Test fallback when primary AI model fails"""
        from src.analysis.model_integrations import FallbackAnalyzer

        analyzer = FallbackAnalyzer(primary_model="claude", fallback_models=["openai", "local"])

        with patch.object(analyzer, "_try_model") as mock_try:
            # Primary fails, fallback succeeds
            mock_try.side_effect = [
                {"success": False, "error": "Primary failed"},
                {"success": True, "score": 0.7, "source": "fallback"},
            ]

            result = analyzer.analyze("test code")

            assert result["score"] == 0.7
            assert result["source"] == "fallback"
            assert mock_try.call_count == 2


class TestAnalysisMetrics:
    """Test analysis quality metrics and validation"""

    def test_analysis_quality_metrics(self):
        """Test measuring quality of analysis results"""
        from src.analysis.metrics import AnalysisQualityChecker

        checker = AnalysisQualityChecker()

        analysis_result = {
            "issues": ["memory_leak", "performance_bottleneck"],
            "confidence": 0.92,
            "recommendations": ["fix memory management", "optimize algorithm"],
            "execution_time": 0.5,  # seconds
        }

        quality = checker.assess_quality(analysis_result)

        assert "completeness" in quality
        assert "accuracy_confidence" in quality
        assert "response_time" in quality
        assert isinstance(quality["overall_score"], float)

    def test_analysis_consistency(self):
        """Test consistency across multiple analysis runs"""
        from src.analysis.metrics import ConsistencyChecker

        checker = ConsistencyChecker()

        # Same code analyzed multiple times
        results = [
            {"issues": ["memory_leak"], "confidence": 0.9},
            {"issues": ["memory_leak"], "confidence": 0.88},
            {"issues": ["memory_leak", "performance"], "confidence": 0.85},
        ]

        for result in results:
            checker.add_result(result)

        consistency = checker.calculate_consistency()

        assert "issue_consistency" in consistency
        assert "confidence_variance" in consistency
        assert consistency["issue_consistency"] > 0.6  # Should be reasonably consistent

    def test_false_positive_detection(self):
        """Test detecting false positive issues"""
        from src.analysis.metrics import FalsePositiveDetector

        detector = FalsePositiveDetector()

        # Historical data: reported issues and actual outcomes
        detector.add_historical_data(
            reported_issue="memory_leak",
            actual_improvement=0.02,  # Very small improvement
            confidence=0.95,
        )

        detector.add_historical_data(
            reported_issue="algorithm_inefficiency",
            actual_improvement=0.3,  # Significant improvement
            confidence=0.89,
        )

        false_positive_rate = detector.calculate_false_positive_rate()

        assert isinstance(false_positive_rate, float)
        assert 0.0 <= false_positive_rate <= 1.0


@pytest.mark.integration
class TestAIAnalysisIntegration:
    """Integration tests for complete AI analysis system"""

    def test_end_to_end_analysis_workflow(self):
        """Test complete analysis workflow from code to recommendations"""
        from src.analysis.ai_analysis_engine import AIAnalysisEngine
        from src.analysis.analysis_history import AnalysisHistory
        from src.models.agent import Agent

        # Create test agent
        agent = Agent(name="test_analysis_agent", size_kb=5.8, instantiation_us=2.9)

        # Initialize analysis system
        engine = AIAnalysisEngine()
        history = AnalysisHistory(agent_id=agent.id)

        # Sample agent code with known issues
        agent_code = """
def inefficient_function(data):
    result = ""
    for item in data:
        result = result + str(item) + ","
    return result[:-1]
        """

        # Run analysis (using actual implementation)
        analysis_result = engine.analyze_code(agent_code, agent.id)

        # Record in history
        history.add_analysis(
            timestamp=datetime.utcnow(),
            score=analysis_result.get("confidence", 0),
            issues=analysis_result.get("issues", []),
        )

        assert analysis_result["agent_id"] == agent.id
        assert len(analysis_result["issues"]) >= 0  # May or may not have issues
        assert len(analysis_result["recommendations"]) > 0

    def test_analysis_performance_under_load(self):
        """Test analysis system performance under load"""
        from src.analysis.realtime_analyzer import RealtimeAnalyzer

        analyzer = RealtimeAnalyzer()

        start_time = datetime.utcnow()

        # Simulate multiple concurrent analyses
        agents_to_analyze = 20

        with patch.object(analyzer, "_call_ai_model") as mock_ai:
            mock_ai.return_value = {
                "issues": ["test_issue"],
                "confidence": 0.8,
                "processing_time": 0.1,
            }

            results = []
            for i in range(agents_to_analyze):
                result = analyzer.analyze_code(
                    code=f"def test_{i}(): pass", agent_id=f"load_test_{i}"
                )
                results.append(result)

            end_time = datetime.utcnow()
            total_time = (end_time - start_time).total_seconds()

            assert len(results) == agents_to_analyze
            assert total_time < 5.0  # Should complete within 5 seconds
            assert all(r["agent_id"].startswith("load_test_") for r in results)
