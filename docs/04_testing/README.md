# 🧪 Testing Documentation

## Overview
T-Developer AI Autonomous Evolution System의 포괄적인 테스트 문서입니다. 단위 테스트부터 Evolution 테스트까지 모든 테스트 전략을 다룹니다.

## 📁 Test Documentation

### Main Guide
- [**Complete Test Guide**](01_complete-test-guide.md) - 전체 테스트 가이드

## 🎯 Test Coverage

### Current Coverage
| Component | Coverage | Target | Status |
|-----------|----------|--------|---------|
| Agents | 92% | 80% | ✅ |
| Evolution | 88% | 85% | ✅ |
| API | 95% | 90% | ✅ |
| Core | 91% | 85% | ✅ |
| **Overall** | **87%** | **87%** | ✅ |

## 🔧 Test Types

### 1. Unit Tests (60%)
- Individual component testing
- Mocked dependencies
- Fast execution (< 5s)

### 2. Integration Tests (15%)
- API endpoint testing
- Database integration
- Service communication

### 3. Evolution Tests (20%)
- Fitness evaluation
- Constraint validation
- Safety verification

### 4. E2E Tests (5%)
- Complete workflow testing
- Production simulation
- Performance validation

## 📊 Test Pyramid
```
         /\
        /E2E\        5%
       /------\
      /Integr. \    15%
     /----------\
    / Evolution  \  20%
   /--------------\
  /   Unit Tests   \ 60%
 /------------------\
```

## 🚀 Quick Commands

### Run All Tests
```bash
pytest
```

### Run Specific Type
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/evolution/
```

### With Coverage
```bash
pytest --cov=src --cov-report=html
```

### Parallel Execution
```bash
pytest -n auto
```

## 🔗 Related Documents
- [Implementation Guides](../02_implementation/README.md)
- [API Documentation](../03_api/README.md)
- [Operations Manual](../05_operations/README.md)

## 📈 Test Metrics

### Execution Time
- Unit tests: < 5 seconds
- Integration tests: < 30 seconds
- Evolution tests: < 1 minute
- E2E tests: < 5 minutes
- **Total**: < 7 minutes

### Test Count
- Unit tests: 450+
- Integration tests: 120+
- Evolution tests: 80+
- E2E tests: 25+
- **Total**: 675+ tests

## 🎯 Key Test Scenarios

### Critical Tests
1. **Memory Constraint Test** - Agent stays under 6.5KB
2. **Speed Test** - Instantiation under 3μs
3. **Evolution Safety** - No malicious patterns
4. **Rollback Test** - Generation rollback works
5. **API Security** - Authentication/authorization

## 💡 Testing Best Practices
1. Write tests before code (TDD)
2. Keep tests isolated and independent
3. Use meaningful test names
4. Mock external dependencies
5. Test edge cases and error conditions

---
**Test Framework**: Pytest 7.x  
**Last Updated**: 2024-01-01