# Matching Rate Agent Documentation

## Overview

The Matching Rate Agent calculates precise matching scores between project requirements and available components. It uses multi-dimensional analysis including functional fit, technical compatibility, performance impact, and ecosystem compatibility to provide comprehensive matching assessments.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Matching Rate Agent                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Semantic    │  │Compatibility│  │Performance  │         │
│  │ Similarity  │  │ Analyzer    │  │ Predictor   │         │
│  │ Analyzer    │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                 Agno Framework                              │
│           AWS Bedrock (Nova Pro)                           │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Semantic Similarity Analyzer
- **Purpose**: Analyze semantic similarity between requirements and components
- **Features**:
  - TF-IDF vectorization
  - Cosine similarity calculation
  - Feature overlap analysis
  - Caching for performance

### 2. Compatibility Analyzer
- **Purpose**: Evaluate technical and platform compatibility
- **Features**:
  - Technology stack compatibility matrix
  - Version compatibility checking
  - License compatibility analysis
  - Platform support verification

### 3. Performance Predictor
- **Purpose**: Predict performance impact of components
- **Features**:
  - Bundle size estimation
  - Load time prediction
  - Memory usage analysis
  - Performance scoring

## Usage Examples

### Basic Matching Score Calculation

```python
from matching_rate_agent import MatchingRateAgent

# Initialize agent
agent = MatchingRateAgent()

# Define requirement
requirement = {
    'name': 'Frontend Framework',
    'description': 'Modern reactive frontend framework',
    'required_features': [
        'component-based architecture',
        'virtual DOM',
        'state management'
    ],
    'tech_stack': ['javascript', 'typescript'],
    'performance_requirements': {
        'max_bundle_size_kb': 200,
        'max_load_time_ms': 2000
    }
}

# Define component
component = {
    'name': 'React',
    'version': '18.2.0',
    'description': 'JavaScript library for building user interfaces',
    'features': ['component-based architecture', 'virtual DOM', 'hooks'],
    'supported_platforms': ['web', 'mobile'],
    'license': 'MIT'
}

# Calculate matching score
score = await agent.calculate_matching_score(requirement, component)

print(f"Overall Score: {score.overall_score:.2f}")
print(f"Functional: {score.functional_score:.2f}")
print(f"Technical: {score.technical_score:.2f}")
print(f"Performance: {score.performance_score:.2f}")
print(f"Compatibility: {score.compatibility_score:.2f}")
print(f"Confidence: {score.confidence:.2f}")
print(f"Explanation: {score.explanation}")
```

### Batch Component Matching

```python
# Multiple components
components = [
    {
        'name': 'React',
        'version': '18.2.0',
        'features': ['virtual DOM', 'components'],
        'license': 'MIT'
    },
    {
        'name': 'Vue',
        'version': '3.3.0',
        'features': ['reactive data', 'components'],
        'license': 'MIT'
    },
    {
        'name': 'Angular',
        'version': '16.0.0',
        'features': ['dependency injection', 'TypeScript'],
        'license': 'MIT'
    }
]

# Batch calculation
matches = await agent.batch_calculate_matching(requirement, components)

for match in matches:
    print(f"{match.component_name}: {match.matching_score.overall_score:.2f}")
    print(f"  Pros: {', '.join(match.pros)}")
    print(f"  Cons: {', '.join(match.cons)}")
    print(f"  Integration: {match.integration_effort}")
```

### Custom Scoring Weights

```python
# Performance-focused weights
performance_weights = {
    'functional': 0.2,
    'technical': 0.2,
    'performance': 0.5,
    'compatibility': 0.1
}

score = await agent.calculate_matching_score(
    requirement, component, performance_weights
)
```

### Semantic Similarity Analysis

```python
from matching_rate_agent import SemanticSimilarityAnalyzer

analyzer = SemanticSimilarityAnalyzer()

# Calculate similarity between texts
similarity = await analyzer.calculate_semantic_similarity(
    "React framework for building UIs",
    "Vue framework for creating interfaces"
)

# Analyze feature overlap
overlap = await analyzer.analyze_feature_overlap(
    ['virtual DOM', 'components', 'state management'],
    ['virtual DOM', 'reactive data', 'components']
)

print(f"Similarity: {similarity:.2f}")
print(f"Overlap Ratio: {overlap['overlap_ratio']:.2f}")
```

