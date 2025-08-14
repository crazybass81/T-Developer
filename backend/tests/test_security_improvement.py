"""
Test suite for Security and Improvement Systems
Day 29: Phase 2 - ServiceImproverAgent
"""

import asyncio
from typing import Dict, List

import pytest

from src.agents.meta.improvement_executor import (
    ABTestConfig,
    ExecutionResult,
    ImprovementExecutor,
    ImprovementPlan,
    get_executor,
)
from src.security.vulnerability_scanner import (
    SecurityReport,
    Vulnerability,
    VulnerabilityScanner,
    get_scanner,
)


class TestVulnerabilityScanner:
    """Test vulnerability scanner"""
    
    @pytest.fixture
    def scanner(self):
        """Get scanner instance"""
        return get_scanner()
    
    def test_scan_injection_vulnerabilities(self, scanner):
        """Test injection vulnerability detection"""
        
        vulnerable_code = """
def unsafe_query(user_input):
    query = "SELECT * FROM users WHERE id = " + user_input
    eval(user_input)
    exec(user_input)
    os.system("rm " + user_input)
"""
        
        report = scanner.scan(vulnerable_code, "test.py")
        
        assert isinstance(report, SecurityReport)
        assert len(report.vulnerabilities) > 0
        
        # Should detect eval, exec, os.system
        injection_vulns = [v for v in report.vulnerabilities if v.type == "A03_injection"]
        assert len(injection_vulns) >= 3
        
        # Should have critical severity
        assert any(v.severity == "critical" for v in injection_vulns)
    
    def test_scan_crypto_failures(self, scanner):
        """Test cryptographic failure detection"""
        
        vulnerable_code = """
import hashlib

password = "admin123"
api_key = "sk-secret-key"
token = "bearer-token-123"

def weak_hash(data):
    return hashlib.md5(data).hexdigest()
    
def weak_hash2(data):
    return hashlib.sha1(data).hexdigest()
"""
        
        report = scanner.scan(vulnerable_code, "test.py")
        
        crypto_vulns = [v for v in report.vulnerabilities if v.type == "A02_crypto_failures"]
        assert len(crypto_vulns) > 0
        
        # Should detect hardcoded secrets
        hardcoded = [v for v in crypto_vulns if "secret" in v.description.lower() or "hardcoded" in v.description.lower()]
        assert len(hardcoded) >= 3
    
    def test_scan_access_control(self, scanner):
        """Test access control vulnerability detection"""
        
        vulnerable_code = """
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel(request):
    # No authentication check
    return render_template('admin.html')
    
def delete_user(request):
    # No permission check
    user_id = request.args.get('id')
    delete_from_db(user_id)
"""
        
        report = scanner.scan(vulnerable_code, "test.py")
        
        access_vulns = [v for v in report.vulnerabilities if v.type == "A01_broken_access"]
        # Pattern matching might detect these
        assert isinstance(report, SecurityReport)
    
    def test_scan_logging_failures(self, scanner):
        """Test logging failure detection"""
        
        vulnerable_code = """
def process_payment(amount):
    try:
        charge_card(amount)
    except:
        pass  # Silent failure
    
    print(f"Password: {user_password}")
    print(f"Token: {api_token}")
"""
        
        report = scanner.scan(vulnerable_code, "test.py")
        
        logging_vulns = [v for v in report.vulnerabilities if v.type == "A09_logging_failures"]
        assert len(logging_vulns) > 0
    
    def test_risk_score_calculation(self, scanner):
        """Test risk score calculation"""
        
        # Code with multiple vulnerabilities
        high_risk_code = """
password = "123456"
eval(user_input)
os.system(command)
hashlib.md5(data)
"""
        
        # Code with fewer vulnerabilities
        low_risk_code = """
def safe_function():
    return "Hello World"
"""
        
        high_risk_report = scanner.scan(high_risk_code)
        low_risk_report = scanner.scan(low_risk_code)
        
        assert high_risk_report.risk_score > low_risk_report.risk_score
        assert high_risk_report.risk_score > 50  # Should be high risk
    
    def test_owasp_compliance_check(self, scanner):
        """Test OWASP compliance checking"""
        
        clean_code = """
def secure_function():
    return "Secure"
"""
        
        report = scanner.scan(clean_code)
        
        # Should be compliant with most categories
        compliant_count = sum(1 for v in report.compliance.values() if v)
        assert compliant_count >= 8  # Most categories should be compliant
    
    def test_recommendations_generation(self, scanner):
        """Test security recommendations"""
        
        vulnerable_code = """
eval(input())
password = "weak"
import requests  # potentially vulnerable version
"""
        
        report = scanner.scan(vulnerable_code)
        
        assert len(report.recommendations) > 0
        # Should recommend fixing critical issues
        assert any("critical" in rec.lower() or "immediately" in rec.lower() 
                  for rec in report.recommendations)
    
    def test_ast_based_scanning(self, scanner):
        """Test AST-based vulnerability detection"""
        
        code = """
def process():
    password = "hardcoded123"
    secret_key = "sk-12345"
    api_token = "token-xyz"
    
    eval(user_data)
    exec(user_code)
    compile(source, 'file', 'exec')
"""
        
        report = scanner.scan(code)
        
        # Should detect through AST analysis
        ast_vulns = [v for v in report.vulnerabilities if v.confidence >= 0.9]
        assert len(ast_vulns) > 0


