"""
🧬 T-Developer AI Analyzers Tests
TDD tests for AI analysis components
"""
import ast
import tempfile
from pathlib import Path

import pytest

from src.ai.analyzers.capability_extractor import (
    CapabilityExtractor,
    CapabilityProfile,
    extract_quick,
)
from src.ai.analyzers.code_analyzer import AnalysisResult, CodeAnalyzer, CodeMetrics, quick_analyze
from src.ai.prompts.analysis_prompts import AnalysisPrompts, analyze_code, get_prompt


class TestCodeAnalyzer:
    """Test CodeAnalyzer functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = CodeAnalyzer()
        self.sample_code = '''
import pandas as pd
import requests

async def process_data(file_path):
    """Process CSV data"""
    df = pd.read_csv(file_path)
    return df.groupby('category').sum()

class DataProcessor:
    def __init__(self):
        self.data = None

    def analyze(self):
        if self.data:
            return len(self.data)
        return 0
'''

    def test_analyzer_initialization(self):
        """Test analyzer creates properly"""
        analyzer = CodeAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, "capability_patterns")
        assert len(analyzer.capability_patterns) > 0

    def test_code_analysis_basic(self):
        """Test basic code analysis"""
        result = self.analyzer.analyze_code(self.sample_code)

        assert isinstance(result, AnalysisResult)
        assert len(result.capabilities) > 0
        assert result.metrics.lines > 0
        assert result.metrics.functions > 0
        assert result.metrics.classes > 0
        assert result.quality_score > 0

    def test_capability_detection(self):
        """Test capability detection"""
        result = self.analyzer.analyze_code(self.sample_code)

        # Should detect data processing and async capabilities
        capabilities = result.capabilities
        assert "data_processing" in capabilities
        assert "async" in capabilities

    def test_metrics_calculation(self):
        """Test metrics calculation"""
        result = self.analyzer.analyze_code(self.sample_code)
        metrics = result.metrics

        assert metrics.lines > 10
        assert metrics.functions == 1  # process_data
        assert metrics.classes == 1  # DataProcessor
        assert metrics.imports > 0
        assert metrics.memory_score >= 0

    def test_memory_efficiency_check(self):
        """Test 6.5KB memory constraint check"""
        short_code = "def hello(): return 'world'"
        long_code = "x = 1\n" * 200  # Large code

        short_result = self.analyzer.analyze_code(short_code)
        long_result = self.analyzer.analyze_code(long_code)

        assert short_result.memory_efficient == True
        assert long_result.memory_efficient == False

    def test_suggestion_generation(self):
        """Test suggestion generation"""
        complex_code = """
from module import *
def complex_function():
    for i in range(100):
        for j in range(100):
            for k in range(100):
                if i > j:
                    if j > k:
                        print(i, j, k)
"""
        result = self.analyzer.analyze_code(complex_code)
        suggestions = result.suggestions

        assert len(suggestions) > 0
        assert any("wildcard" in s.lower() for s in suggestions)
        assert any("complex" in s.lower() for s in suggestions)

    def test_file_analysis(self):
        """Test file analysis"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(self.sample_code)
            f.flush()

            result = self.analyzer.analyze_file(Path(f.name))
            assert isinstance(result, AnalysisResult)
            assert len(result.capabilities) > 0

    def test_error_handling(self):
        """Test error handling for invalid code"""
        invalid_code = "def invalid( syntax error"
        result = self.analyzer.analyze_code(invalid_code)

        assert isinstance(result, AnalysisResult)
        assert len(result.suggestions) > 0
        assert "error" in result.suggestions[0].lower()

    def test_quick_analyze_function(self):
        """Test quick analyze utility function"""
        result = quick_analyze(self.sample_code)

        assert isinstance(result, dict)
        assert "capabilities" in result
        assert "quality_score" in result
        assert "memory_efficient" in result
        assert "lines" in result


class TestCapabilityExtractor:
    """Test CapabilityExtractor functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.extractor = CapabilityExtractor()
        self.api_code = """
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()
"""

    def test_extractor_initialization(self):
        """Test extractor initialization"""
        extractor = CapabilityExtractor()
        assert extractor is not None
        assert hasattr(extractor, "patterns")
        assert len(extractor.patterns) > 0

    def test_capability_profile_creation(self):
        """Test capability profile creation"""
        profile = self.extractor.extract_capabilities(self.api_code)

        assert isinstance(profile, CapabilityProfile)
        assert len(profile.capabilities) > 0
        assert len(profile.primary_functions) > 0
        assert len(profile.tech_stack) > 0
        assert profile.complexity_level in ["simple", "moderate", "complex", "advanced"]
        assert 0.0 <= profile.specialization_score <= 1.0

    def test_web_api_detection(self):
        """Test web API capability detection"""
        profile = self.extractor.extract_capabilities(self.api_code)

        # Should detect web_api capability
        web_caps = [cap for cap in profile.capabilities if cap.name == "web_api"]
        assert len(web_caps) > 0
        assert web_caps[0].confidence > 0.5

    def test_tech_stack_identification(self):
        """Test technology stack identification"""
        profile = self.extractor.extract_capabilities(self.api_code)

        # Should identify FastAPI and Requests
        assert "FastAPI" in profile.tech_stack
        assert "Requests" in profile.tech_stack

    def test_complexity_assessment(self):
        """Test complexity level assessment"""
        simple_code = "def add(a, b): return a + b"
        complex_code = """
from typing import Protocol, TypeVar, Generic
from abc import abstractmethod

T = TypeVar('T')

class Repository(Protocol, Generic[T]):
    @abstractmethod
    async def get(self, id: int) -> T: ...
