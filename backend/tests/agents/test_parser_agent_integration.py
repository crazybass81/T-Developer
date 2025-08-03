# backend/tests/agents/test_parser_agent_integration.py
import pytest
import asyncio
from unittest.mock import Mock, patch

class TestParserAgentIntegration:
    """Parser Agent 통합 테스트"""

    @pytest.fixture
    async def parser_agent(self):
        """Parser Agent 인스턴스"""
        from parser_agent import ParserAgent
        
        agent = ParserAgent()
        await agent.initialize()
        yield agent
        await agent.cleanup()

    @pytest.fixture
    def test_requirements(self):
        """다양한 테스트 요구사항"""
        return [
            {
                "name": "E-commerce Platform",
                "description": """
                We need to build a modern e-commerce platform that supports multiple vendors.

                The system MUST support user registration and authentication using OAuth 2.0.
                Users SHALL be able to browse products, add items to cart, and checkout.

                The platform SHOULD handle at least 10,000 concurrent users and respond
                within 200ms for product searches. Payment processing MUST be PCI compliant.

                Key features include:
                - Product catalog with categories and filters
                - Shopping cart with session persistence
                - Order management system
                - Inventory tracking with real-time updates
                - Customer reviews and ratings
                - Admin dashboard for vendors

                The system will integrate with Stripe for payments, SendGrid for emails,
                and use PostgreSQL for the main database with Redis for caching.

                Mobile apps for iOS and Android are required, using React Native.
                The web frontend should be built with Next.js for SEO optimization.

                API endpoints needed:
                - GET /api/products?category={category}&page={page}
                - POST /api/cart/items
                - PUT /api/orders/{orderId}/status
                - DELETE /api/cart/items/{itemId}

                Data models:
                - User entity with fields: id, email, name, password_hash, created_at
                - Product entity with fields: id, name, description, price, stock_quantity
                - Order entity with fields: id, user_id, total_amount, status, created_at
                """,
                "expected_counts": {
                    "functional_requirements": 15,
                    "non_functional_requirements": 5,
                    "technical_requirements": 8,
                    "api_endpoints": 4,
                    "data_models": 3
                }
            },
            {
                "name": "Healthcare Management System",
                "description": """
                Develop a HIPAA-compliant healthcare management system for clinics.

                CRITICAL REQUIREMENTS:
                - All patient data MUST be encrypted at rest and in transit
                - System MUST maintain audit logs for all data access
                - Role-based access control is REQUIRED

                The system should support appointment scheduling, patient records,
                prescription management, and billing. Integration with insurance
                providers is needed via HL7 FHIR standards.

                Performance requirements:
                - Support 500 concurrent users per clinic
                - Database queries must return within 100ms
                - 99.9% uptime SLA required
                - Automated backups every 6 hours
                """,
                "expected_counts": {
                    "functional_requirements": 8,
                    "non_functional_requirements": 7,
                    "constraints": 4,
                    "business_requirements": 3
                }
            }
        ]

    @pytest.mark.asyncio
    async def test_comprehensive_parsing(self, parser_agent, test_requirements):
        """포괄적인 파싱 테스트"""
        
        for test_case in test_requirements:
            # 요구사항 파싱
            result = await parser_agent.parse_requirements(
                test_case["description"],
                project_context={
                    "name": test_case["name"],
                    "domain": "e-commerce" if "e-commerce" in test_case["name"] else "healthcare"
                }
            )

            # 기본 구조 검증
            assert result.project_info is not None
            assert len(result.functional_requirements) > 0

            # 예상 카운트 검증
            expected = test_case["expected_counts"]

            if "functional_requirements" in expected:
                assert len(result.functional_requirements) >= expected["functional_requirements"] * 0.8

            if "api_endpoints" in expected:
                assert len(result.api_specifications) >= expected["api_endpoints"]

            if "data_models" in expected:
                assert len(result.data_models) >= expected["data_models"]

            # 각 요구사항 검증
            for req in result.functional_requirements:
                assert req.id is not None
                assert req.description != ""
                assert req.priority in ['critical', 'high', 'medium', 'low']

    @pytest.mark.asyncio
    async def test_requirement_separation(self, parser_agent):
        """기능/비기능 요구사항 분리 테스트"""
        
        mixed_requirements = [
            "The system must authenticate users with OAuth 2.0",
            "Response time should be under 200ms",
            "Users can create and manage their profiles",
            "The system must support 10,000 concurrent users",
            "Admin can generate monthly reports"
        ]

        functional_reqs, non_functional_reqs = await parser_agent.requirement_separator.separate_requirements(
            mixed_requirements
        )

        # 기능 요구사항 검증
        functional_descriptions = [req.description for req in functional_reqs]
        assert any("authenticate" in desc for desc in functional_descriptions)
        assert any("create and manage" in desc for desc in functional_descriptions)
        assert any("generate monthly reports" in desc for desc in functional_descriptions)

        # 비기능 요구사항 검증
        non_functional_descriptions = [req.description for req in non_functional_reqs]
        assert any("200ms" in desc for desc in non_functional_descriptions)
        assert any("10,000 concurrent" in desc for desc in non_functional_descriptions)

    @pytest.mark.asyncio
    async def test_dependency_analysis(self, parser_agent):
        """의존성 분석 테스트"""
        
        requirements_with_dependencies = [
            {"id": "REQ-001", "description": "User authentication system with OAuth 2.0"},
            {"id": "REQ-002", "description": "User profile management depends on authentication"},
            {"id": "REQ-003", "description": "Shopping cart functionality"},
            {"id": "REQ-004", "description": "Order processing requires cart and payment"},
            {"id": "REQ-005", "description": "Payment integration with Stripe"},
            {"id": "REQ-006", "description": "Email notifications need user profile"}
        ]

        dependency_graph = await parser_agent.dependency_analyzer.analyze_dependencies(
            requirements_with_dependencies
        )

        # 의존성 그래프 확인
        assert len(dependency_graph.edges) >= 3
        assert len(dependency_graph.cycles) == 0  # 순환 의존성 없음

        # 특정 의존성 확인
        dependency_pairs = [(edge.source_id, edge.target_id) for edge in dependency_graph.edges]
        
        # Order processing이 cart와 payment에 의존하는지 확인
        order_deps = [pair for pair in dependency_pairs if pair[0] == "REQ-004"]
        assert len(order_deps) >= 1

    @pytest.mark.asyncio
    async def test_user_story_generation(self, parser_agent):
        """사용자 스토리 생성 테스트"""
        
        requirements = [
            {
                "id": "REQ-001",
                "description": "Users should be able to search for products by category and price range",
                "priority": "high"
            },
            {
                "id": "REQ-002", 
                "description": "Admin users must be able to manage product inventory",
                "priority": "medium"
            }
        ]

        story_result = await parser_agent.user_story_generator.generate_user_stories(
            requirements
        )

        # 기본 구조 검증
        assert 'user_stories' in story_result
        assert 'epics' in story_result
        assert 'personas' in story_result

        # 사용자 스토리 검증
        user_stories = story_result['user_stories']
        assert len(user_stories) >= 2

        for story in user_stories:
            assert story.id is not None
            assert story.actor is not None
            assert story.goal is not None
            assert story.benefit is not None
            assert len(story.acceptance_criteria) > 0
            assert story.story_points > 0

        # 페르소나 검증
        personas = story_result['personas']
        assert len(personas) >= 1
        
        persona_names = [p['name'] for p in personas]
        assert any('User' in name for name in persona_names)

    @pytest.mark.asyncio
    async def test_nlp_accuracy(self, parser_agent):
        """NLP 처리 정확도 테스트"""
        
        test_sentences = [
            {
                "text": "The system MUST authenticate users with JWT tokens",
                "expected_priority": "high",
                "expected_actor": "system",
                "expected_action": "authenticate"
            },
            {
                "text": "Response time SHOULD be under 200ms for API calls",
                "expected_priority": "medium",
                "expected_category": "performance"
            },
            {
                "text": "Users MAY customize their dashboard layout",
                "expected_priority": "low",
                "expected_actor": "user",
                "expected_action": "customize"
            }
        ]

        for test in test_sentences:
            # 요구사항 분리 테스트
            functional_reqs, non_functional_reqs = await parser_agent.requirement_separator.separate_requirements(
                [test["text"]]
            )

            all_reqs = functional_reqs + non_functional_reqs
            assert len(all_reqs) == 1

            req = all_reqs[0]
            
            # 우선순위 확인
            assert req.priority == test["expected_priority"]
            
            # 액터 확인 (기능 요구사항인 경우)
            if "expected_actor" in test and functional_reqs:
                assert req.actor == test["expected_actor"]
            
            # 액션 확인 (기능 요구사항인 경우)
            if "expected_action" in test and functional_reqs:
                assert req.action == test["expected_action"]
            
            # 카테고리 확인 (비기능 요구사항인 경우)
            if "expected_category" in test and non_functional_reqs:
                assert req.category == test["expected_category"]

    @pytest.mark.performance
    async def test_parsing_performance(self, parser_agent):
        """파싱 성능 테스트"""
        
        # 다양한 길이의 요구사항
        test_texts = [
            "Simple requirement" * 10,  # 짧은 텍스트
            "Medium complexity requirement with details" * 50,  # 중간
            "Complex requirement with multiple sections" * 200  # 긴 텍스트
        ]

        import time
        parsing_times = []

        for text in test_texts:
            start_time = time.time()
            await parser_agent.parse_requirements(text)
            elapsed = time.time() - start_time
            parsing_times.append(elapsed)

        # 성능 메트릭
        avg_time = sum(parsing_times) / len(parsing_times)
        max_time = max(parsing_times)

        # 성능 기준
        assert avg_time < 2.0  # 평균 2초 이내
        assert max_time < 5.0  # 최대 5초 이내

    @pytest.mark.asyncio
    async def test_concurrent_parsing(self, parser_agent):
        """동시 파싱 성능 테스트"""
        
        num_concurrent = 10
        test_requirement = "Build a web application with user authentication and data management"

        async def parse_task():
            return await parser_agent.parse_requirements(test_requirement)

        import time
        start_time = time.time()
        tasks = [parse_task() for _ in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # 모든 결과가 성공적으로 반환되었는지 확인
        assert len(results) == num_concurrent
        assert all(r is not None for r in results)

        # 동시 처리 성능 확인 (10개 요청이 10초 이내)
        assert total_time < 10.0

    @pytest.mark.asyncio
    async def test_error_handling(self, parser_agent):
        """에러 처리 테스트"""
        
        # 빈 입력
        result = await parser_agent.parse_requirements("")
        assert result is not None
        assert len(result.functional_requirements) == 0

        # 잘못된 형식
        result = await parser_agent.parse_requirements("Invalid input @#$%^&*()")
        assert result is not None

        # 매우 긴 입력 (메모리 테스트)
        long_text = "This is a test requirement. " * 10000
        result = await parser_agent.parse_requirements(long_text)
        assert result is not None

    @pytest.mark.asyncio
    async def test_context_awareness(self, parser_agent):
        """컨텍스트 인식 테스트"""
        
        requirement = "Users should be able to make payments"
        
        # E-commerce 컨텍스트
        ecommerce_result = await parser_agent.parse_requirements(
            requirement,
            project_context={"domain": "e-commerce", "type": "web_application"}
        )
        
        # Healthcare 컨텍스트
        healthcare_result = await parser_agent.parse_requirements(
            requirement,
            project_context={"domain": "healthcare", "type": "management_system"}
        )

        # 컨텍스트에 따라 다른 해석이 되어야 함
        assert ecommerce_result.functional_requirements != healthcare_result.functional_requirements

    @pytest.mark.asyncio
    async def test_multilingual_support(self, parser_agent):
        """다국어 지원 테스트 (향후 확장)"""
        
        # 현재는 영어만 지원하지만, 향후 확장을 위한 테스트 구조
        english_req = "Users must be able to login with email and password"
        
        result = await parser_agent.parse_requirements(english_req)
        
        assert len(result.functional_requirements) > 0
        
        # 향후 한국어, 일본어 등 추가 예정
        # korean_req = "사용자는 이메일과 비밀번호로 로그인할 수 있어야 한다"
        # japanese_req = "ユーザーはメールアドレスとパスワードでログインできる必要があります"