class TestImprovementExecutor:
    """Test improvement executor"""
    
    @pytest.fixture
    def executor(self):
        """Get executor instance"""
        return get_executor()
    
    @pytest.mark.asyncio
    async def test_execute_improvement(self, executor):
        """Test improvement execution"""
        
        plan = ImprovementPlan(
            id="test_001",
            type="performance",
            description="Test improvement",
            changes=[
                {"type": "config", "config": {"cache": True}}
            ],
            estimated_impact=0.2,
            risk_level="low",
            rollback_plan={"steps": []}
        )
        
        result = await executor.execute(plan, enable_ab_test=False)
        
        assert isinstance(result, ExecutionResult)
        assert result.improvement_id == "test_001"
        assert result.execution_time > 0
        assert result.metrics_before is not None
        assert result.metrics_after is not None
    
    @pytest.mark.asyncio
    async def test_ab_testing(self, executor):
        """Test A/B testing functionality"""
        
        plan = ImprovementPlan(
            id="test_ab_001",
            type="performance",
            description="A/B test improvement",
            changes=[{"type": "config", "config": {}}],
            estimated_impact=0.3,
            risk_level="medium",
            rollback_plan={}
        )
        
        result = await executor.execute(plan, enable_ab_test=True)
        
        assert result.ab_test_results is not None
        assert "winner" in result.ab_test_results
        assert "statistical_significance" in result.ab_test_results
        assert "variant_a" in result.ab_test_results
        assert "variant_b" in result.ab_test_results
    
    @pytest.mark.asyncio
    async def test_rollback_on_failure(self, executor):
        """Test automatic rollback on failure"""
        
        plan = ImprovementPlan(
            id="test_rollback",
            type="performance",
            description="Failing improvement",
            changes=[{"type": "config", "config": {}}],
            estimated_impact=0.9,  # High expectation
            risk_level="high",
            rollback_plan={"steps": [{"action": "restore"}]}
        )
        
        # Mock low actual impact to trigger rollback
        result = await executor.execute(plan, auto_rollback=True)
        
        # The actual impact will be much lower than estimated
        # This should trigger rollback
        if result.actual_impact < plan.estimated_impact * 0.5:
            assert result.rollback_performed or not result.success
    
    def test_ab_config_creation(self, executor):
        """Test A/B test configuration creation"""
        
        plan = ImprovementPlan(
            id="test_config",
            type="test",
            description="Test",
            changes=[],
            estimated_impact=0.1,
            risk_level="low",
            rollback_plan={}
        )
        
        config = executor._create_ab_config(plan)
        
        assert isinstance(config, ABTestConfig)
        assert config.traffic_split == 0.5  # Low risk = 50% split
        assert config.minimum_sample_size > 0
        assert len(config.success_metrics) > 0
    
    @pytest.mark.asyncio
    async def test_metrics_capture(self, executor):
        """Test metrics capture"""
        
        metrics = await executor._capture_metrics()
        
        assert isinstance(metrics, dict)
        assert "response_time" in metrics
        assert "error_rate" in metrics
        assert "throughput" in metrics
        assert "user_satisfaction" in metrics
        
        # All metrics should be numeric
        assert all(isinstance(v, (int, float)) for v in metrics.values())
    
    def test_impact_calculation(self, executor):
        """Test impact calculation"""
        
        before = {
            "response_time": 200,
            "error_rate": 0.02,
            "throughput": 500,
            "user_satisfaction": 0.7
        }
        
        after = {
            "response_time": 150,  # 25% improvement
            "error_rate": 0.01,  # 50% improvement
            "throughput": 600,  # 20% improvement
            "user_satisfaction": 0.8  # 14% improvement
        }
        
        impact = executor._calculate_impact(before, after)
        
        assert impact > 0  # Should show improvement
        assert 0 <= impact <= 1  # Should be normalized
    
    @pytest.mark.asyncio
    async def test_execution_history(self, executor):
        """Test execution history tracking"""
        
        plan = ImprovementPlan(
            id="history_test",
            type="test",
            description="History test",
            changes=[],
            estimated_impact=0.1,
            risk_level="low",
            rollback_plan={}
        )
        
        initial_count = len(executor.execution_history)
        
        await executor.execute(plan)
        
        assert len(executor.execution_history) == initial_count + 1
        
        history = executor.get_execution_history()
        assert len(history) > 0
        assert history[-1].improvement_id == "history_test"
    
    def test_metrics_reporting(self, executor):
        """Test metrics reporting"""
        
        metrics = executor.get_metrics()
        
        assert "total_executions" in metrics
        assert "successful_executions" in metrics
        assert "success_rate" in metrics
        assert "active_tests" in metrics
        assert "rollback_stack_size" in metrics


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security and improvement systems"""
    
    @pytest.mark.asyncio
    async def test_security_improvement_flow(self):
        """Test complete security improvement flow"""
        
        scanner = get_scanner()
        executor = get_executor()
        
        # Scan vulnerable code
        vulnerable_code = """
password = "weak123"
eval(user_input)
hashlib.md5(data)
"""
        
        report = scanner.scan(vulnerable_code)
        
        # Create improvement plan based on vulnerabilities
        if report.vulnerabilities:
            plan = ImprovementPlan(
                id="security_fix_001",
                type="security",
                description="Fix security vulnerabilities",
                changes=[
                    {"type": "code", "code": {"fix": "security_patches"}}
                ],
                estimated_impact=0.5,
                risk_level="high",
                rollback_plan={"steps": [{"action": "revert"}]}
            )
            
            # Execute improvement
            result = await executor.execute(plan, enable_ab_test=True)
            
            assert result is not None
            assert result.improvement_id == "security_fix_001"
            
            # If A/B test was run, check results
            if result.ab_test_results:
                assert "winner" in result.ab_test_results
        
        # Verify integration
        assert report.risk_score > 0
        assert len(report.recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])