## Configuration

### Environment Variables

```bash
# AWS Bedrock Configuration
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0

# Agent Configuration
MATCHING_RATE_MEMORY_TABLE=t-dev-matching-memory
MATCHING_RATE_TEMPERATURE=0.2

# Performance Settings
SEMANTIC_CACHE_SIZE=1000
BATCH_PROCESSING_SIZE=50
```

### Scoring Weights Configuration

```python
# Default weights
default_weights = {
    'functional': 0.3,      # How well features match
    'technical': 0.25,      # Technology compatibility
    'performance': 0.25,    # Performance impact
    'compatibility': 0.2    # Ecosystem compatibility
}

# Enterprise-focused weights
enterprise_weights = {
    'functional': 0.25,
    'technical': 0.3,
    'performance': 0.2,
    'compatibility': 0.25
}

# Performance-critical weights
performance_weights = {
    'functional': 0.2,
    'technical': 0.2,
    'performance': 0.5,
    'compatibility': 0.1
}
```

## API Reference

### MatchingRateAgent Class

#### Methods

##### `calculate_matching_score(requirement, component, weights=None) -> MatchingScore`
Calculates comprehensive matching score between requirement and component.

**Parameters:**
- `requirement`: Dictionary containing requirement specifications
- `component`: Dictionary containing component information
- `weights`: Optional custom scoring weights

**Returns:**
```python
MatchingScore(
    overall_score=float,        # 0.0-1.0
    functional_score=float,     # 0.0-1.0
    technical_score=float,      # 0.0-1.0
    performance_score=float,    # 0.0-1.0
    compatibility_score=float,  # 0.0-1.0
    confidence=float,           # 0.0-1.0
    explanation=str
)
```

##### `batch_calculate_matching(requirement, components, weights=None) -> List[ComponentMatch]`
Calculates matching scores for multiple components in parallel.

**Returns:**
```python
List[ComponentMatch(
    component_id=str,
    component_name=str,
    matching_score=MatchingScore,
    pros=List[str],
    cons=List[str],
    integration_effort=str,
    risks=List[str]
)]
```

### SemanticSimilarityAnalyzer Class

#### Methods

##### `calculate_semantic_similarity(text1, text2) -> float`
Calculates semantic similarity between two texts using TF-IDF and cosine similarity.

##### `analyze_feature_overlap(required_features, component_features) -> Dict`
Analyzes overlap between required and available features.

**Returns:**
```python
{
    'overlap_ratio': float,      # Ratio of matched features
    'coverage_score': float,     # Overall coverage score
    'exact_matches': int,        # Number of exact matches
    'semantic_matches': int      # Number of semantic matches
}
```

### CompatibilityAnalyzer Class

#### Methods

##### `analyze_technical_compatibility(component, tech_stack) -> Dict[str, float]`
Analyzes compatibility between component and required technology stack.

##### `check_version_compatibility(component, required_versions) -> Dict[str, bool]`
Checks version compatibility for dependencies.

### PerformancePredictor Class

#### Methods

##### `predict_performance_impact(component, performance_requirements) -> Dict[str, float]`
Predicts performance impact of using the component.

**Returns:**
```python
{
    'performance_score': float,
    'bundle_size_score': float,
    'load_time_score': float,
    'memory_score': float
}
```

## Scoring Methodology

### 1. Functional Score (30%)
- **Feature Overlap**: Exact and semantic matching of required features
- **Semantic Similarity**: TF-IDF cosine similarity between descriptions
- **Use Case Alignment**: How well the component fits the intended use case

### 2. Technical Score (25%)
- **Technology Stack Compatibility**: Compatibility with required technologies
- **Version Compatibility**: Support for required dependency versions
- **Integration Complexity**: Ease of integration with existing systems

### 3. Performance Score (25%)
- **Bundle Size Impact**: Effect on application bundle size
- **Load Time Impact**: Effect on initial loading time
- **Memory Usage**: Runtime memory consumption
- **Scalability**: Performance under load

