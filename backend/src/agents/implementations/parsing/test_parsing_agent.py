"""
Test suite for Parsing Agent
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from parsing_agent import ParsingAgent, ASTAnalyzer, DependencyMapper, PatternDetector

@pytest.fixture
def sample_python_code():
    return '''
import os
import sys
from typing import List, Dict

class SampleClass:
    def __init__(self, name: str):
        self.name = name
    
    def process_data(self, data: List[Dict]) -> Dict:
        result = {}
        for item in data:
            if item.get('valid'):
                result[item['key']] = item['value']
        return result
    
    def complex_method(self, x, y, z):
        if x > 0:
            if y > 0:
                if z > 0:
                    return x + y + z
                else:
                    return x + y
            else:
                return x
        else:
            return 0

def utility_function(param):
    return param * 2
'''

@pytest.fixture
def sample_codebase(tmp_path):
    """Create a sample codebase for testing"""
    
    # Create main module
    main_file = tmp_path / "main.py"
    main_file.write_text('''
from utils import helper_function
from models.user import User

def main():
    user = User("test")
    result = helper_function(user.name)
    print(result)

if __name__ == "__main__":
    main()
''')
    
    # Create utils module
    utils_dir = tmp_path / "utils"
    utils_dir.mkdir()
    (utils_dir / "__init__.py").write_text("")
    (utils_dir / "helpers.py").write_text('''
def helper_function(name: str) -> str:
    return f"Hello, {name}!"

class UtilityClass:
    @staticmethod
    def process(data):
        return data.upper()
''')
    
    # Create models module
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("")
    (models_dir / "user.py").write_text('''
class User:
    def __init__(self, name: str):
        self.name = name
    
    def get_info(self):
        return {"name": self.name}
''')
    
    return str(tmp_path)

class TestASTAnalyzer:
    """AST Analyzer 테스트"""
    
    @pytest.mark.asyncio
    async def test_python_ast_analysis(self, sample_python_code):
        analyzer = ASTAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_python_code)
            f.flush()
            
            result = await analyzer.analyze_file(f.name, 'python')
            
            # 클래스 검증
            assert len(result['classes']) == 1
            assert result['classes'][0]['name'] == 'SampleClass'
            assert 'process_data' in result['classes'][0]['methods']
            
            # 함수 검증
            functions = [f['name'] for f in result['functions']]
            assert 'utility_function' in functions
            
            # 임포트 검증
            assert 'os' in result['imports']
            assert 'sys' in result['imports']
            
        os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_complexity_calculation(self, sample_python_code):
        analyzer = ASTAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_python_code)
            f.flush()
            
            result = await analyzer.analyze_file(f.name, 'python')
            
            # complex_method의 복잡도가 높아야 함
            complex_func = next(
                (f for f in result['functions'] if f['name'] == 'complex_method'),
                None
            )
            assert complex_func is not None
            assert complex_func['complexity'] > 3
            
        os.unlink(f.name)

class TestDependencyMapper:
    """Dependency Mapper 테스트"""
    
    @pytest.mark.asyncio
    async def test_dependency_mapping(self, sample_codebase):
        mapper = DependencyMapper()
        
        result = await mapper.map_dependencies(sample_codebase)
        
        # 내부 의존성 확인
        assert 'main.py' in result['internal_dependencies']
        main_deps = result['internal_dependencies']['main.py']
        assert any('utils' in dep for dep in main_deps)
        assert any('models.user' in dep for dep in main_deps)
        
        # 외부 의존성 확인 (없어야 함)
        assert len(result['external_dependencies']) == 0
        
        # 순환 의존성 확인 (없어야 함)
        assert len(result['circular_dependencies']) == 0
    
    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, tmp_path):
        # 순환 의존성이 있는 코드 생성
        file_a = tmp_path / "a.py"
        file_a.write_text("from b import function_b")
        
        file_b = tmp_path / "b.py"
        file_b.write_text("from a import function_a")
        
        mapper = DependencyMapper()
        result = await mapper.map_dependencies(str(tmp_path))
        
        # 순환 의존성이 감지되어야 함
        assert len(result['circular_dependencies']) > 0

class TestPatternDetector:
    """Pattern Detector 테스트"""
    
    @pytest.mark.asyncio
    async def test_singleton_detection(self, tmp_path):
        singleton_code = '''
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
'''
        
        singleton_file = tmp_path / "singleton.py"
        singleton_file.write_text(singleton_code)
        
        detector = PatternDetector()
        patterns = await detector.detect_patterns(str(tmp_path))
        
        assert 'singleton' in patterns
        assert len(patterns['singleton']) > 0
        assert patterns['singleton'][0]['type'] == 'classic_singleton'
    
    @pytest.mark.asyncio
    async def test_factory_detection(self, tmp_path):
        factory_code = '''
class ShapeFactory:
    def create_circle(self, radius):
        return Circle(radius)
    
    def create_square(self, side):
        return Square(side)
    
    def make_triangle(self, base, height):
        return Triangle(base, height)
'''
        
        factory_file = tmp_path / "factory.py"
        factory_file.write_text(factory_code)
        
        detector = PatternDetector()
        patterns = await detector.detect_patterns(str(tmp_path))
        
        assert 'factory' in patterns
        assert len(patterns['factory']) > 0

class TestParsingAgent:
    """Parsing Agent 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_codebase_parsing(self, sample_codebase):
        agent = ParsingAgent()
        
        result = await agent.parse_codebase(sample_codebase)
        
        # 기본 구조 확인
        assert 'summary' in result
        assert 'structure' in result
        assert 'dependencies' in result
        assert 'patterns' in result
        assert 'metrics' in result
        assert 'recommendations' in result
        
        # 구조 분석 확인
        structure = result['structure']
        assert structure['total_files'] > 0
        assert '.py' in structure['languages']
        
        # 의존성 분석 확인
        dependencies = result['dependencies']
        assert 'internal_dependencies' in dependencies
        assert 'external_dependencies' in dependencies
    
    @pytest.mark.asyncio
    async def test_reusable_component_extraction(self, sample_codebase):
        agent = ParsingAgent()
        
        components = await agent.extract_reusable_components(sample_codebase)
        
        # 컴포넌트가 추출되어야 함
        assert len(components) > 0
        
        # User 클래스가 컴포넌트로 추출되어야 함
        user_component = next(
            (c for c in components if c.name == 'User'),
            None
        )
        assert user_component is not None
        assert user_component.type == 'class'
        assert user_component.reusability_score > 0
    
    @pytest.mark.asyncio
    async def test_metrics_calculation(self, sample_codebase):
        agent = ParsingAgent()
        
        result = await agent.parse_codebase(sample_codebase)
        metrics = result['metrics']
        
        # 메트릭이 계산되어야 함
        assert hasattr(metrics, 'cyclomatic_complexity')
        assert hasattr(metrics, 'maintainability_index')
        assert hasattr(metrics, 'technical_debt_ratio')
        assert isinstance(metrics.code_smells, list)
    
    @pytest.mark.asyncio
    async def test_recommendations_generation(self, sample_codebase):
        agent = ParsingAgent()
        
        result = await agent.parse_codebase(sample_codebase)
        recommendations = result['recommendations']
        
        # 권장사항이 생성되어야 함
        assert isinstance(recommendations, list)
        
        # 각 권장사항은 필수 필드를 가져야 함
        for rec in recommendations:
            assert 'type' in rec
            assert 'priority' in rec
            assert 'title' in rec
            assert 'description' in rec

class TestPerformance:
    """성능 테스트"""
    
    @pytest.mark.asyncio
    async def test_large_codebase_performance(self, tmp_path):
        # 큰 코드베이스 생성
        for i in range(50):
            file_path = tmp_path / f"module_{i}.py"
            file_path.write_text(f'''
class Module{i}:
    def __init__(self):
        self.value = {i}
    
    def process(self, data):
        return data * {i}
    
    def validate(self, input_data):
        if input_data > {i}:
            return True
        return False
''')
        
        agent = ParsingAgent()
        
        import time
        start_time = time.time()
        
        result = await agent.parse_codebase(str(tmp_path))
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 성능 검증 (50개 파일을 10초 이내에 처리)
        assert processing_time < 10
        assert result['structure']['total_files'] == 50
    
    @pytest.mark.asyncio
    async def test_memory_usage(self, sample_codebase):
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        agent = ParsingAgent()
        await agent.parse_codebase(sample_codebase)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 메모리 사용량이 100MB를 초과하지 않아야 함
        assert memory_increase < 100 * 1024 * 1024

if __name__ == "__main__":
    pytest.main([__file__])