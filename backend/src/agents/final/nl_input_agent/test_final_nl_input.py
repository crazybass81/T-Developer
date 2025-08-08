"""
Comprehensive test suite for Final NL Input Agent
Tests all processing modes and features
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FINAL_NL_INPUT_AGENT import (
    FinalNLInputAgent,
    ProcessingMode,
    ProjectRequirements,
    create_fast_processor,
    create_standard_processor,
    create_advanced_processor,
    create_enterprise_processor,
    lambda_handler,
    create_nl_input_api
)


class TestFinalNLInputAgent:
    """Comprehensive test suite for Final NL Input Agent"""
    
    @pytest.fixture
    async def fast_agent(self):
        """Create FAST mode agent"""
        agent = FinalNLInputAgent(mode=ProcessingMode.FAST)
        await agent.initialize()
        yield agent
        await agent.cleanup()
    
    @pytest.fixture
    async def standard_agent(self):
        """Create STANDARD mode agent"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key',
            'REDIS_URL': 'redis://localhost:6379'
        }):
            agent = FinalNLInputAgent(mode=ProcessingMode.STANDARD)
            # Mock AI clients
            agent.anthropic_client = AsyncMock()
            agent.openai_client = AsyncMock()
            agent.redis_client = AsyncMock()
            await agent.initialize()
            yield agent
            await agent.cleanup()
    
    @pytest.fixture
    async def advanced_agent(self):
        """Create ADVANCED mode agent"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key',
            'REDIS_URL': 'redis://localhost:6379'
        }):
            agent = FinalNLInputAgent(mode=ProcessingMode.ADVANCED)
            agent.anthropic_client = AsyncMock()
            agent.openai_client = AsyncMock()
            agent.redis_client = AsyncMock()
            await agent.initialize()
            yield agent
            await agent.cleanup()
    
    @pytest.fixture
    async def enterprise_agent(self):
        """Create ENTERPRISE mode agent"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key',
            'REDIS_URL': 'redis://localhost:6379',
            'AWS_REGION': 'us-east-1'
        }):
            agent = FinalNLInputAgent(mode=ProcessingMode.ENTERPRISE)
            agent.anthropic_client = AsyncMock()
            agent.openai_client = AsyncMock()
            agent.redis_client = AsyncMock()
            await agent.initialize()
            yield agent
            await agent.cleanup()
    
    # Test initialization
    @pytest.mark.asyncio
    async def test_fast_mode_initialization(self, fast_agent):
        """Test FAST mode initialization"""
        assert fast_agent.mode == ProcessingMode.FAST
        assert fast_agent.anthropic_client is None
        assert fast_agent.redis_client is None
        assert not fast_agent.cache_enabled
    
    @pytest.mark.asyncio
    async def test_standard_mode_initialization(self, standard_agent):
        """Test STANDARD mode initialization"""
        assert standard_agent.mode == ProcessingMode.STANDARD
        assert standard_agent.anthropic_client is not None
        assert standard_agent.redis_client is not None
        assert standard_agent.cache_enabled
    
    @pytest.mark.asyncio
    async def test_advanced_mode_initialization(self, advanced_agent):
        """Test ADVANCED mode initialization"""
        assert advanced_agent.mode == ProcessingMode.ADVANCED
        assert hasattr(advanced_agent, 'intent_analyzer')
        assert hasattr(advanced_agent, 'priority_analyzer')
        assert hasattr(advanced_agent, 'domain_processor')
    
    @pytest.mark.asyncio
    async def test_enterprise_mode_initialization(self, enterprise_agent):
        """Test ENTERPRISE mode initialization"""
        assert enterprise_agent.mode == ProcessingMode.ENTERPRISE
        assert hasattr(enterprise_agent, 'metrics')
        assert hasattr(enterprise_agent, 'circuit_breaker')
        assert hasattr(enterprise_agent, 'compliance_checker')
    
    # Test basic processing
    @pytest.mark.asyncio
    async def test_fast_processing(self, fast_agent):
        """Test FAST mode processing"""
        query = "Create a React todo app with TypeScript"
        
        result = await fast_agent.process(query)
        
        assert isinstance(result, ProjectRequirements)
        assert result.project_type == "web_app"
        assert "React" in str(result.technical_requirements)
        assert "TypeScript" in str(result.technical_requirements)
        assert result.confidence_score > 0
        assert result.processing_time < 0.5  # Should be very fast
    
    @pytest.mark.asyncio
    async def test_standard_processing_with_cache(self, standard_agent):
        """Test STANDARD mode with caching"""
        query = "Build an e-commerce platform with payment integration"
        
        # Mock AI response
        standard_agent.anthropic_client.messages.create = AsyncMock(
            return_value=Mock(content=[Mock(text=json.dumps({
                "project_type": "e-commerce",
                "features": ["payment", "shopping cart", "user accounts"],
                "technical_requirements": {
                    "frameworks": ["react", "node.js"],
                    "databases": ["postgresql"],
                    "integrations": ["stripe", "paypal"]
                }
            }))])
        )
        
        # Mock cache
        standard_agent.redis_client.get = AsyncMock(return_value=None)
        standard_agent.redis_client.setex = AsyncMock()
        
        # First call (no cache)
        result1 = await standard_agent.process(query)
        assert result1.project_type == "e-commerce"
        assert "payment" in result1.features
        
        # Verify cache was set
        standard_agent.redis_client.setex.assert_called_once()
        
        # Second call (with cache)
        cached_data = result1.dict()
        standard_agent.redis_client.get = AsyncMock(
            return_value=json.dumps(cached_data)
        )
        
        result2 = await standard_agent.process(query)
        assert result2.project_type == result1.project_type
        assert result2.features == result1.features
    
    @pytest.mark.asyncio
    async def test_advanced_intent_analysis(self, advanced_agent):
        """Test ADVANCED mode intent analysis"""
        query = "I urgently need a mobile app for iOS that tracks fitness activities"
        
        # Mock intent analyzer
        advanced_agent.intent_analyzer = AsyncMock(
            return_value={
                "primary_intent": "create_mobile_app",
                "urgency": "high",
                "domain": "fitness",
                "platform": "ios"
            }
        )
        
        # Mock priority analyzer
        advanced_agent.priority_analyzer = AsyncMock(
            return_value={
                "priority_score": 0.9,
                "critical_features": ["activity_tracking", "ios_native"],
                "nice_to_have": ["social_sharing", "analytics"]
            }
        )
        
        result = await advanced_agent.process(query)
        
        assert result.project_type == "mobile_app"
        assert result.metadata.get("urgency") == "high"
        assert result.metadata.get("domain") == "fitness"
        assert result.metadata.get("priority_score") == 0.9
    
    @pytest.mark.asyncio
    async def test_enterprise_compliance_check(self, enterprise_agent):
        """Test ENTERPRISE mode compliance checking"""
        query = "Build a healthcare app that stores patient data"
        
        # Mock compliance checker
        enterprise_agent.compliance_checker = AsyncMock(
            return_value={
                "requirements": ["HIPAA", "GDPR"],
                "security_measures": ["encryption", "access_control", "audit_logs"],
                "data_residency": ["US", "EU"]
            }
        )
        
        result = await enterprise_agent.process(query)
        
        assert "HIPAA" in result.non_functional_requirements.get("compliance", [])
        assert "encryption" in result.non_functional_requirements.get("security", [])
    
    # Test multilingual support
    @pytest.mark.asyncio
    async def test_multilingual_processing(self, advanced_agent):
        """Test multilingual query processing"""
        queries = [
            ("Créer une application web", "fr"),  # French
            ("Crear una aplicación móvil", "es"),  # Spanish
            ("ウェブアプリを作成", "ja"),  # Japanese
            ("웹 앱 만들기", "ko"),  # Korean
        ]
        
        for query, lang in queries:
            # Mock language detection
            with patch('FINAL_NL_INPUT_AGENT.detect', return_value=lang):
                result = await advanced_agent.process(query)
                assert result.project_type in ["web_app", "mobile_app"]
                assert result.metadata.get("detected_language") == lang
    
    # Test error handling
    @pytest.mark.asyncio
    async def test_empty_query_handling(self, fast_agent):
        """Test handling of empty queries"""
        with pytest.raises(ValueError, match="Empty query"):
            await fast_agent.process("")
        
        with pytest.raises(ValueError, match="Empty query"):
            await fast_agent.process("   ")
    
    @pytest.mark.asyncio
    async def test_ai_fallback_to_rules(self, standard_agent):
        """Test fallback to rule-based when AI fails"""
        query = "Create a simple website"
        
        # Make AI fail
        standard_agent.anthropic_client.messages.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        standard_agent.openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        # Should fallback to rule-based
        result = await standard_agent.process(query)
        
        assert result.project_type == "web_app"
        assert result.metadata.get("processing_method") == "rule_based"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self, enterprise_agent):
        """Test circuit breaker functionality"""
        query = "Create an app"
        
        # Simulate multiple failures
        enterprise_agent.anthropic_client.messages.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        # Process multiple times to trigger circuit breaker
        for _ in range(5):
            result = await enterprise_agent.process(query)
            assert result.project_type is not None  # Should still work with fallback
        
        # Circuit should be open now
        assert enterprise_agent.circuit_breaker.is_open
    
    # Test performance
    @pytest.mark.asyncio
    async def test_performance_requirements(self, fast_agent):
        """Test performance requirements for each mode"""
        queries = [
            "Create a todo app",
            "Build an e-commerce platform with React and Node.js",
            "Develop a mobile app for iOS and Android with real-time chat"
        ]
        
        for query in queries:
            start = asyncio.get_event_loop().time()
            result = await fast_agent.process(query)
            elapsed = asyncio.get_event_loop().time() - start
            
            # FAST mode should process in < 100ms
            assert elapsed < 0.1
            assert result is not None
    
    # Test complex queries
    @pytest.mark.asyncio
    async def test_complex_query_extraction(self, advanced_agent):
        """Test extraction from complex queries"""
        query = """
        I need a comprehensive e-commerce platform with the following features:
        - User authentication with OAuth2 (Google, Facebook)
        - Product catalog with search and filters
        - Shopping cart and checkout with Stripe integration
        - Admin dashboard for inventory management
        - Real-time order tracking
        - Mobile responsive design
        - Multi-language support (English, Spanish, French)
        - Email notifications
        - Analytics and reporting
        
        Tech stack preferences:
        - Frontend: React with TypeScript
        - Backend: Node.js with Express
        - Database: PostgreSQL
        - Cache: Redis
        - Deployment: AWS with Docker
        
        Must comply with PCI DSS for payment processing.
        Target launch in 3 months with a team of 4 developers.
        """
        
        result = await advanced_agent.process(query)
        
        assert result.project_type == "e-commerce"
        assert len(result.features) >= 8
        assert "OAuth2" in str(result.technical_requirements)
        assert "Stripe" in str(result.technical_requirements)
        assert "React" in str(result.technical_requirements)
        assert "PostgreSQL" in str(result.technical_requirements)
        assert "PCI DSS" in str(result.non_functional_requirements)
        assert result.constraints.get("timeline") == "3 months"
        assert result.constraints.get("team_size") == 4
        assert result.estimated_complexity in ["high", "very_high"]
    
    # Test convenience functions
    @pytest.mark.asyncio
    async def test_convenience_creators():
        """Test convenience creator functions"""
        processors = [
            await create_fast_processor(),
            await create_standard_processor(),
            await create_advanced_processor(),
            await create_enterprise_processor()
        ]
        
        for processor in processors:
            assert processor is not None
            result = await processor.process("Create a simple app")
            assert result.project_type is not None
            await processor.cleanup()
    
    # Test Lambda handler
    def test_lambda_handler_success(self):
        """Test Lambda handler with successful processing"""
        event = {
            'body': json.dumps({
                'query': 'Create a todo app with React',
                'mode': 'FAST'
            })
        }
        
        with patch('FINAL_NL_INPUT_AGENT.FinalNLInputAgent') as MockAgent:
            mock_instance = AsyncMock()
            MockAgent.return_value = mock_instance
            mock_instance.process = AsyncMock(
                return_value=ProjectRequirements(
                    project_type="web_app",
                    project_name="TodoApp",
                    description="Todo application",
                    features=["tasks", "categories"],
                    technical_requirements={
                        "frameworks": ["react"],
                        "languages": ["javascript"]
                    },
                    non_functional_requirements={},
                    constraints={},
                    estimated_complexity="low",
                    confidence_score=0.8,
                    metadata={},
                    processing_time=0.05
                )
            )
            
            # Need to run in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            response = lambda_handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['project_type'] == 'web_app'
            assert body['confidence_score'] == 0.8
    
    def test_lambda_handler_error(self):
        """Test Lambda handler with error"""
        event = {
            'body': json.dumps({
                'query': ''  # Empty query
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
    
    # Test FastAPI integration
    @pytest.mark.asyncio
    async def test_fastapi_integration(self):
        """Test FastAPI app creation"""
        from fastapi.testclient import TestClient
        
        app = create_nl_input_api()
        client = TestClient(app)
        
        # Test health check
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test processing endpoint
        response = client.post(
            "/process",
            json={
                "query": "Create a blog platform",
                "mode": "FAST"
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert result['project_type'] in ['web_app', 'blog']
    
    # Test multimodal processing
    @pytest.mark.asyncio
    async def test_multimodal_image_processing(self, advanced_agent):
        """Test image input processing"""
        query = "Create an app like this"
        image_path = "/tmp/mockup.png"
        
        # Mock image processing
        with patch('FINAL_NL_INPUT_AGENT.process_image_requirements') as mock_process:
            mock_process.return_value = {
                "detected_ui_elements": ["header", "navigation", "cards"],
                "color_scheme": ["blue", "white"],
                "layout": "grid"
            }
            
            result = await advanced_agent.process(
                query,
                additional_inputs={"image": image_path}
            )
            
            assert result.metadata.get("multimodal_input") == True
            assert "detected_ui_elements" in result.metadata
    
    # Test template learning
    @pytest.mark.asyncio
    async def test_template_learning(self, advanced_agent):
        """Test learning from previous requirements"""
        # Process similar queries
        queries = [
            "Create an e-commerce site with cart and checkout",
            "Build an online store with shopping features",
            "Develop an e-commerce platform with payment"
        ]
        
        results = []
        for query in queries:
            result = await advanced_agent.process(query)
            results.append(result)
        
        # Should learn common patterns
        assert all(r.project_type == "e-commerce" for r in results)
        
        # Later queries should have higher confidence
        assert results[-1].confidence_score >= results[0].confidence_score
    
    # Test priority analysis
    @pytest.mark.asyncio
    async def test_priority_analysis_mcdm(self, advanced_agent):
        """Test MCDM-based priority analysis"""
        query = """
        Critical: User authentication and security
        Important: Payment processing
        Nice to have: Social sharing
        Optional: Advanced analytics
        """
        
        result = await advanced_agent.process(query)
        
        priorities = result.metadata.get("feature_priorities", {})
        assert priorities.get("authentication", 0) > priorities.get("social_sharing", 0)
        assert priorities.get("payment", 0) > priorities.get("analytics", 0)
    
    # Test performance optimization
    @pytest.mark.asyncio
    async def test_query_optimization(self, advanced_agent):
        """Test query optimization features"""
        # Long, redundant query
        query = """
        I want to create a web application. The web application should be a todo app.
        The todo app needs to have tasks. Tasks should be creatable. Tasks should be editable.
        Tasks should be deletable. The app needs a database. Use PostgreSQL database.
        The frontend should be React. Use React for the frontend. Deploy on AWS.
        """
        
        result = await advanced_agent.process(query)
        
        # Should optimize and extract key requirements
        assert result.project_type == "web_app"
        assert "todo" in result.project_name.lower()
        assert "PostgreSQL" in str(result.technical_requirements)
        assert "React" in str(result.technical_requirements)
        assert "AWS" in str(result.technical_requirements)
        
        # Optimized query should be shorter
        assert len(result.metadata.get("optimized_query", query)) < len(query)
    
    # Test health monitoring
    @pytest.mark.asyncio
    async def test_health_check(self, enterprise_agent):
        """Test health check functionality"""
        health = await enterprise_agent.health_check()
        
        assert health['status'] in ['healthy', 'degraded', 'unhealthy']
        assert 'components' in health
        assert 'ai_providers' in health['components']
        assert 'cache' in health['components']
        assert 'metrics' in health
    
    # Test metrics collection
    @pytest.mark.asyncio
    async def test_metrics_collection(self, enterprise_agent):
        """Test metrics collection in enterprise mode"""
        queries = [
            "Create a simple app",
            "Build a complex platform",
            "Develop a mobile application"
        ]
        
        for query in queries:
            await enterprise_agent.process(query)
        
        metrics = enterprise_agent.get_metrics()
        
        assert metrics['total_requests'] == 3
        assert metrics['average_processing_time'] > 0
        assert metrics['cache_hit_rate'] >= 0
        assert 'success_rate' in metrics
        assert 'ai_provider_usage' in metrics


class TestIntegration:
    """Integration tests for Final NL Input Agent"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_integration(self):
        """Test full processing pipeline"""
        agent = FinalNLInputAgent(mode=ProcessingMode.ADVANCED)
        await agent.initialize()
        
        try:
            query = """
            Build a SaaS platform for project management with:
            - Multi-tenant architecture
            - Real-time collaboration
            - Kanban boards
            - Time tracking
            - Reporting dashboard
            - Mobile apps
            - API for integrations
            Tech: React, Node.js, PostgreSQL, Redis
            """
            
            result = await agent.process(query)
            
            # Verify comprehensive extraction
            assert result.project_type in ["saas", "web_app"]
            assert len(result.features) >= 6
            assert result.estimated_complexity in ["high", "very_high"]
            assert "multi-tenant" in str(result.non_functional_requirements).lower()
            assert all(tech in str(result.technical_requirements) 
                      for tech in ["React", "Node.js", "PostgreSQL", "Redis"])
            
        finally:
            await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_mode_switching(self):
        """Test switching between processing modes"""
        queries = [
            ("Quick todo app", ProcessingMode.FAST),
            ("E-commerce platform with payments", ProcessingMode.STANDARD),
            ("Enterprise CRM system", ProcessingMode.ENTERPRISE)
        ]
        
        for query, mode in queries:
            agent = FinalNLInputAgent(mode=mode)
            await agent.initialize()
            
            try:
                result = await agent.process(query)
                assert result is not None
                assert result.metadata.get("processing_mode") == mode.value
                
                # Check mode-specific features
                if mode == ProcessingMode.FAST:
                    assert result.processing_time < 0.1
                elif mode == ProcessingMode.ENTERPRISE:
                    assert "compliance" in result.non_functional_requirements
                
            finally:
                await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent request handling"""
        agent = FinalNLInputAgent(mode=ProcessingMode.STANDARD)
        await agent.initialize()
        
        try:
            queries = [
                "Create a blog",
                "Build an API",
                "Develop a mobile app",
                "Make a dashboard",
                "Design a chatbot"
            ]
            
            # Process concurrently
            tasks = [agent.process(q) for q in queries]
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == len(queries)
            assert all(r.project_type is not None for r in results)
            
            # Each should be different
            project_types = [r.project_type for r in results]
            assert len(set(project_types)) > 1
            
        finally:
            await agent.cleanup()


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=FINAL_NL_INPUT_AGENT",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_report",
        "-x"  # Stop on first failure
    ])