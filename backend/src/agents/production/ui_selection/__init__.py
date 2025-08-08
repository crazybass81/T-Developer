"""
UI Selection Agent Production Implementation
UI 프레임워크 및 기술 스택 선택 에이전트
"""

from .core import UISelectionAgent, UISelectionResult, UIStack
from .framework_analyzer import FrameworkAnalyzer
from .design_system_selector import DesignSystemSelector
from .component_library_matcher import ComponentLibraryMatcher
from .boilerplate_generator import BoilerplateGenerator
from .realtime_benchmarker import RealtimeBenchmarker
from .validation import UISelectionValidator
from .monitoring import UISelectionMonitor

__all__ = [
    'UISelectionAgent',
    'UISelectionResult',
    'UIStack',
    'FrameworkAnalyzer',
    'DesignSystemSelector',
    'ComponentLibraryMatcher',
    'BoilerplateGenerator',
    'RealtimeBenchmarker',
    'UISelectionValidator',
    'UISelectionMonitor'
]

# 버전 정보
__version__ = '1.0.0'