### 4. Compatibility Score (20%)
- **Platform Support**: Support for target platforms
- **License Compatibility**: License compatibility with project requirements
- **Ecosystem Integration**: How well it works with other tools

## Matching Confidence

The confidence score indicates how reliable the matching assessment is:

- **High Confidence (0.8-1.0)**: Consistent scores across all dimensions
- **Medium Confidence (0.6-0.8)**: Some variation in scores
- **Low Confidence (0.0-0.6)**: Significant variation or insufficient data

## Integration Effort Estimation

Based on the overall matching score:

- **Low Effort (0.8-1.0)**: Straightforward integration, minimal customization
- **Medium Effort (0.6-0.8)**: Some customization and adaptation needed
- **High Effort (0.4-0.6)**: Significant integration work required
- **Very High Effort (0.0-0.4)**: Major challenges, consider alternatives

## Performance Considerations

### Optimization Features

1. **Semantic Similarity Caching**: Results cached for repeated calculations
2. **Batch Processing**: Parallel processing of multiple components
3. **Lazy Loading**: Components loaded only when needed
4. **Memory Management**: Efficient memory usage for large datasets

### Performance Metrics

- **Single Matching**: < 500ms per component
- **Batch Processing**: 50+ components per minute
- **Memory Usage**: 6.5KB per agent instance
- **Cache Hit Rate**: 80%+ for repeated calculations

## Best Practices

### 1. Requirement Specification
- Provide detailed feature requirements
- Specify performance constraints clearly
- Include technology stack preferences
- Define platform and license requirements

### 2. Component Information
- Include comprehensive feature lists
- Provide accurate version information
- Specify supported platforms
- Include performance benchmarks when available

### 3. Weight Customization
- Adjust weights based on project priorities
- Consider team expertise and constraints
- Balance different aspects appropriately
- Document weight decisions

### 4. Result Interpretation
- Consider confidence scores in decisions
- Review explanations for context
- Evaluate risks and mitigation strategies
- Plan for integration effort

## Troubleshooting

### Common Issues

1. **Low Matching Scores**
   - Solution: Review requirement specifications
   - Check: Component feature completeness

2. **Inconsistent Results**
   - Solution: Verify input data quality
   - Check: Component information accuracy

3. **Performance Issues**
   - Solution: Enable caching and batch processing
   - Check: Network connectivity to AI models

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

agent = MatchingRateAgent()
# Enable verbose logging
score = await agent.calculate_matching_score(requirement, component)
```

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/component-matching.yml
name: Component Matching Analysis
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Component Matching Analysis
        run: |
          python -c "
          import asyncio
          from matching_rate_agent import MatchingRateAgent
          
          async def analyze():
              agent = MatchingRateAgent()
              matches = await agent.batch_calculate_matching(
                  requirement, proposed_components
              )
              
              for match in matches:
                  if match.matching_score.overall_score < 0.7:
                      print(f'⚠️ Low match: {match.component_name}')
                  else:
                      print(f'✅ Good match: {match.component_name}')
          
          asyncio.run(analyze())
          "
```

### Component Selection Automation

```python
# Automated component selection
async def select_best_components(requirements, available_components):
    agent = MatchingRateAgent()
    
    matches = await agent.batch_calculate_matching(
        requirements, available_components
    )
    
    # Filter by minimum score and confidence
    qualified_matches = [
        match for match in matches
        if match.matching_score.overall_score > 0.7
        and match.matching_score.confidence > 0.6
    ]
    
    return qualified_matches[:3]  # Top 3 matches
```

## Contributing

### Adding New Compatibility Rules

1. Update compatibility matrix in `CompatibilityAnalyzer`
2. Add new technology patterns
3. Include version compatibility rules
4. Add comprehensive tests

### Improving Semantic Analysis

1. Enhance feature extraction algorithms
2. Add domain-specific vocabularies
3. Improve similarity calculation methods
4. Validate against real-world data

## License

This Matching Rate Agent is part of the T-Developer project and follows the same licensing terms.