"""

        simple_profile = self.extractor.extract_capabilities(simple_code)
        complex_profile = self.extractor.extract_capabilities(complex_code)

        assert simple_profile.complexity_level in ["simple", "moderate"]
        assert complex_profile.complexity_level in ["complex", "advanced"]

    def test_specialization_score(self):
        """Test specialization score calculation"""
        # Highly specialized (only data processing)
        specialized_code = """
import pandas as pd
import numpy as np

def process_csv(file):
    df = pd.read_csv(file)
    return df.groupby('col').mean()
"""

        # Multi-purpose (web + data + files)
        general_code = """
from fastapi import FastAPI
import pandas as pd
import shutil

app = FastAPI()

@app.post("/upload")
def upload_file(file):
    df = pd.read_csv(file)
    shutil.copy(file, "/backup/")
    return {"status": "ok"}
"""

        specialized_profile = self.extractor.extract_capabilities(specialized_code)
        general_profile = self.extractor.extract_capabilities(general_code)

        # Specialized should have higher score
        assert specialized_profile.specialization_score >= general_profile.specialization_score

    def test_to_dict_conversion(self):
        """Test profile to dictionary conversion"""
        profile = self.extractor.extract_capabilities(self.api_code)
        result_dict = self.extractor.to_dict(profile)

        assert isinstance(result_dict, dict)
        assert "capabilities" in result_dict
        assert "primary_functions" in result_dict
        assert "tech_stack" in result_dict
        assert "complexity_level" in result_dict
        assert "specialization_score" in result_dict

    def test_extract_quick_function(self):
        """Test quick extraction utility"""
        result = extract_quick(self.api_code)

        assert isinstance(result, dict)
        assert "top_capabilities" in result
        assert "complexity" in result
        assert "specialization" in result


class TestAnalysisPrompts:
    """Test AnalysisPrompts functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.prompts = AnalysisPrompts()
        self.sample_code = "def hello(): return 'world'"

    def test_prompts_initialization(self):
        """Test prompts initialization"""
        prompts = AnalysisPrompts()
        assert prompts is not None
        assert hasattr(prompts, "templates")
        assert len(prompts.templates) > 0

    def test_template_retrieval(self):
        """Test template retrieval"""
        template = self.prompts.get_template("code_analysis")
        assert template is not None
        assert template.name == "code_analysis"
        assert len(template.variables) > 0
        assert template.max_tokens > 0

    def test_prompt_formatting(self):
        """Test prompt formatting"""
        prompt = self.prompts.format_prompt("code_analysis", code=self.sample_code)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert self.sample_code in prompt

    def test_missing_variable_error(self):
        """Test error handling for missing variables"""
        with pytest.raises(ValueError, match="Missing variable"):
            self.prompts.format_prompt("code_analysis")  # Missing 'code' variable

    def test_convenience_functions(self):
        """Test convenience prompt functions"""
        analysis_prompt = self.prompts.get_analysis_prompt(self.sample_code)
        capability_prompt = self.prompts.get_capability_prompt(self.sample_code)
        optimization_prompt = self.prompts.get_optimization_prompt(self.sample_code, 100)

        assert isinstance(analysis_prompt, str)
        assert isinstance(capability_prompt, str)
        assert isinstance(optimization_prompt, str)

        assert self.sample_code in analysis_prompt
        assert self.sample_code in capability_prompt
        assert self.sample_code in optimization_prompt

    def test_template_listing(self):
        """Test template listing"""
        templates = self.prompts.list_templates()

        assert isinstance(templates, list)
        assert len(templates) > 0
        assert "code_analysis" in templates
        assert "capability_extraction" in templates

    def test_template_info(self):
        """Test template information retrieval"""
        info = self.prompts.get_template_info("code_analysis")

        assert isinstance(info, dict)
        assert "name" in info
        assert "variables" in info
        assert "max_tokens" in info
        assert "purpose" in info

    def test_global_prompt_functions(self):
        """Test global prompt utility functions"""
        # Test imported convenience functions
        result = analyze_code(self.sample_code)
        assert isinstance(result, str)
        assert self.sample_code in result

        # Test get_prompt function
        prompt = get_prompt("analyze", self.sample_code)
        assert isinstance(prompt, str)
        assert self.sample_code in prompt

    def test_invalid_prompt_type(self):
        """Test error handling for invalid prompt types"""
        with pytest.raises(ValueError, match="Unknown prompt type"):
            get_prompt("invalid_type", self.sample_code)


# Integration tests
class TestIntegration:
    """Integration tests for AI analyzer components"""

    def test_analyzer_with_extractor(self):
        """Test integration of analyzer and extractor"""
        code = """
import pandas as pd

def process_data(csv_file):
    df = pd.read_csv(csv_file)
    return df.describe()
"""

        analyzer = CodeAnalyzer()
        extractor = CapabilityExtractor()

        analysis_result = analyzer.analyze_code(code)
        capability_profile = extractor.extract_capabilities(code)

        # Both should detect data processing
        assert "data_processing" in analysis_result.capabilities
        assert any(cap.name == "data_processing" for cap in capability_profile.capabilities)

    def test_memory_constraint_validation(self):
        """Test 6.5KB memory constraint across components"""
        # Test with code exactly at limit
        large_code = "# " + "x" * 6650  # ~6.5KB

        analyzer = CodeAnalyzer()
        result = analyzer.analyze_code(large_code)

        # Should flag as not memory efficient
        assert result.memory_efficient == False
        assert any("6.5KB" in suggestion for suggestion in result.suggestions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
