"""
Test Suite for Unified Agent System
Tests all 9 agents and orchestrator
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.unified.unified_agents import (
    UnifiedNLInputAgent,
    UnifiedUISelectionAgent,
    UnifiedParserAgent,
    UnifiedComponentDecisionAgent,
    UnifiedMatchRateAgent,
    UnifiedSearchAgent,
    UnifiedGenerationAgent,
    UnifiedAssemblyAgent,
    UnifiedDownloadAgent
)
from src.agents.unified.orchestrator import UnifiedOrchestrator
from src.agents.enterprise.base_agent import AgentContext


@pytest.fixture
def agent_context():
    """Create test context"""
    return AgentContext(
        trace_id="test-trace-123",
        user_id="test-user",
        tenant_id="test-tenant"
    )


@pytest.fixture
def sample_requirements():
    """Sample requirements for testing"""
    return {
        "project_type": "web_app",
        "project_name": "Test Project",
        "description": "A test web application",
        "features": ["authentication", "dashboard", "api"],
        "technical_requirements": {
            "languages": ["python", "javascript"],
            "frameworks": ["fastapi", "react"],
            "databases": ["postgresql"]
        },
        "estimated_complexity": "medium"
    }


class TestUnifiedNLInputAgent:
    """Test NL Input Agent"""
    
    @pytest.mark.asyncio
    async def test_nl_input_basic(self, agent_context):
        """Test basic NL processing"""
        agent = UnifiedNLInputAgent()
        await agent.initialize()
        
        result = await agent.process(
            {"query": "Create a web app with user authentication"},
            agent_context
        )
        
        assert result is not None
        assert "project_type" in result
        assert "features" in result
        
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_nl_input_fallback(self, agent_context):
        """Test fallback to rule-based processing"""
        agent = UnifiedNLInputAgent()
        # Don't initialize AI providers
        
        result = await agent.process(
            {"query": "Build a mobile app"},
            agent_context
        )
        
        assert result is not None
        assert result.get("project_type") == "mobile"


class TestUnifiedUISelectionAgent:
    """Test UI Selection Agent"""
    
    @pytest.mark.asyncio
    async def test_ui_selection(self, agent_context, sample_requirements):
        """Test UI framework selection"""
        agent = UnifiedUISelectionAgent()
        await agent.initialize()
        
        result = await agent.process(
            {"requirements": sample_requirements},
            agent_context
        )
        
        assert result is not None
        assert "selected_framework" in result
        assert "scores" in result
        assert "alternatives" in result
        
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_ui_selection_react(self, agent_context):
        """Test React selection for web app"""
        agent = UnifiedUISelectionAgent()
        
        requirements = {
            "project_type": "web_app",
            "features": ["dashboard", "real-time"],
            "estimated_complexity": "high"
        }
        
        result = await agent.process(
            {"requirements": requirements},
            agent_context
        )
        
        # React should score high for complex web apps
        assert result["selected_framework"]["id"] in ["react", "nextjs"]


class TestUnifiedParserAgent:
    """Test Parser Agent"""
    
    @pytest.mark.asyncio
    async def test_parse_requirements(self, agent_context, sample_requirements):
        """Test requirements parsing"""
        agent = UnifiedParserAgent()
        await agent.initialize()
        
        result = await agent.process(
            {"type": "requirements", "requirements": sample_requirements},
            agent_context
        )
        
        assert result is not None
        assert "components" in result
        assert "models" in result
        assert "endpoints" in result
        
        # Check for auth component
        auth_component = next(
            (c for c in result["components"] if "auth" in c["name"].lower()),
            None
        )
        assert auth_component is not None
        
        await agent.cleanup()


class TestUnifiedComponentDecisionAgent:
    """Test Component Decision Agent"""
    
    @pytest.mark.asyncio
    async def test_component_decision(self, agent_context, sample_requirements):
        """Test component selection"""
        agent = UnifiedComponentDecisionAgent()
        await agent.initialize()
        
        result = await agent.process(
            {
                "requirements": sample_requirements,
                "parsed_data": {"components": []}
            },
            agent_context
        )
        
        assert result is not None
        assert "selected_components" in result
        assert "database" in result["selected_components"]
        
        await agent.cleanup()


class TestUnifiedMatchRateAgent:
    """Test Match Rate Agent"""
    
    @pytest.mark.asyncio
    async def test_match_rate(self, agent_context, sample_requirements):
        """Test template matching"""
        agent = UnifiedMatchRateAgent()
        await agent.initialize()
        
        result = await agent.process(
            {"requirements": sample_requirements},
            agent_context
        )
        
        assert result is not None
        assert "best_match" in result
        assert "alternatives" in result
        assert "recommendation" in result
        
        await agent.cleanup()


class TestUnifiedSearchAgent:
    """Test Search Agent"""
    
    @pytest.mark.asyncio
    async def test_search(self, agent_context, sample_requirements):
        """Test code search"""
        agent = UnifiedSearchAgent()
        await agent.initialize()
        
        result = await agent.process(
            {
                "query": "authentication",
                "requirements": sample_requirements
            },
            agent_context
        )
        
        assert result is not None
        assert "code_snippets" in result
        assert "patterns" in result
        assert "libraries" in result
        
        await agent.cleanup()


class TestUnifiedGenerationAgent:
    """Test Generation Agent"""
    
    @pytest.mark.asyncio
    async def test_generation(self, agent_context, sample_requirements):
        """Test code generation"""
        agent = UnifiedGenerationAgent()
        await agent.initialize()
        
        result = await agent.process(
            {
                "requirements": sample_requirements,
                "ui_framework": {"selected_framework": {"id": "react"}},
                "components": {"database": {"name": "PostgreSQL"}},
                "templates": {}
            },
            agent_context
        )
        
        assert result is not None
        assert "structure" in result
        assert "files" in result
        assert "package" in result["files"]
        assert "main" in result["files"]
        
        await agent.cleanup()


class TestUnifiedAssemblyAgent:
    """Test Assembly Agent"""
    
    @pytest.mark.asyncio
    async def test_assembly(self, agent_context):
        """Test project assembly"""
        agent = UnifiedAssemblyAgent()
        await agent.initialize()
        
        files = {
            "package": {"filename": "package.json", "content": "{}"},
            "main": {"filename": "src/main.js", "content": "// Main"},
            "config": [
                {"filename": ".env", "content": "NODE_ENV=test"}
            ]
        }
        
        result = await agent.process(
            {"files": files, "structure": {}},
            agent_context
        )
        
        assert result is not None
        assert "project" in result
        assert "validation" in result
        assert result["validation"]["is_valid"] is False  # Missing README
        
        await agent.cleanup()


class TestUnifiedDownloadAgent:
    """Test Download Agent"""
    
    @pytest.mark.asyncio
    async def test_download(self, agent_context):
        """Test project packaging"""
        agent = UnifiedDownloadAgent()
        await agent.initialize()
        
        project = {
            "package.json": '{"name": "test"}',
            "src/main.js": "console.log('test');"
        }
        
        result = await agent.process(
            {
                "project": project,
                "metadata": {"project_name": "test-project"}
            },
            agent_context
        )
        
        assert result is not None
        assert "download_url" in result
        assert "size_bytes" in result
        assert "checksum" in result
        
        await agent.cleanup()


class TestUnifiedOrchestrator:
    """Test Orchestrator"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        orchestrator = UnifiedOrchestrator()
        await orchestrator.initialize()
        
        # Check all agents initialized
        assert len(orchestrator.agents) == 9
        
        await orchestrator.cleanup()
    
    @pytest.mark.asyncio
    async def test_orchestrator_health_check(self):
        """Test health check"""
        orchestrator = UnifiedOrchestrator()
        await orchestrator.initialize()
        
        health = await orchestrator.health_check()
        
        assert health is not None
        assert "orchestrator" in health
        assert "agents" in health
        assert len(health["agents"]) == 9
        
        await orchestrator.cleanup()
    
    @pytest.mark.asyncio
    async def test_orchestrator_pipeline_basic(self):
        """Test basic pipeline execution"""
        orchestrator = UnifiedOrchestrator()
        await orchestrator.initialize()
        
        # Mock agent responses for speed
        for agent_name, agent in orchestrator.agents.items():
            agent.process = AsyncMock(return_value={"mocked": True})
        
        result = await orchestrator.execute_pipeline(
            query="Create a simple web app",
            user_id="test-user"
        )
        
        assert result is not None
        assert "success" in result
        assert "trace_id" in result
        
        await orchestrator.cleanup()
    
    @pytest.mark.asyncio
    async def test_orchestrator_stage_failure_handling(self):
        """Test handling of stage failures"""
        orchestrator = UnifiedOrchestrator()
        await orchestrator.initialize()
        
        # Mock NL Input to fail (critical agent)
        orchestrator.agents["nl_input"].process = AsyncMock(
            side_effect=Exception("Test failure")
        )
        
        result = await orchestrator.execute_pipeline(
            query="Test query"
        )
        
        assert result is not None
        assert result["success"] is False
        
        await orchestrator.cleanup()
    
    @pytest.mark.asyncio
    async def test_orchestrator_non_critical_failure(self):
        """Test non-critical agent failure"""
        orchestrator = UnifiedOrchestrator()
        await orchestrator.initialize()
        
        # Mock most agents
        for agent_name, agent in orchestrator.agents.items():
            if agent_name == "search":
                # Search fails (non-critical)
                agent.process = AsyncMock(side_effect=Exception("Search failed"))
            else:
                agent.process = AsyncMock(return_value={"mocked": True})
        
        result = await orchestrator.execute_pipeline(
            query="Test query"
        )
        
        # Pipeline should continue despite search failure
        assert result is not None
        # Success depends on other agents
        
        await orchestrator.cleanup()


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_pipeline_integration(self):
        """Test complete pipeline with real agents"""
        orchestrator = UnifiedOrchestrator()
        await orchestrator.initialize()
        
        # Run with simple query
        result = await orchestrator.execute_pipeline(
            query="Create a TODO app with React and Python backend"
        )
        
        assert result is not None
        assert "trace_id" in result
        
        if result.get("success"):
            assert "download_url" in result
            assert "project_details" in result
            
            details = result["project_details"]
            assert details["requirements"] is not None
            assert details["framework"] is not None
        
        await orchestrator.cleanup()


