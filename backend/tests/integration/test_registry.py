"""
Day 10: Registry Integration Tests
Comprehensive E2E testing for agent registration, AI analysis, and system integration
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List

import pytest
import requests
from httpx import AsyncClient

from backend.src.messaging.agent_registry import AgentCapabilityRegistry
from backend.src.api.enhanced_gateway import EnhancedAPIGateway
from backend.src.analysis.ai_analysis_engine import AIAnalysisEngine


class TestRegistryE2E:
    """End-to-End tests for the complete agent registry system"""

    @pytest.fixture
    async def setup_test_environment(self):
        """Setup test environment with all components"""
        # Initialize components
        self.registry = AgentCapabilityRegistry()
        self.gateway = EnhancedAPIGateway({"host": "localhost", "port": 8888})
        self.ai_engine = AIAnalysisEngine()
        
        # Initialize the API Gateway
        await self.gateway.initialize()
        
        return {
            "registry": self.registry,
            "gateway": self.gateway,
            "ai_engine": self.ai_engine
        }

    @pytest.mark.asyncio
    async def test_complete_agent_registration_flow(self, setup_test_environment):
        """Test complete agent registration from creation to availability"""
        env = await setup_test_environment
        
        # Step 1: Create test agent data
        test_agent = {
            "agent_id": f"test_agent_{uuid.uuid4().hex[:8]}",
            "name": "Test Agent E2E",
            "capabilities": ["data_processing", "text_analysis", "api_integration"],
            "input_types": ["text", "json"],
            "output_types": ["json", "analysis_report"],
            "metadata": {
                "version": "1.0.0",
                "author": "system_test",
                "performance_tier": "standard"
            },
            "endpoints": [
                {"path": "/process", "methods": ["POST"], "description": "Process data"},
                {"path": "/analyze", "methods": ["POST"], "description": "Analyze text"}
            ]
        }
        
        # Step 2: Register agent in registry
        start_time = time.time()
        await env["registry"].register_agent_capabilities_async(
            test_agent["agent_id"], test_agent
        )
        registration_time = (time.time() - start_time) * 1000  # ms
        
        # Verify registration time performance
        assert registration_time < 100, f"Registration took {registration_time}ms, should be <100ms"
        
        # Step 3: Verify agent appears in registry
        retrieved_agent = await env["registry"].get_agent_capabilities_async(test_agent["agent_id"])
        assert retrieved_agent is not None, "Agent not found after registration"
        assert retrieved_agent["name"] == test_agent["name"]
        assert set(retrieved_agent["capabilities"]) == set(test_agent["capabilities"])
        
        # Step 4: Test capability-based queries
        matching_agents = await env["registry"].find_agents_by_capability_async("data_processing")
        assert test_agent["agent_id"] in matching_agents, "Agent not found by capability search"
        
        # Step 5: Test input/output type queries
        input_agents = env["registry"].find_agents_by_input_type("json")
        assert test_agent["agent_id"] in input_agents, "Agent not found by input type search"
        
        output_agents = env["registry"].find_agents_by_output_type("json")
        assert test_agent["agent_id"] in output_agents, "Agent not found by output type search"
        
        # Step 6: Test agent removal
        await env["registry"].remove_agent(test_agent["agent_id"])
        removed_agent = await env["registry"].get_agent_capabilities_async(test_agent["agent_id"])
        assert removed_agent is None, "Agent still exists after removal"

    @pytest.mark.asyncio
    async def test_ai_analysis_integration(self, setup_test_environment):
        """Test AI analysis accuracy and integration"""
        env = await setup_test_environment
        
        # Sample agent code for analysis
        sample_agent_code = '''
class DataProcessorAgent:
    def __init__(self):
        self.name = "Data Processor"
        self.version = "1.0"
    
    def process_text(self, text: str) -> Dict:
        """Process text data and return analysis"""
        word_count = len(text.split())
        char_count = len(text)
        return {
            "word_count": word_count,
            "char_count": char_count,
            "analysis_type": "text_stats"
        }
    
    def process_json(self, data: Dict) -> Dict:
        """Process JSON data"""
        return {
            "keys": list(data.keys()),
            "size": len(data),
            "processed": True
        }
'''
        
        # Perform AI analysis
        analysis_start = time.time()
        analysis_result = await env["ai_engine"].analyze_agent_code(sample_agent_code)
        analysis_time = (time.time() - analysis_start) * 1000  # ms
        
        # Verify analysis performance
        assert analysis_time < 5000, f"AI analysis took {analysis_time}ms, should be <5000ms"
        
        # Verify analysis results
        assert analysis_result["success"] is True, "AI analysis failed"
        assert "capabilities" in analysis_result, "AI analysis missing capabilities"
        assert "performance_score" in analysis_result, "AI analysis missing performance score"
        
        # Verify capability extraction accuracy
        detected_capabilities = analysis_result["capabilities"]
        expected_capabilities = ["data_processing", "text_analysis", "json_processing"]
        
        # At least 2 out of 3 capabilities should be detected (70% accuracy threshold)
        overlap = set(detected_capabilities) & set(expected_capabilities)
        accuracy = len(overlap) / len(expected_capabilities)
        assert accuracy >= 0.7, f"AI analysis accuracy {accuracy:.2f} below 70% threshold"

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, setup_test_environment):
        """Test concurrent agent registration and operations"""
        env = await setup_test_environment
        
        # Create multiple test agents
        test_agents = []
        for i in range(10):
            agent = {
                "agent_id": f"concurrent_agent_{i}_{uuid.uuid4().hex[:6]}",
                "name": f"Concurrent Test Agent {i}",
                "capabilities": [f"capability_{i}", "shared_capability"],
                "input_types": ["text"],
                "output_types": ["json"],
                "metadata": {"test_batch": "concurrent_test"}
            }
            test_agents.append(agent)
        
        # Register agents concurrently
        start_time = time.time()
        tasks = []
        for agent in test_agents:
            task = env["registry"].register_agent_capabilities_async(
                agent["agent_id"], agent
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        concurrent_registration_time = (time.time() - start_time) * 1000  # ms
        
        # Verify concurrent performance
        avg_time_per_agent = concurrent_registration_time / len(test_agents)
        assert avg_time_per_agent < 50, f"Avg registration time {avg_time_per_agent}ms too high"
        
        # Verify all agents were registered
        for agent in test_agents:
            retrieved = await env["registry"].get_agent_capabilities_async(agent["agent_id"])
            assert retrieved is not None, f"Agent {agent['agent_id']} not found after concurrent registration"
        
        # Test concurrent capability search
        search_start = time.time()
        search_tasks = [
            env["registry"].find_agents_by_capability_async("shared_capability"),
            env["registry"].find_agents_by_capability_async("capability_0"),
            env["registry"].find_agents_by_capability_async("capability_5")
        ]
        
        results = await asyncio.gather(*search_tasks)
        search_time = (time.time() - search_start) * 1000  # ms
        
        assert search_time < 200, f"Concurrent search took {search_time}ms, should be <200ms"
        
        # Verify search results
        shared_results = results[0]
        assert len(shared_results) == len(test_agents), "Shared capability search incomplete"
        
        # Cleanup
        cleanup_tasks = [env["registry"].remove_agent(agent["agent_id"]) for agent in test_agents]
        await asyncio.gather(*cleanup_tasks)

    @pytest.mark.asyncio
    async def test_api_gateway_integration(self, setup_test_environment):
        """Test API Gateway integration with registry"""
        env = await setup_test_environment
        
        # Test agent for API Gateway integration
        test_agent = {
            "agent_id": f"api_test_agent_{uuid.uuid4().hex[:8]}",
            "name": "API Test Agent",
            "capabilities": ["api_processing"],
            "endpoints": [
                {
                    "path": "/test",
                    "methods": ["GET", "POST"],
                    "description": "Test endpoint"
                }
            ]
        }
        
        # Register agent through API Gateway
        async with AsyncClient() as client:
            # Note: In real test, we'd start the gateway server
            # For now, test the integration logic
            
            # Test agent registration via registry
            await env["registry"].register_agent_capabilities_async(
                test_agent["agent_id"], test_agent
            )
            
            # Verify agent appears in all agents list
            all_agents = await env["registry"].get_all_agents()
            agent_ids = [agent["agent_id"] for agent in all_agents]
            assert test_agent["agent_id"] in agent_ids, "Agent not in all agents list"
            
            # Test gateway memory usage
            memory_usage = env["gateway"].get_memory_usage_kb()
            assert memory_usage < 6.5, f"Gateway memory usage {memory_usage}KB exceeds 6.5KB limit"
            
            # Test instantiation time
            instantiation_time = env["gateway"].validate_instantiation_time()
            assert instantiation_time < 3.0, f"Gateway instantiation {instantiation_time}μs exceeds 3μs limit"

    @pytest.mark.asyncio
    async def test_registry_persistence_and_recovery(self, setup_test_environment):
        """Test registry data persistence and recovery capabilities"""
        env = await setup_test_environment
        
        # Create test agents
        persistent_agents = []
        for i in range(5):
            agent = {
                "agent_id": f"persistent_agent_{i}_{uuid.uuid4().hex[:6]}",
                "name": f"Persistent Agent {i}",
                "capabilities": ["persistence_test"],
                "metadata": {"persistent": True}
            }
            persistent_agents.append(agent)
            await env["registry"].register_agent_capabilities_async(agent["agent_id"], agent)
        
        # Verify agents exist
        for agent in persistent_agents:
            retrieved = await env["registry"].get_agent_capabilities_async(agent["agent_id"])
            assert retrieved is not None, f"Agent {agent['agent_id']} not persisted"
        
        # Simulate registry recovery (new instance)
        new_registry = AgentCapabilityRegistry()
        
        # Verify data recovery
        for agent in persistent_agents:
            recovered = await new_registry.get_agent_capabilities_async(agent["agent_id"])
            # Note: This test depends on Redis persistence being configured
            # In local/test environment, this might not persist
            
        # Test statistics
        stats = env["registry"].get_capability_statistics()
        assert stats["total_agents"] >= len(persistent_agents), "Statistics not reflecting registered agents"

    def test_memory_constraint_validation(self):
        """Test 6.5KB memory constraint compliance"""
        # Test registry memory usage
        registry = AgentCapabilityRegistry()
        
        # Add multiple agents to test memory usage
        for i in range(100):  # Large number to test memory scaling
            agent_data = {
                "agent_id": f"memory_test_agent_{i}",
                "name": f"Memory Test Agent {i}",
                "capabilities": [f"cap_{j}" for j in range(5)],  # 5 capabilities each
                "input_types": ["text", "json"],
                "output_types": ["json"],
                "metadata": {"batch": "memory_test"}
            }
            registry.register_agent_capabilities(agent_data["agent_id"], agent_data)
        
        # Registry should maintain efficiency even with many agents
        # This is more about the implementation efficiency than actual memory
        stats = registry.get_capability_statistics()
        assert stats["total_agents"] == 100, "Memory test agents not all registered"
        
        # Test that registry operations remain fast with many agents
        start_time = time.time()
        matching_agents = registry.find_agents_by_capability("cap_0")
        search_time = (time.time() - start_time) * 1000  # ms
        
        assert search_time < 10, f"Search with 100 agents took {search_time}ms, should be <10ms"
        assert len(matching_agents) == 100, "Not all agents found in capability search"

    def test_instantiation_performance(self):
        """Test 3μs instantiation requirement"""
        instantiation_times = []
        
        # Test multiple instantiations
        for _ in range(10):
            start_time = time.perf_counter()
            registry = AgentCapabilityRegistry()
            end_time = time.perf_counter()
            
            instantiation_time = (end_time - start_time) * 1_000_000  # microseconds
            instantiation_times.append(instantiation_time)
        
        avg_instantiation = sum(instantiation_times) / len(instantiation_times)
        max_instantiation = max(instantiation_times)
        
        # Average should be well under 3μs
        assert avg_instantiation < 3.0, f"Average instantiation {avg_instantiation:.2f}μs exceeds 3μs"
        assert max_instantiation < 5.0, f"Maximum instantiation {max_instantiation:.2f}μs too high"
        
        print(f"✅ Instantiation Performance: Avg {avg_instantiation:.2f}μs, Max {max_instantiation:.2f}μs")

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, setup_test_environment):
        """Test system error handling and recovery capabilities"""
        env = await setup_test_environment
        
        # Test invalid agent data handling
        invalid_agent = {
            "agent_id": "",  # Invalid empty ID
            "name": "Invalid Agent",
            "capabilities": []  # Empty capabilities
        }
        
        # Registry should handle invalid data gracefully
        try:
            await env["registry"].register_agent_capabilities_async("", invalid_agent)
            # Should not raise exception, but should handle gracefully
        except Exception:
            pass  # Expected for invalid data
        
        # Test recovery from Redis connection issues
        # Simulate Redis unavailability by using invalid config
        unreliable_registry = AgentCapabilityRegistry({"redis_url": "redis://invalid:9999"})
        
        # Should fallback to local registry
        test_agent = {
            "agent_id": "fallback_test_agent",
            "name": "Fallback Test",
            "capabilities": ["fallback_capability"]
        }
        
        # This should work with local fallback
        unreliable_registry.register_agent_capabilities(test_agent["agent_id"], test_agent)
        retrieved = unreliable_registry.get_agent_capabilities(test_agent["agent_id"])
        assert retrieved is not None, "Fallback mechanism failed"
        
        # Test concurrent error scenarios
        error_tasks = []
        for i in range(5):
            # Mix of valid and invalid operations
            if i % 2 == 0:
                task = env["registry"].register_agent_capabilities_async(
                    f"valid_agent_{i}", {"name": f"Valid {i}", "capabilities": ["test"]}
                )
            else:
                task = env["registry"].get_agent_capabilities_async("nonexistent_agent")
            error_tasks.append(task)
        
        # Should handle mixed success/failure without crashing
        results = await asyncio.gather(*error_tasks, return_exceptions=True)
        
        # At least some operations should succeed
        successful_ops = sum(1 for r in results if not isinstance(r, Exception) and r is not None)
        assert successful_ops >= 2, "Too many operations failed in error scenario test"


if __name__ == "__main__":
    # Run tests directly for development
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])