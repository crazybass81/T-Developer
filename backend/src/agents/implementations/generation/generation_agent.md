# Generation Agent Documentation

## Overview
The Generation Agent is responsible for AI-powered code generation, creating high-quality, production-ready components based on requirements and specifications.

## Architecture

### Core Components

1. **CodeGenerationEngine**: AI-based code generation using Agno + AWS Bedrock
2. **TemplateBasedGenerator**: Template-driven code generation for common patterns
3. **QualityAssuranceEngine**: Automated code review and quality assessment
4. **OptimizationEngine**: Performance and code optimization

## Usage

### Basic Component Generation

```python
from generation_agent import GenerationAgent, GenerationRequest

# Initialize agent
agent = GenerationAgent()

# Create generation request
request = GenerationRequest(
    component_type="react_component",
    requirements={
        "name": "UserProfile",
        "props": ["user", "onEdit", "onDelete"],
        "functionality": "Display user profile with edit/delete actions"
    },
    framework="react",
    language="typescript"
)

# Generate component
result = await agent.generate_component(request)

print(f"Generated code:\n{result.source_code}")
print(f"Test code:\n{result.test_code}")
print(f"Quality score: {result.quality_score}")
```

### Batch Generation

```python
# Generate multiple components
requests = [
    GenerationRequest(
        component_type="api_endpoint",
        requirements={"method": "GET", "path": "/users"},
        framework="fastapi",
        language="python"
    ),
    GenerationRequest(
        component_type="database_model",
        requirements={"table": "users", "fields": ["id", "name", "email"]},
        framework="sqlalchemy",
        language="python"
    )
]

results = await agent.batch_generate(requests)
```

### Template-Based Generation

```python
from generation_agent import TemplateBasedGenerator

generator = TemplateBasedGenerator()

# Generate React component from template
params = {
    "component_name": "Button",
    "props": "text: string; onClick: () => void",
    "prop_names": "text, onClick",
    "jsx_content": "<button onClick={onClick}>{text}</button>"
}

code = await generator.generate_from_template("react_component", params)
```

## Configuration

### Environment Variables

```bash
# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Agno Configuration (Optional - Open Source)
AGNO_MONITORING_URL=https://agno.com
```

### Agent Configuration

```python
# Custom model configuration
agent = GenerationAgent()
agent.code_engine.agent.model = AwsBedrock(
    id="anthropic.claude-3-opus-v1:0",  # Use more powerful model
    temperature=0.2  # Lower temperature for more consistent code
)
```

## Supported Frameworks and Languages

### Web Frameworks
- **React** (JavaScript/TypeScript)
- **Vue.js** (JavaScript/TypeScript)
- **Angular** (TypeScript)
- **Svelte** (JavaScript/TypeScript)

### Backend Frameworks
- **FastAPI** (Python)
- **Express.js** (JavaScript/TypeScript)
- **Django** (Python)
- **Spring Boot** (Java)

### Mobile Frameworks
- **React Native** (JavaScript/TypeScript)
- **Flutter** (Dart)

## Quality Assurance

The Generation Agent includes automated quality assurance:

### Quality Metrics
- **Code Quality Score**: 0-100 based on best practices
- **Security Analysis**: Vulnerability detection
- **Performance Assessment**: Efficiency evaluation
- **Maintainability**: Code structure and readability

### Quality Thresholds
- **Minimum Quality Score**: 80/100
- **Auto-optimization**: Triggered for scores < 80
- **Manual Review**: Required for scores < 60

## Code Templates

### Available Templates

1. **react_component**: React functional component
2. **python_class**: Python class with methods
3. **api_endpoint**: REST API endpoint
4. **database_model**: Database model/schema
5. **test_suite**: Unit test template

### Custom Templates

```python
# Add custom template
generator = TemplateBasedGenerator()
generator.templates["custom_template"] = """
// Custom template content
{custom_placeholder}
"""
```

## Performance Optimization

### Optimization Goals
- **Performance**: Execution speed and efficiency
- **Memory**: Memory usage optimization
- **Readability**: Code clarity and maintainability
- **Scalability**: Ability to handle growth

### Example Optimization

```python
# Request optimization
optimized_code = await agent.optimizer.optimize_code(
    original_code,
    optimization_goals=["performance", "memory"]
)
```

## Error Handling

### Common Errors

1. **Generation Timeout**: Large components may timeout
2. **Invalid Requirements**: Malformed requirement specifications
3. **Template Not Found**: Requested template doesn't exist
4. **Quality Threshold**: Generated code below minimum quality

### Error Recovery

```python
try:
    result = await agent.generate_component(request)
except GenerationTimeoutError:
    # Retry with simpler requirements
    simplified_request = simplify_requirements(request)
    result = await agent.generate_component(simplified_request)
except QualityThresholdError as e:
    # Manual review required
    print(f"Quality too low: {e.quality_score}")
    # Implement manual review process
```

## Integration Examples

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Generate Components
  run: |
    python -c "
    import asyncio
    from generation_agent import GenerationAgent, GenerationRequest
    
    async def generate():
        agent = GenerationAgent()
        request = GenerationRequest(...)
        result = await agent.generate_component(request)
        
        with open('generated_component.tsx', 'w') as f:
            f.write(result.source_code)
    
    asyncio.run(generate())
    "
```

### API Integration

```python
from fastapi import FastAPI
from generation_agent import GenerationAgent

app = FastAPI()
agent = GenerationAgent()

@app.post("/generate")
async def generate_code(request: GenerationRequest):
    result = await agent.generate_component(request)
    return {
        "source_code": result.source_code,
        "test_code": result.test_code,
        "quality_score": result.quality_score
    }
```

## Best Practices

### 1. Clear Requirements
- Provide detailed, specific requirements
- Include examples and use cases
- Specify constraints and preferences

### 2. Quality First
- Always review generated code
- Run tests before deployment
- Monitor quality scores

### 3. Template Usage
- Use templates for common patterns
- Customize templates for your needs
- Maintain template library

### 4. Optimization
- Profile generated code
- Optimize for your specific use case
- Monitor performance metrics

## Troubleshooting

### Low Quality Scores
- Review requirement specifications
- Check for conflicting requirements
- Consider manual code review

### Generation Failures
- Simplify complex requirements
- Break down into smaller components
- Check framework compatibility

### Performance Issues
- Enable optimization engine
- Use appropriate model size
- Consider template-based generation for simple cases