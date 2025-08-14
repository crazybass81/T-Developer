"""Unified test for all domain generators"""
import pytest

from src.generators.ecommerce_generator import EcommerceGenerator
from src.generators.finance_generator import FinanceGenerator
from src.generators.healthcare_generator import HealthcareGenerator


class TestDomainGenerators:
    """Test all domain generators"""

    def test_finance_generator(self):
        """Test finance generator"""
        gen = FinanceGenerator()

        # Test risk analyzer
        agent = gen.generate({"agent_type": "risk_analyzer"})
        assert agent["name"] == "RiskAnalyzer"
        assert agent["size_kb"] <= 6.5
        assert "calculate_var" in agent["methods"]

        # Test trading bot
        agent = gen.generate({"agent_type": "trading_bot"})
        assert agent["name"] == "TradingBot"
        assert "execute_trade" in agent["methods"]

        # Test compliance
        issues = gen.validate_compliance("process_transaction without audit")
        assert len(issues) > 0

    def test_healthcare_generator(self):
        """Test healthcare generator"""
        gen = HealthcareGenerator()

        # Test patient monitor
        agent = gen.generate({"agent_type": "patient_monitor"})
        assert agent["name"] == "PatientMonitor"
        assert agent["compliance"]["HIPAA"] is True
        assert agent["size_kb"] <= 6.5

        # Test diagnosis assistant
        agent = gen.generate({"agent_type": "diagnosis_assistant"})
        assert agent["name"] == "DiagnosisAssistant"
        assert "analyze_symptoms" in agent["methods"]

        # Test HIPAA compliance
        issues = gen.validate_compliance("patient data without encrypt")
        assert len(issues) > 0

    def test_ecommerce_generator(self):
        """Test e-commerce generator"""
        gen = EcommerceGenerator()

        # Test product recommender
        agent = gen.generate({"agent_type": "product_recommender"})
        assert agent["name"] == "ProductRecommender"
        assert agent["size_kb"] <= 6.5
        assert "recommend_products" in agent["methods"]

        # Test fraud detector
        agent = gen.generate({"agent_type": "fraud_detector"})
        assert agent["name"] == "FraudDetector"
        assert agent["security"]["risk_scoring"] is True

        # Test business rules
        rules = gen.validate_business_rules({"min_order": 10, "max_discount": 50})
        assert rules["valid"] is True

    def test_all_generators_size_constraint(self):
        """Test that all generators meet size constraints"""
        generators = [
            (FinanceGenerator(), ["risk_analyzer", "trading_bot", "fraud_detector"]),
            (
                HealthcareGenerator(),
                ["patient_monitor", "diagnosis_assistant", "medication_manager"],
            ),
            (
                EcommerceGenerator(),
                ["product_recommender", "inventory_manager", "pricing_optimizer"],
            ),
        ]

        for gen, agent_types in generators:
            for agent_type in agent_types:
                agent = gen.generate({"agent_type": agent_type})
                assert agent["size_kb"] <= 6.5, f"{agent_type} exceeds 6.5KB limit"

    def test_all_generators_code_generation(self):
        """Test that all generators produce valid code"""
        generators = [
            (FinanceGenerator(), "risk_analyzer"),
            (HealthcareGenerator(), "patient_monitor"),
            (EcommerceGenerator(), "product_recommender"),
        ]

        for gen, agent_type in generators:
            agent = gen.generate({"agent_type": agent_type})
            assert "code" in agent
            assert "class" in agent["code"]
            assert agent["name"] in agent["code"]
            assert "def" in agent["code"]  # Has methods

    def test_domain_specific_compliance(self):
        """Test domain-specific compliance features"""
        # Finance: PCI_DSS for payment
        fin_gen = FinanceGenerator()
        agent = fin_gen.generate({"agent_type": "payment_processor"})
        assert agent["compliance"].get("PCI_DSS") or agent["security"].get("encryption")

        # Healthcare: HIPAA for all
        health_gen = HealthcareGenerator()
        agent = health_gen.generate({"agent_type": "patient_monitor"})
        assert agent["compliance"]["HIPAA"] is True

        # E-commerce: Risk scoring for fraud
        ecom_gen = EcommerceGenerator()
        agent = ecom_gen.generate({"agent_type": "fraud_detector"})
        assert agent["security"]["risk_scoring"] is True
