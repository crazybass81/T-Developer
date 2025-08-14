"""
EcommerceGenerator Tests - Day 33
Tests for e-commerce domain agent generator
"""

import pytest

from src.generators.ecommerce_generator import EcommerceGenerator


class TestEcommerceGenerator:
    """Tests for EcommerceGenerator"""

    @pytest.fixture
    def generator(self):
        """Create EcommerceGenerator instance"""
        return EcommerceGenerator()

    def test_generator_initialization(self, generator):
        """Test EcommerceGenerator initialization"""
        assert generator is not None
        assert hasattr(generator, "templates")
        assert hasattr(generator, "business_rules")

    def test_generate_product_recommender(self, generator):
        """Test product recommendation agent generation"""
        config = {
            "agent_type": "product_recommender",
            "algorithms": ["collaborative", "content_based"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "ProductRecommender"
        assert "recommend_products" in agent["methods"]
        assert agent["size_kb"] <= 6.5

    def test_generate_inventory_manager(self, generator):
        """Test inventory management agent"""
        config = {
            "agent_type": "inventory_manager",
            "features": ["stock_tracking", "reorder_point"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "InventoryManager"
        assert "track_stock" in agent["methods"]
        assert "calculate_reorder" in agent["methods"]

    def test_generate_pricing_optimizer(self, generator):
        """Test dynamic pricing agent"""
        config = {
            "agent_type": "pricing_optimizer",
            "strategies": ["competitive", "demand_based"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "PricingOptimizer"
        assert "optimize_price" in agent["methods"]
        assert "analyze_competition" in agent["methods"]

    def test_generate_cart_analyzer(self, generator):
        """Test shopping cart analysis agent"""
        config = {
            "agent_type": "cart_analyzer",
            "features": ["abandonment_prediction", "upsell"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "CartAnalyzer"
        assert "predict_abandonment" in agent["methods"]
        assert "suggest_upsell" in agent["methods"]

    def test_generate_order_processor(self, generator):
        """Test order processing agent"""
        config = {
            "agent_type": "order_processor",
            "features": ["validation", "fulfillment"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "OrderProcessor"
        assert "process_order" in agent["methods"]
        assert "validate_payment" in agent["methods"]

    def test_generate_customer_service_bot(self, generator):
        """Test customer service agent"""
        config = {
            "agent_type": "customer_service",
            "capabilities": ["chat", "ticket_routing"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "CustomerServiceBot"
        assert "handle_inquiry" in agent["methods"]
        assert "route_ticket" in agent["methods"]

    def test_generate_review_analyzer(self, generator):
        """Test review analysis agent"""
        config = {
            "agent_type": "review_analyzer",
            "features": ["sentiment", "topic_extraction"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "ReviewAnalyzer"
        assert "analyze_sentiment" in agent["methods"]
        assert "extract_topics" in agent["methods"]

    def test_generate_search_optimizer(self, generator):
        """Test search optimization agent"""
        config = {
            "agent_type": "search_optimizer",
            "features": ["autocomplete", "relevance_ranking"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "SearchOptimizer"
        assert "optimize_results" in agent["methods"]
        assert "suggest_queries" in agent["methods"]

    def test_generate_fraud_detector(self, generator):
        """Test e-commerce fraud detection"""
        config = {
            "agent_type": "fraud_detector",
            "methods": ["transaction_analysis", "user_behavior"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "FraudDetector"
        assert "detect_fraud" in agent["methods"]
        assert agent["security"]["risk_scoring"] is True

    def test_generate_shipping_optimizer(self, generator):
        """Test shipping optimization agent"""
        config = {
            "agent_type": "shipping_optimizer",
            "features": ["route_optimization", "carrier_selection"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "ShippingOptimizer"
        assert "optimize_route" in agent["methods"]
        assert "select_carrier" in agent["methods"]

    def test_generate_loyalty_manager(self, generator):
        """Test loyalty program management"""
        config = {
            "agent_type": "loyalty_manager",
            "features": ["points_calculation", "tier_management"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "LoyaltyManager"
        assert "calculate_points" in agent["methods"]
        assert "update_tier" in agent["methods"]

    def test_generate_personalization_engine(self, generator):
        """Test personalization engine"""
        config = {
            "agent_type": "personalization",
            "features": ["content", "layout", "offers"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "PersonalizationEngine"
        assert "personalize_content" in agent["methods"]
        assert "customize_layout" in agent["methods"]

    def test_generate_marketplace_integrator(self, generator):
        """Test marketplace integration agent"""
        config = {
            "agent_type": "marketplace_integrator",
            "platforms": ["amazon", "ebay"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "MarketplaceIntegrator"
        assert "sync_inventory" in agent["methods"]
        assert "manage_listings" in agent["methods"]

    def test_generate_analytics_dashboard(self, generator):
        """Test analytics dashboard agent"""
        config = {
            "agent_type": "analytics_dashboard",
            "metrics": ["conversion", "revenue", "traffic"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "AnalyticsDashboard"
        assert "calculate_metrics" in agent["methods"]
        assert "generate_reports" in agent["methods"]

    def test_business_rules_validation(self, generator):
        """Test business rules validation"""
        rules = generator.validate_business_rules(
            {
                "min_order": 10,
                "max_discount": 50,
                "shipping_threshold": 50,
            }
        )

        assert rules["valid"] is True
        assert "min_order" in rules["applied"]

    def test_multi_channel_support(self, generator):
        """Test multi-channel commerce support"""
        config = {
            "agent_type": "channel_manager",
            "channels": ["web", "mobile", "social"],
        }

        agent = generator.generate(config)

        assert agent["name"] == "ChannelManager"
        assert "sync_channels" in agent["methods"]
        assert len(agent["channels"]) == 3
