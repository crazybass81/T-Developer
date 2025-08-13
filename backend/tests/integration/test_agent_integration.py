"""
Day 19: Integration Tests for AgentCore System
Tests end-to-end agent workflows and inter-agent communication
"""
import asyncio
import json
import sys
import time
import unittest
from pathlib import Path
from typing import Dict, List

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.agentcore.component_decision.main import ComponentDecisionAgent
from src.agents.agentcore.match_rate.main import MatchRateAgent

# Import agent modules
from src.agents.agentcore.nl_input.main import NLInputAgent
from src.agents.agentcore.parser.main import ParserAgent
from src.agents.agentcore.search.main import SearchAgent
from src.agents.agentcore.ui_selection.main import UISelectionAgent


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agent system"""

    def setUp(self):
        """Set up test environment"""
        self.agents = {
            "nl_input": NLInputAgent(),
            "ui_selection": UISelectionAgent(),
            "parser": ParserAgent(),
            "component_decision": ComponentDecisionAgent(),
            "match_rate": MatchRateAgent(),
            "search": SearchAgent(),
        }

    def test_agent_initialization(self):
        """Test that all agents initialize correctly"""
        for agent_name, agent in self.agents.items():
            self.assertIsNotNone(agent)
            self.assertTrue(hasattr(agent, "process"))
            self.assertTrue(hasattr(agent, "validate_input"))
            self.assertTrue(hasattr(agent, "get_metadata"))

            # Test metadata
            metadata = agent.get_metadata()
            self.assertIn("name", metadata)
            self.assertIn("version", metadata)
            self.assertIn("capabilities", metadata)

    def test_nl_input_processing(self):
        """Test NL Input agent processing"""
        agent = self.agents["nl_input"]

        test_cases = [
            {
                "input": "Create a web application with user authentication",
                "expected_intent": "create_application",
            },
            {"input": "Fix the bug in the login system", "expected_intent": "fix_issue"},
            {"input": "Update the dashboard layout", "expected_intent": "modify_application"},
        ]

        for test_case in test_cases:
            result = agent.process({"input": test_case["input"]})
            self.assertEqual(result["status"], "success")
            self.assertIn("result", result)
            self.assertEqual(result["result"]["intent"], test_case["expected_intent"])

    def test_ui_selection_processing(self):
        """Test UI Selection agent processing"""
        agent = self.agents["ui_selection"]

        request = {
            "input": "dummy",  # Required field
            "requirements": {"responsive": True},
            "platform": "web",
        }

        result = agent.process(request)
        self.assertEqual(result["status"], "success")
        self.assertIn("result", result)
        self.assertIn("components", result["result"])
        self.assertIn("theme", result["result"])
        self.assertIn("layout", result["result"])
        self.assertEqual(result["result"]["framework"], "react")

    def test_parser_processing(self):
        """Test Parser agent processing"""
        agent = self.agents["parser"]

        request = {
            "input": "The system must handle 1000 users\nIt should be responsive\nBudget constraint is $10000",
            "type": "text",
        }

        result = agent.process(request)
        self.assertEqual(result["status"], "success")
        self.assertIn("result", result)
        self.assertIn("parsed_requirements", result["result"])
        self.assertIn("specification", result["result"])
        self.assertIn("validation", result["result"])

    def test_component_decision_processing(self):
        """Test Component Decision agent processing"""
        agent = self.agents["component_decision"]

        request = {
            "input": "dummy",
            "requirements": {"scalability": "high", "authentication": True},
            "constraints": {"language": "python", "sql": True},
        }

        result = agent.process(request)
        self.assertEqual(result["status"], "success")
        self.assertIn("result", result)
        self.assertIn("architecture", result["result"])
        self.assertIn("components", result["result"])
        self.assertIn("tech_stack", result["result"])

    def test_match_rate_processing(self):
        """Test Match Rate agent processing"""
        agent = self.agents["match_rate"]

        request = {
            "input": "dummy",
            "query": {
                "features": ["authentication", "dashboard"],
                "technologies": ["python", "react"],
                "budget": 10000,
            },
            "candidates": [
                {
                    "id": "solution_1",
                    "features": ["authentication", "dashboard", "api"],
                    "technologies": ["python", "react", "postgresql"],
                    "cost": 8000,
                },
                {
                    "id": "solution_2",
                    "features": ["authentication"],
                    "technologies": ["nodejs", "vue"],
                    "cost": 12000,
                },
            ],
        }

        result = agent.process(request)
        self.assertEqual(result["status"], "success")
        self.assertIn("result", result)
        self.assertIn("scores", result["result"])
        self.assertIn("quality_metrics", result["result"])
        self.assertIn("best_match", result["result"])

    def test_search_processing(self):
        """Test Search agent processing"""
        agent = self.agents["search"]

        request = {
            "input": "dummy",
            "query": "authentication system",
            "filters": {"category": "technology"},
            "limit": 5,
        }

        result = agent.process(request)
        self.assertEqual(result["status"], "success")
        self.assertIn("result", result)
        self.assertIn("results", result["result"])
        self.assertIn("total_count", result["result"])
        self.assertIn("facets", result["result"])

    def test_agent_workflow_integration(self):
        """Test complete agent workflow"""
        # Step 1: NL Input processing
        nl_input = self.agents["nl_input"].process(
            {"input": "Create a web application with user authentication and dashboard"}
        )
        self.assertEqual(nl_input["status"], "success")

        # Step 2: Parser processing
        parser = self.agents["parser"].process(
            {
                "input": "The system must handle user authentication\nIt should have a dashboard\nMust be scalable",
                "type": "text",
            }
        )
        self.assertEqual(parser["status"], "success")

        # Step 3: Component Decision
        component_decision = self.agents["component_decision"].process(
            {
                "input": "dummy",
                "requirements": {"scalability": "high", "authentication": True, "dashboard": True},
                "constraints": {"language": "python"},
            }
        )
        self.assertEqual(component_decision["status"], "success")

        # Step 4: UI Selection
        ui_selection = self.agents["ui_selection"].process(
            {"input": "dummy", "requirements": {"dashboard": True}, "platform": "web"}
        )
        self.assertEqual(ui_selection["status"], "success")

        # Verify workflow consistency
        self.assertEqual(nl_input["result"]["intent"], "create_application")
        self.assertIn("functional", parser["result"]["parsed_requirements"])
        self.assertIn("architecture", component_decision["result"])
        self.assertIn("components", ui_selection["result"])

    def test_error_handling(self):
        """Test error handling across agents"""
        for agent_name, agent in self.agents.items():
            # Test with empty request
            result = agent.process({})
            self.assertEqual(result["status"], "error")
            self.assertIn("error", result)

            # Test with missing required field
            result = agent.process({"invalid_field": "value"})
            self.assertEqual(result["status"], "error")
            self.assertIn("Missing input field", result["error"])

    def test_agent_metadata_consistency(self):
        """Test metadata consistency across agents"""
        for agent_name, agent in self.agents.items():
            metadata = agent.get_metadata()

            # Check required fields
            self.assertIn("name", metadata)
            self.assertIn("version", metadata)
            self.assertIn("description", metadata)
            self.assertIn("capabilities", metadata)
            self.assertIn("constraints", metadata)

            # Check constraints
            constraints = metadata["constraints"]
            self.assertEqual(constraints["max_memory_kb"], 6.5)
            self.assertEqual(constraints["max_instantiation_us"], 3.0)

            # Check capabilities is a list
            self.assertIsInstance(metadata["capabilities"], list)
            self.assertGreater(len(metadata["capabilities"]), 0)


class TestPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarking for agents"""

    def setUp(self):
        """Set up benchmark environment"""
        self.agents = {
            "nl_input": NLInputAgent(),
            "ui_selection": UISelectionAgent(),
            "parser": ParserAgent(),
            "component_decision": ComponentDecisionAgent(),
            "match_rate": MatchRateAgent(),
            "search": SearchAgent(),
        }
        self.benchmark_results = {}

    def test_agent_instantiation_time(self):
        """Benchmark agent instantiation time"""
        target_us = 3.0  # Target: < 3 microseconds

        for agent_name, agent_class in [
            ("nl_input", NLInputAgent),
            ("ui_selection", UISelectionAgent),
            ("parser", ParserAgent),
            ("component_decision", ComponentDecisionAgent),
            ("match_rate", MatchRateAgent),
            ("search", SearchAgent),
        ]:
            start_time = time.perf_counter()
            for _ in range(1000):
                instance = agent_class()
            end_time = time.perf_counter()

            avg_time_us = ((end_time - start_time) / 1000) * 1_000_000
            self.benchmark_results[f"{agent_name}_instantiation_us"] = avg_time_us

            print(f"{agent_name}: {avg_time_us:.2f} μs")
            self.assertLess(avg_time_us, target_us * 10)  # Allow 10x margin for Python

    def test_agent_processing_time(self):
        """Benchmark agent processing time"""
        target_ms = 100  # Target: < 100ms per request

        test_requests = {
            "nl_input": {"input": "Create a web application with authentication"},
            "ui_selection": {"input": "dummy", "platform": "web"},
            "parser": {"input": "System requirements text", "type": "text"},
            "component_decision": {"input": "dummy", "requirements": {}, "constraints": {}},
            "match_rate": {"input": "dummy", "query": {}, "candidates": []},
            "search": {"input": "dummy", "query": "test", "limit": 10},
        }

        for agent_name, agent in self.agents.items():
            request = test_requests[agent_name]

            start_time = time.perf_counter()
            for _ in range(100):
                result = agent.process(request)
            end_time = time.perf_counter()

            avg_time_ms = ((end_time - start_time) / 100) * 1000
            self.benchmark_results[f"{agent_name}_processing_ms"] = avg_time_ms

            print(f"{agent_name}: {avg_time_ms:.2f} ms")
            self.assertLess(avg_time_ms, target_ms)

    def test_memory_usage(self):
        """Test agent memory usage"""
        import sys

        for agent_name, agent in self.agents.items():
            size_bytes = sys.getsizeof(agent)
            size_kb = size_bytes / 1024

            self.benchmark_results[f"{agent_name}_memory_kb"] = size_kb
            print(f"{agent_name}: {size_kb:.2f} KB")

            # Agent instance should be small (< 100KB)
            self.assertLess(size_kb, 100)

    def tearDown(self):
        """Save benchmark results"""
        if self.benchmark_results:
            results_file = Path("logs/day19_benchmark_results.json")
            results_file.parent.mkdir(parents=True, exist_ok=True)
            results_file.write_text(json.dumps(self.benchmark_results, indent=2))
            print(f"\nBenchmark results saved to {results_file}")


if __name__ == "__main__":
    # Run integration tests
    print("=" * 60)
    print("Running Integration Tests")
    print("=" * 60)

    integration_suite = unittest.TestLoader().loadTestsFromTestCase(TestAgentIntegration)
    integration_runner = unittest.TextTestRunner(verbosity=2)
    integration_result = integration_runner.run(integration_suite)

    # Run performance benchmarks
    print("\n" + "=" * 60)
    print("Running Performance Benchmarks")
    print("=" * 60)

    benchmark_suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceBenchmark)
    benchmark_runner = unittest.TextTestRunner(verbosity=2)
    benchmark_result = benchmark_runner.run(benchmark_suite)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    total_tests = integration_result.testsRun + benchmark_result.testsRun
    total_failures = len(integration_result.failures) + len(benchmark_result.failures)
    total_errors = len(integration_result.errors) + len(benchmark_result.errors)

    print(f"Total tests run: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")

    if total_failures == 0 and total_errors == 0:
        print("\n✅ All tests passed!")
        exit(0)
    else:
        print("\n❌ Some tests failed")
        exit(1)
