# backend/src/agents/implementations/generation/test_generation_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from generation_agent import (
    GenerationAgent, CodeGenerationEngine, TemplateBasedGenerator,
    QualityAssuranceEngine, OptimizationEngine, GenerationRequest, GeneratedCode
)

@pytest.fixture
def generation_request():
    return GenerationRequest(
        component_type="react_component",
        requirements={
            "name": "UserCard",
            "props": ["name", "email", "avatar"],
            "functionality": "Display user information"
        },
        framework="react",
        language="typescript"
    )

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.arun = AsyncMock(return_value="""
    ```typescript
    interface UserCardProps {
        name: string;
        email: string;
        avatar: string;
    }
    
    const UserCard: React.FC<UserCardProps> = ({ name, email, avatar }) => {
        return (
            <div className="user-card">
                <img src={avatar} alt={name} />
                <h3>{name}</h3>
                <p>{email}</p>
            </div>
        );
    };
    
    export default UserCard;
    ```
    
    ```typescript
    // Test file
    import { render, screen } from '@testing-library/react';
    import UserCard from './UserCard';
    
    test('renders user information', () => {
        render(<UserCard name="John" email="john@test.com" avatar="avatar.jpg" />);
        expect(screen.getByText('John')).toBeInTheDocument();
    });
    ```
    """)
    return agent

class TestCodeGenerationEngine:
    @pytest.mark.asyncio
    async def test_generate_component(self, generation_request, mock_agent):
        with patch('generation_agent.Agent', return_value=mock_agent):
            engine = CodeGenerationEngine()
            result = await engine.generate_component(generation_request)
            
            assert isinstance(result, GeneratedCode)
            assert "UserCard" in result.source_code
            assert "test" in result.test_code.lower()
            assert result.quality_score > 0

    def test_parse_generated_response(self):
        engine = CodeGenerationEngine()
        response = """
        Here's the component:
        ```typescript
        const Component = () => <div>Hello</div>;
        ```
        
        And the test:
        ```typescript
        test('renders', () => {});
        ```
        """
        
        result = engine._parse_generated_response(response)
        assert "Component" in result.source_code
        assert "test" in result.test_code

class TestTemplateBasedGenerator:
    @pytest.mark.asyncio
    async def test_generate_from_template(self):
        generator = TemplateBasedGenerator()
        
        params = {
            "component_name": "TestComponent",
            "props": "title: string",
            "prop_names": "title",
            "jsx_content": "<h1>{title}</h1>"
        }
        
        result = await generator.generate_from_template("react_component", params)
        
        assert "TestComponent" in result
        assert "title: string" in result
        assert "<h1>{title}</h1>" in result

    @pytest.mark.asyncio
    async def test_invalid_template(self):
        generator = TemplateBasedGenerator()
        
        with pytest.raises(ValueError):
            await generator.generate_from_template("invalid_template", {})

class TestQualityAssuranceEngine:
    @pytest.mark.asyncio
    async def test_review_code(self, mock_agent):
        with patch('generation_agent.Agent', return_value=mock_agent):
            mock_agent.arun.return_value = "Quality score: 85. Good code structure."
            
            qa_engine = QualityAssuranceEngine()
            result = await qa_engine.review_code("const x = 1;", "javascript")
            
            assert "quality_score" in result
            assert "feedback" in result
            assert isinstance(result["issues"], list)
            assert isinstance(result["suggestions"], list)

    def test_extract_score(self):
        qa_engine = QualityAssuranceEngine()
        
        response = "The code quality score is 85 out of 100."
        score = qa_engine._extract_score(response)
        assert score == 0.85

class TestOptimizationEngine:
    @pytest.mark.asyncio
    async def test_optimize_code(self, mock_agent):
        with patch('generation_agent.Agent', return_value=mock_agent):
            mock_agent.arun.return_value = """
            Optimized code:
            ```javascript
            const optimizedFunction = () => {
                // Optimized implementation
                return result;
            };
            ```
            """
            
            optimizer = OptimizationEngine()
            result = await optimizer.optimize_code(
                "function slow() { return 1; }", 
                ["performance"]
            )
            
            assert "optimizedFunction" in result

class TestGenerationAgent:
    @pytest.mark.asyncio
    async def test_generate_component_full_flow(self, generation_request):
        with patch('generation_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="""
            ```typescript
            const UserCard = () => <div>User Card</div>;
            ```
            Quality score: 90
            """)
            mock_agent_class.return_value = mock_agent
            
            agent = GenerationAgent()
            result = await agent.generate_component(generation_request)
            
            assert isinstance(result, GeneratedCode)
            assert result.source_code
            assert result.quality_score > 0

    @pytest.mark.asyncio
    async def test_batch_generate(self, generation_request):
        with patch('generation_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="```js\nconst x = 1;\n```")
            mock_agent_class.return_value = mock_agent
            
            agent = GenerationAgent()
            requests = [generation_request, generation_request]
            results = await agent.batch_generate(requests)
            
            assert len(results) == 2
            assert all(isinstance(r, GeneratedCode) for r in results)

    @pytest.mark.asyncio
    async def test_low_quality_optimization(self, generation_request):
        with patch('generation_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            
            # First call returns low quality code
            # Second call (QA) returns low score
            # Third call (optimizer) returns optimized code
            mock_agent.arun = AsyncMock(side_effect=[
                "```js\nconst bad = 1;\n```",  # Initial generation
                "Quality score: 60. Needs improvement.",  # QA review
                "```js\nconst optimized = 1;\n```"  # Optimization
            ])
            mock_agent_class.return_value = mock_agent
            
            agent = GenerationAgent()
            result = await agent.generate_component(generation_request)
            
            # Should have called optimizer due to low quality score
            assert mock_agent.arun.call_count == 3

if __name__ == "__main__":
    pytest.main([__file__])