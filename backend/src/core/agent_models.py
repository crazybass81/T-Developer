"""
Agent-specific data models for the 9-agent pipeline
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# ============= NL Input Agent Models =============


@dataclass
class NLInputResult:
    """Result from Natural Language Input Agent"""

    project_type: str
    main_functionality: str
    technical_requirements: Dict[str, Any]
    features: List[str]
    constraints: List[str]
    preferences: Dict[str, str]
    complexity: str  # simple, medium, complex
    estimated_effort_hours: int
    keywords: List[str]
    intent_confidence: float

    # Language analysis
    language: str = "en"
    sentiment: str = "neutral"
    clarity_score: float = 1.0


# ============= UI Selection Agent Models =============


@dataclass
class FrameworkChoice:
    """Framework selection details"""

    name: str
    version: str
    reason: str
    compatibility_score: float
    ecosystem_maturity: float
    community_support: float


@dataclass
class UISelectionResult:
    """Result from UI Selection Agent"""

    framework: FrameworkChoice
    ui_library: Optional[FrameworkChoice]
    styling_solution: FrameworkChoice
    state_management: Optional[FrameworkChoice]
    bundler: FrameworkChoice
    testing_framework: FrameworkChoice

    # Additional recommendations
    component_libraries: List[str] = field(default_factory=list)
    dev_tools: List[str] = field(default_factory=list)
    deployment_target: str = "vercel"

    # Performance considerations
    estimated_bundle_size_kb: int = 0
    estimated_build_time_seconds: int = 0


# ============= Parser Agent Models =============


@dataclass
class FileStructure:
    """File and directory structure"""

    path: str
    type: str  # file or directory
    children: List["FileStructure"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIEndpoint:
    """API endpoint definition"""

    method: str
    path: str
    description: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    authentication_required: bool = True


@dataclass
class DatabaseSchema:
    """Database table schema"""

    table_name: str
    columns: Dict[str, str]
    primary_key: str
    foreign_keys: Dict[str, str] = field(default_factory=dict)
    indexes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class ParserResult:
    """Result from Parser Agent"""

    file_structure: FileStructure
    api_endpoints: List[APIEndpoint]
    database_schemas: List[DatabaseSchema]

    # Configuration files
    config_files: Dict[str, Any] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)

    # Module organization
    modules: Dict[str, List[str]] = field(default_factory=dict)
    entry_points: List[str] = field(default_factory=list)

    # Dependencies
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)


# ============= Component Decision Agent Models =============


class ArchitecturePattern(Enum):
    """Architecture patterns"""

    MVC = "mvc"
    MVP = "mvp"
    MVVM = "mvvm"
    FEATURE_BASED = "feature_based"
    DOMAIN_DRIVEN = "domain_driven"
    LAYERED = "layered"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"


@dataclass
class ComponentDefinition:
    """Component definition"""

    name: str
    type: str  # container, presentational, hook, service, etc.
    purpose: str
    props: Dict[str, str] = field(default_factory=dict)
    state: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)


@dataclass
class ComponentDecisionResult:
    """Result from Component Decision Agent"""

    architecture_pattern: ArchitecturePattern
    design_patterns: List[str]
    components: List[ComponentDefinition]
    component_hierarchy: Dict[str, Any]

    # Data flow
    data_flow_type: str  # unidirectional, bidirectional
    state_management_strategy: str

    # Communication patterns
    event_system: Optional[str] = None
    messaging_pattern: Optional[str] = None

    # Modularization
    modules: Dict[str, List[str]] = field(default_factory=dict)
    shared_components: List[str] = field(default_factory=list)
    utility_functions: List[str] = field(default_factory=list)


# ============= Match Rate Agent Models =============


@dataclass
class TemplateMatch:
    """Template matching result"""

    template_id: str
    template_name: str
    match_score: float
    matching_features: List[str]
    missing_features: List[str]
    additional_features: List[str]
    customization_effort: str  # none, minor, moderate, major
    estimated_adaptation_hours: int


@dataclass
class MatchRateResult:
    """Result from Match Rate Agent"""

    template_matches: List[TemplateMatch]
    best_match: Optional[TemplateMatch]
    recommendation: str  # use_template, customize_template, build_from_scratch
    confidence: float

    # Gap analysis
    coverage_percentage: float
    missing_capabilities: List[str]

    # Customization plan
    required_modifications: List[str] = field(default_factory=list)
    new_components_needed: List[str] = field(default_factory=list)
    estimated_total_effort_hours: int = 0


# ============= Search Agent Models =============


@dataclass
class LibraryInfo:
    """Library/package information"""

    name: str
    version: str
    purpose: str
    license: str
    popularity: int  # downloads/stars
    last_updated: datetime
    size_kb: int
    dependencies_count: int
    security_score: float = 1.0
    compatibility_confirmed: bool = True


@dataclass
class CodeSnippet:
    """Code snippet from search"""

    source: str  # github, stackoverflow, etc.
    url: str
    relevance_score: float
    language: str
    description: str
    code: str
    usage_count: int = 0
    quality_score: float = 1.0


@dataclass
class SearchResult:
    """Result from Search Agent"""

    libraries: List[LibraryInfo]
    code_snippets: List[CodeSnippet]
    best_practices: List[str]

    # Documentation and resources
    documentation_links: List[str] = field(default_factory=list)
    tutorial_links: List[str] = field(default_factory=list)
    example_projects: List[str] = field(default_factory=list)

    # Security and licensing
    security_warnings: List[str] = field(default_factory=list)
    license_conflicts: List[str] = field(default_factory=list)

    # Alternative solutions
    alternative_libraries: Dict[str, List[str]] = field(default_factory=dict)


# ============= Generation Agent Models =============


@dataclass
class GeneratedFile:
    """Generated file information"""

    path: str
    content: str
    file_type: str
    size_bytes: int
    lines_of_code: int
    language: str
    has_tests: bool = False
    test_coverage: float = 0.0


@dataclass
class GenerationResult:
    """Result from Generation Agent"""

    files: List[GeneratedFile]
    total_files: int
    total_lines_of_code: int

    # Code quality metrics
    code_quality_score: float
    test_coverage: float
    documentation_coverage: float

    # Generation statistics
    generation_time_seconds: float
    templates_used: List[str] = field(default_factory=list)

    # Components and modules
    components_created: int = 0
    services_created: int = 0
    tests_created: int = 0

    # Validation
    syntax_valid: bool = True
    type_checking_passed: bool = True
    linting_passed: bool = True


# ============= Assembly Agent Models =============


@dataclass
class BuildResult:
    """Build process result"""

    success: bool
    output_path: str
    build_time_seconds: float
    bundle_size_bytes: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Test execution result"""

    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    coverage_percentage: float
    execution_time_seconds: float
    test_report_path: Optional[str] = None