# Benchmark tests
class TestPerformance:
    """Performance benchmarks"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_agent_performance(self, agent_context, sample_requirements):
        """Benchmark individual agent performance"""
        import time
        
        agents = [
            UnifiedNLInputAgent(),
            UnifiedUISelectionAgent(),
            UnifiedParserAgent(),
            UnifiedComponentDecisionAgent(),
            UnifiedMatchRateAgent(),
            UnifiedSearchAgent()
        ]
        
        for agent in agents:
            await agent.initialize()
            
            start = time.time()
            
            # Run agent
            if isinstance(agent, UnifiedNLInputAgent):
                input_data = {"query": "Test query"}
            else:
                input_data = {"requirements": sample_requirements}
            
            await agent.process(input_data, agent_context)
            
            duration = time.time() - start
            
            # Check performance
            assert duration < agent.config.timeout, \
                f"{agent.config.name} took {duration}s (timeout: {agent.config.timeout}s)"
            
            await agent.cleanup()
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_pipeline_performance(self):
        """Benchmark full pipeline performance"""
        import time
        
        orchestrator = UnifiedOrchestrator()
        await orchestrator.initialize()
        
        # Mock heavy operations
        orchestrator.agents["generation"].process = AsyncMock(
            return_value={"files": {}, "structure": {}}
        )
        
        start = time.time()
        
        result = await orchestrator.execute_pipeline(
            query="Create a simple app"
        )
        
        duration = time.time() - start
        
        # Pipeline should complete within reasonable time
        assert duration < 120, f"Pipeline took {duration}s"
        
        await orchestrator.cleanup()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])