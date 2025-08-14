"""
FinanceGenerator Tests - Day 33
Tests for finance domain agent generator
"""

import pytest

from src.generators.finance_generator import FinanceGenerator


class TestFinanceGenerator:
    """Tests for FinanceGenerator"""

    @pytest.fixture
    def generator(self):
        """Create FinanceGenerator instance"""
        return FinanceGenerator()

    @pytest.fixture
    def finance_requirements(self):
        """Sample finance domain requirements"""
        return {
            "type": "risk_analyzer",
            "features": ["portfolio_analysis", "risk_calculation", "compliance_check"],
            "regulations": ["SOX", "GDPR"],
            "data_sources": ["market_data", "transactions"],
        }

    def test_generator_initialization(self, generator):
        """Test FinanceGenerator initialization"""
        assert generator is not None
        assert hasattr(generator, "templates")
        assert hasattr(generator, "compliance_rules")

    def test_generate_risk_analyzer(self, generator):
        """Test risk analyzer agent generation"""
        config = {
            "agent_type": "risk_analyzer",
            "risk_models": ["VaR", "CVaR", "Monte Carlo"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "RiskAnalyzer"
        assert "calculate_var" in agent["methods"]
        assert agent["size_kb"] <= 6.5

    def test_generate_trading_bot(self, generator):
        """Test trading bot agent generation"""
        config = {
            "agent_type": "trading_bot",
            "strategies": ["mean_reversion", "momentum"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "TradingBot"
        assert "execute_trade" in agent["methods"]
        assert "backtest" in agent["methods"]

    def test_compliance_validation(self, generator):
        """Test compliance validation"""
        agent_code = """
        def process_transaction(self, data):
            # Process without logging
            return data
        """

        issues = generator.validate_compliance(agent_code)
        assert len(issues) > 0
        assert any("audit" in issue.lower() for issue in issues)

    def test_generate_fraud_detector(self, generator):
        """Test fraud detection agent generation"""
        config = {
            "agent_type": "fraud_detector",
            "algorithms": ["anomaly_detection", "pattern_matching"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "FraudDetector"
        assert "detect_anomaly" in agent["methods"]
        assert agent["compliance"]["PCI_DSS"] is True

    def test_portfolio_optimizer_generation(self, generator):
        """Test portfolio optimizer generation"""
        config = {
            "agent_type": "portfolio_optimizer",
            "optimization": "markowitz",
            "constraints": ["max_risk", "min_return"],
        }

        agent = generator.generate(config)

        assert "optimize_portfolio" in agent["methods"]
        assert "calculate_sharpe_ratio" in agent["methods"]

    def test_credit_scorer_generation(self, generator):
        """Test credit scoring agent generation"""
        config = {
            "agent_type": "credit_scorer",
            "model": "logistic_regression",
            "features": ["income", "debt_ratio", "payment_history"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "CreditScorer"
        assert "calculate_score" in agent["methods"]
        assert "explain_score" in agent["methods"]

    def test_regulatory_reporter(self, generator):
        """Test regulatory reporting agent"""
        config = {
            "agent_type": "regulatory_reporter",
            "reports": ["MiFID_II", "Basel_III"],
        }

        agent = generator.generate(config)

        assert "generate_report" in agent["methods"]
        assert agent["compliance"]["regulatory"] is True

    def test_market_analyzer(self, generator):
        """Test market analysis agent"""
        config = {
            "agent_type": "market_analyzer",
            "indicators": ["RSI", "MACD", "Bollinger"],
        }

        agent = generator.generate(config)

        assert "analyze_trend" in agent["methods"]
        assert "calculate_indicators" in agent["methods"]

    def test_payment_processor(self, generator):
        """Test payment processing agent"""
        config = {
            "agent_type": "payment_processor",
            "methods": ["card", "ACH", "wire"],
            "security": "PCI_DSS",
        }

        agent = generator.generate(config)

        assert "process_payment" in agent["methods"]
        assert "validate_transaction" in agent["methods"]
        assert agent["security"]["encryption"] is True

    def test_domain_knowledge_integration(self, generator):
        """Test domain knowledge integration"""
        knowledge = generator.get_domain_knowledge("derivatives")

        assert "options" in knowledge
        assert "futures" in knowledge
        assert "swaps" in knowledge

    def test_template_customization(self, generator):
        """Test template customization"""
        template = generator.get_template("risk_analyzer")
        customized = generator.customize_template(
            template, {"additional_metrics": ["Sortino", "Calmar"]}
        )

        assert "Sortino" in customized["code"]
        assert "Calmar" in customized["code"]

    def test_multi_agent_generation(self, generator):
        """Test generation of multiple coordinated agents"""
        config = {
            "system": "trading_platform",
            "agents": ["analyzer", "executor", "risk_manager"],
        }

        agents = generator.generate_system(config)

        assert len(agents) == 3
        assert all(a["size_kb"] <= 6.5 for a in agents)

    def test_code_optimization(self, generator):
        """Test code optimization for size constraints"""
        large_agent = {"code": "x" * 10000, "name": "LargeAgent"}
        optimized = generator.optimize_size(large_agent)

        assert len(optimized["code"]) < len(large_agent["code"])
        assert optimized["size_kb"] <= 6.5

    def test_security_features(self, generator):
        """Test security feature generation"""
        config = {
            "agent_type": "secure_wallet",
            "security_level": "high",
        }

        agent = generator.generate(config)

        assert "encrypt_data" in agent["methods"]
        assert "validate_signature" in agent["methods"]
        assert agent["security"]["multi_factor_auth"] is True

    def test_real_time_processing(self, generator):
        """Test real-time processing capabilities"""
        config = {
            "agent_type": "market_maker",
            "latency_requirement": "microseconds",
        }

        agent = generator.generate(config)

        assert agent["performance"]["optimized"] is True
        assert "stream_processor" in agent["methods"]

    def test_audit_trail_generation(self, generator):
        """Test audit trail implementation"""
        config = {
            "agent_type": "transaction_processor",
            "audit": True,
        }

        agent = generator.generate(config)

        assert "log_transaction" in agent["methods"]
        assert "generate_audit_report" in agent["methods"]
