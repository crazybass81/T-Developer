"""Integration Test for Day 33-35 Completion"""
import os
import sqlite3

import pytest


def test_day33_domain_generators():
    """Test Day 33: Domain generators"""
    from src.generators.ecommerce_generator import EcommerceGenerator
    from src.generators.finance_generator import FinanceGenerator
    from src.generators.healthcare_generator import HealthcareGenerator

    # Test all generators
    generators = [
        (FinanceGenerator(), "risk"),
        (HealthcareGenerator(), "patient"),
        (EcommerceGenerator(), "product"),
    ]

    for gen, agent_type in generators:
        agent = gen.generate({"agent_type": agent_type})
        assert agent["name"] is not None
        assert agent["size_kb"] <= 6.5  # Size constraint
        assert len(agent["methods"]) > 0
        assert agent["code"] is not None

    # Test domain knowledge database
    assert os.path.exists("/home/ec2-user/T-DeveloperMVP/knowledge/domain_knowledge.db")

    conn = sqlite3.connect("/home/ec2-user/T-DeveloperMVP/knowledge/domain_knowledge.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM domains")
    assert cursor.fetchone()[0] == 3  # 3 domains

    cursor.execute("SELECT COUNT(*) FROM patterns")
    assert cursor.fetchone()[0] == 9  # 9 patterns

    conn.close()


def test_day34_test_generation():
    """Test Day 34: Test generation"""
    from src.testing.coverage_analyzer import CoverageAnalyzer
    from src.testing.performance_test_builder import PerformanceTestBuilder
    from src.testing.test_generator import TestGenerator

    # Test generator
    tg = TestGenerator()
    code = """
class Calculator:
    def add(self, a, b):
        return a + b
    def subtract(self, a, b):
        return a - b
"""

    unit_tests = tg.generate_unit_tests(code)
    assert "test_Calculator_add" in unit_tests
    assert "test_Calculator_subtract" in unit_tests

    # Coverage analyzer
    ca = CoverageAnalyzer()
    analysis = ca.analyze_code(code, unit_tests)
    assert analysis["functions"] == 2
    assert analysis["lines"] > 0

    # Performance test builder
    ptb = PerformanceTestBuilder()
    perf_test = ptb.build_latency_test("process", 200)
    assert "test_process_latency" in perf_test
    assert "200ms" in perf_test

    # Test templates exist
    assert os.path.exists(
        "/home/ec2-user/T-DeveloperMVP/templates/test_templates/unit_test_template.py"
    )
    assert os.path.exists(
        "/home/ec2-user/T-DeveloperMVP/templates/test_templates/integration_test_template.py"
    )
    assert os.path.exists(
        "/home/ec2-user/T-DeveloperMVP/templates/test_templates/performance_test_template.py"
    )


def test_day35_documentation():
    """Test Day 35: Documentation automation"""
    from src.documentation.api_doc_builder import APIDocBuilder
    from src.documentation.changelog_generator import ChangelogGenerator
    from src.documentation.doc_generator import DocGenerator

    # Doc generator
    dg = DocGenerator()
    code = '''
"""Module docstring"""
class MyClass:
    """Class docstring"""
    def method(self):
        """Method docstring"""
        pass
'''

    docs = dg.generate_from_code(code, "Test Module")
    assert "Test Module" in docs
    assert "Module docstring" in docs
    assert "MyClass" in docs
    assert "method" in docs

    # API doc builder
    adb = APIDocBuilder()
    config = {
        "title": "Test API",
        "version": "1.0.0",
        "endpoints": [{"path": "/test", "method": "GET", "description": "Test endpoint"}],
    }

    openapi = adb.build_openapi(config)
    assert openapi["info"]["title"] == "Test API"
    assert "/test" in openapi["paths"]

    markdown = adb.build_markdown(config)
    assert "# Test API" in markdown
    assert "GET /test" in markdown

    # Changelog generator
    cg = ChangelogGenerator()
    commits = [{"message": "feat: Add new feature", "tag": "1.0.0"}, {"message": "fix: Fix bug"}]

    changelog = cg.generate_from_commits(commits)
    assert "# Changelog" in changelog
    assert "1.0.0" in changelog
    assert "Added" in changelog
    assert "Fixed" in changelog


def test_file_size_constraints():
    """Test that all files meet size constraints"""
    import os

    files_to_check = [
        "/home/ec2-user/T-DeveloperMVP/backend/src/generators/finance_generator.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/generators/healthcare_generator.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/generators/ecommerce_generator.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/testing/test_generator.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/testing/coverage_analyzer.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/testing/performance_test_builder.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/documentation/doc_generator.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/documentation/api_doc_builder.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/documentation/changelog_generator.py",
    ]

    for file_path in files_to_check:
        size = os.path.getsize(file_path)
        assert size <= 6656, f"{file_path} exceeds 6.5KB limit: {size} bytes"
        print(f"✅ {os.path.basename(file_path)}: {size} bytes ({size/1024:.1f}KB)")


if __name__ == "__main__":
    print("🚀 Running Day 33-35 Integration Tests...")

    test_day33_domain_generators()
    print("✅ Day 33: Domain generators - PASSED")

    test_day34_test_generation()
    print("✅ Day 34: Test generation - PASSED")

    test_day35_documentation()
    print("✅ Day 35: Documentation automation - PASSED")

    test_file_size_constraints()
    print("✅ All files meet 6.5KB constraint - PASSED")

    print("\n🎉 Day 33-35 Successfully Completed!")