@dataclass
class AssemblyResult:
    """Result from Assembly Agent"""

    project_path: str
    build_result: BuildResult
    test_result: Optional[TestResult]

    # Validation results
    structure_valid: bool
    dependencies_installed: bool
    configuration_valid: bool

    # Documentation
    readme_generated: bool
    api_docs_generated: bool
    user_guide_generated: bool

    # Deployment readiness
    docker_configured: bool = False
    ci_cd_configured: bool = False
    environment_files_created: bool = True

    # Quality checks
    security_scan_passed: bool = True
    accessibility_check_passed: bool = True
    performance_check_passed: bool = True


# ============= Download Agent Models =============


@dataclass
class PackageMetadata:
    """Package metadata"""

    project_id: str
    project_name: str
    version: str
    created_at: datetime
    framework: str
    language: str

    # Package details
    total_files: int
    total_size_bytes: int
    compressed_size_bytes: int

    # Generation details
    pipeline_id: str
    agents_used: List[str]
    generation_time_seconds: float

    # Instructions
    setup_instructions: str
    run_instructions: str
    deployment_instructions: Optional[str] = None


@dataclass
class DownloadResult:
    """Result from Download Agent"""

    package_url: str
    package_format: str  # zip, tar.gz
    package_size_mb: float
    checksum: str

    # Package contents
    metadata: PackageMetadata
    included_files: int
    excluded_files: List[str] = field(default_factory=list)

    # Download details
    download_token: Optional[str] = None
    expiry_time: Optional[datetime] = None

    # Additional resources
    documentation_url: Optional[str] = None
    demo_url: Optional[str] = None
    repository_url: Optional[str] = None


# ============= Pipeline Result =============


@dataclass
class PipelineResult:
    """Complete pipeline execution result"""

    pipeline_id: str
    project_id: str
    status: str

    # Agent results
    nl_input: Optional[NLInputResult] = None
    ui_selection: Optional[UISelectionResult] = None
    parser: Optional[ParserResult] = None
    component_decision: Optional[ComponentDecisionResult] = None
    match_rate: Optional[MatchRateResult] = None
    search: Optional[SearchResult] = None
    generation: Optional[GenerationResult] = None
    assembly: Optional[AssemblyResult] = None
    download: Optional[DownloadResult] = None

    # Execution metrics
    total_execution_time_seconds: float = 0.0
    total_agents_executed: int = 0
    successful_agents: int = 0
    failed_agents: int = 0

    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# Export all models
__all__ = [
    "NLInputResult",
    "FrameworkChoice",
    "UISelectionResult",
    "FileStructure",
    "APIEndpoint",
    "DatabaseSchema",
    "ParserResult",
    "ArchitecturePattern",
    "ComponentDefinition",
    "ComponentDecisionResult",
    "TemplateMatch",
    "MatchRateResult",
    "LibraryInfo",
    "CodeSnippet",
    "SearchResult",
    "GeneratedFile",
    "GenerationResult",
    "BuildResult",
    "TestResult",
    "AssemblyResult",
    "PackageMetadata",
    "DownloadResult",
    "PipelineResult",
]
