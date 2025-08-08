"""
Parser Agent Production Implementation
Phase 4 Tasks 4.21-4.30 완전 구현
"""

from .core import (
    ParserAgent,
    ParsedProject,
    ParsedRequirement,
    UserStory,
    DataModel,
    APISpecification,
    UIComponent,
    IntegrationPoint,
    RequirementType,
    RequirementPriority
)
from .requirement_extractor import RequirementExtractor
from .user_story_generator import UserStoryGenerator
from .data_model_parser import DataModelParser
from .api_spec_parser import APISpecificationParser
from .ui_component_identifier import UIComponentIdentifier
from .integration_analyzer import IntegrationAnalyzer
from .constraint_analyzer import ConstraintAnalyzer
from .dependency_analyzer import DependencyAnalyzer
from .validation_framework import ValidationFramework
from .traceability_generator import TraceabilityGenerator

__all__ = [
    'ParserAgent',
    'ParsedProject',
    'ParsedRequirement',
    'UserStory',
    'DataModel',
    'APISpecification',
    'UIComponent',
    'IntegrationPoint',
    'RequirementType',
    'RequirementPriority',
    'RequirementExtractor',
    'UserStoryGenerator',
    'DataModelParser',
    'APISpecificationParser',
    'UIComponentIdentifier',
    'IntegrationAnalyzer',
    'ConstraintAnalyzer',
    'DependencyAnalyzer',
    'ValidationFramework',
    'TraceabilityGenerator'
]

# 버전 정보
__version__ = '1.0.0'