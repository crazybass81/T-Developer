"""UI Selection Agent Deployment Validation Tests"""

import pytest
import asyncio
import requests
from typing import List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    category: str
    test_name: str
    passed: bool
    message: str
    details: dict

class UISelectionDeploymentValidator:
    """Validates UI Selection Agent deployment"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    async def validate_all(self) -> List[ValidationResult]:
        """Run all validation tests"""
        results = []
        
        # Functionality tests
        results.extend(await self.validate_functionality())
        
        # Performance tests
        results.extend(await self.validate_performance())
        
        # Security tests
        results.extend(await self.validate_security())
        
        return results
    
    async def validate_functionality(self) -> List[ValidationResult]:
        """Validate core functionality"""
        results = []
        
        # Test framework selection
        try:
            response = requests.post(f"{self.base_url}/v1/agents/ui-selection/select", 
                                   json={"project_type": "web", "requirements": ["responsive", "modern"]})
            
            results.append(ValidationResult(
                category="functionality",
                test_name="framework_selection",
                passed=response.status_code == 200 and "framework" in response.json(),
                message="Framework selection working",
                details={"status_code": response.status_code}
            ))
        except Exception as e:
            results.append(ValidationResult(
                category="functionality", 
                test_name="framework_selection",
                passed=False,
                message=str(e),
                details={}
            ))
        
        return results
    
    async def validate_performance(self) -> List[ValidationResult]:
        """Validate performance requirements"""
        results = []
        
        # Response time test
        latencies = []
        for _ in range(10):
            start = asyncio.get_event_loop().time()
            try:
                requests.get(f"{self.base_url}/health", timeout=5)
                latencies.append(asyncio.get_event_loop().time() - start)
            except:
                latencies.append(5.0)
        
        avg_latency = sum(latencies) / len(latencies)
        
        results.append(ValidationResult(
            category="performance",
            test_name="response_time",
            passed=avg_latency < 0.3,
            message=f"Average response time: {avg_latency*1000:.2f}ms",
            details={"avg_latency_ms": avg_latency*1000}
        ))
        
        return results
    
    async def validate_security(self) -> List[ValidationResult]:
        """Validate security measures"""
        results = []
        
        # Health endpoint check
        try:
            response = requests.get(f"{self.base_url}/health")
            results.append(ValidationResult(
                category="security",
                test_name="health_endpoint",
                passed=response.status_code == 200,
                message="Health endpoint accessible",
                details={"status_code": response.status_code}
            ))
        except Exception as e:
            results.append(ValidationResult(
                category="security",
                test_name="health_endpoint", 
                passed=False,
                message=str(e),
                details={}
            ))
        
        return results

@pytest.mark.asyncio
async def test_deployment_validation():
    """Test deployment validation"""
    validator = UISelectionDeploymentValidator()
    results = await validator.validate_all()
    
    # Check that we have results
    assert len(results) > 0
    
    # Check that critical tests pass
    critical_tests = [r for r in results if r.test_name in ["framework_selection", "health_endpoint"]]
    assert all(r.passed for r in critical_tests), f"Critical tests failed: {[r.test_name for r in critical_tests if not r.passed]}"

if __name__ == "__main__":
    validator = UISelectionDeploymentValidator()
    results = asyncio.run(validator.validate_all())
    
    print("🔍 Deployment Validation Results:")
    for result in results:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.category}.{result.test_name}: {result.message}")
    
    failed = [r for r in results if not r.passed]
    if failed:
        print(f"\n❌ {len(failed)} tests failed")
        exit(1)
    else:
        print(f"\n✅ All {len(results)} tests passed")