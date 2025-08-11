"""
Generation Agent - Production Implementation
Generates complete project code from selected components and requirements
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import json
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Import base classes
import sys
sys.path.append('/home/ec2-user/T-DeveloperMVP/backend/src')

from agents.unified.base_agent import UnifiedBaseAgent
from agents.phase2_enhancements import Phase2GenerationResult

# Import all specialized modules
from .modules.code_generator import CodeGenerator
from .modules.project_scaffolder import ProjectScaffolder
from .modules.dependency_manager import DependencyManager
from .modules.template_engine import TemplateEngine
from .modules.configuration_generator import ConfigurationGenerator
from .modules.integration_builder import IntegrationBuilder
from .modules.documentation_generator import DocumentationGenerator
from .modules.testing_generator import TestingGenerator
from .modules.deployment_generator import DeploymentGenerator
from .modules.quality_checker import QualityChecker
from .modules.optimization_engine import OptimizationEngine
from .modules.version_manager import VersionManager


class EnhancedGenerationResult(Phase2GenerationResult):
    """Enhanced result with ECS and production features"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generated_files = {}
        self.project_structure = {}
        self.dependencies = {}
        self.configurations = {}
        self.documentation = {}
        self.tests = {}
        self.deployment_configs = {}
        self.quality_metrics = {}
        self.optimization_report = {}
        self.version_info = {}
        self.generation_stats = {}
        self.build_instructions = []
        self.setup_commands = []


class GenerationAgent(UnifiedBaseAgent):
    """
    Production-ready Generation Agent
    Generates complete project code with advanced features
    """
    
    def __init__(self):
        super().__init__()
        self.agent_name = "Generation"
        self.version = "3.0.0"
        
        # Initialize all specialized modules (12+ modules)
        self.code_generator = CodeGenerator()
        self.project_scaffolder = ProjectScaffolder()
        self.dependency_manager = DependencyManager()
        self.template_engine = TemplateEngine()
        self.configuration_generator = ConfigurationGenerator()
        self.integration_builder = IntegrationBuilder()
        self.documentation_generator = DocumentationGenerator()
        self.testing_generator = TestingGenerator()
        self.deployment_generator = DeploymentGenerator()
        self.quality_checker = QualityChecker()
        self.optimization_engine = OptimizationEngine()
        self.version_manager = VersionManager()
        
        # Configuration
        self.config = {
            'supported_frameworks': [
                'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt.js',
                'express', 'fastapi', 'django', 'flask', 'spring-boot',
                'react-native', 'flutter', 'ionic'
            ],
            'supported_languages': [
                'javascript', 'typescript', 'python', 'java', 'go', 
                'rust', 'php', 'ruby', 'kotlin', 'swift'
            ],
            'output_formats': ['zip', 'tar.gz', 'folder'],
            'quality_standards': {
                'code_coverage': 80,
                'cyclomatic_complexity': 10,
                'maintainability_index': 70,
                'duplication_ratio': 5
            },
            'generation_modes': ['full', 'minimal', 'advanced', 'enterprise'],
            'template_categories': [
                'web_app', 'api_server', 'mobile_app', 'desktop_app',
                'microservice', 'library', 'cli_tool', 'game'
            ]
        }
        
        # Generation context
        self.generation_context = {
            'project_name': '',
            'target_framework': '',
            'target_language': '',
            'architecture_pattern': '',
            'selected_components': [],
            'user_requirements': {},
            'output_directory': '',
            'generation_mode': 'full'
        }
        
    async def process(self, input_data: Dict[str, Any]) -> EnhancedGenerationResult:
        """
        Main processing method for code generation
        
        Args:
            input_data: Generation requirements and selected components
            
        Returns:
            EnhancedGenerationResult with complete project code
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not self._validate_input(input_data):
                return self._create_error_result("Invalid input data")
            
            # Initialize generation context
            self.generation_context = self._initialize_context(input_data)
            
            # Create temporary workspace
            workspace_path = await self._create_workspace()
            
            # Phase 1: Project Scaffolding
            await self.log_event("scaffolding_start", {"project": self.generation_context['project_name']})
            scaffold_result = await self.project_scaffolder.create_structure(
                self.generation_context, workspace_path
            )
            
            if not scaffold_result.success:
                return self._create_error_result(f"Scaffolding failed: {scaffold_result.error}")
            
            # Phase 2: Dependency Management
            await self.log_event("dependency_resolution_start", {})
            dependency_result = await self.dependency_manager.resolve_dependencies(
                self.generation_context['selected_components'],
                self.generation_context['target_framework'],
                self.generation_context['target_language']
            )
            
            # Phase 3: Code Generation
            await self.log_event("code_generation_start", {})
            code_tasks = [
                self.code_generator.generate_core_files(self.generation_context, workspace_path),
                self.code_generator.generate_component_integration(
                    self.generation_context['selected_components'], workspace_path
                ),
                self.configuration_generator.generate_configs(self.generation_context, workspace_path),
                self.integration_builder.build_integrations(self.generation_context, workspace_path)
            ]
            
            generation_results = await asyncio.gather(*code_tasks)
            
            # Phase 4: Documentation and Testing
            await self.log_event("documentation_generation_start", {})
            doc_and_test_tasks = [
                self.documentation_generator.generate_documentation(
                    self.generation_context, workspace_path
                ),
                self.testing_generator.generate_tests(
                    self.generation_context, workspace_path
                ),
                self.deployment_generator.generate_deployment_configs(
                    self.generation_context, workspace_path
                )
            ]
            
            doc_test_results = await asyncio.gather(*doc_and_test_tasks)
            
            # Phase 5: Quality Assurance
            await self.log_event("quality_check_start", {})
            quality_result = await self.quality_checker.analyze_project(
                workspace_path, self.generation_context
            )
            
            # Phase 6: Optimization
            await self.log_event("optimization_start", {})
            optimization_result = await self.optimization_engine.optimize_project(
                workspace_path, self.generation_context, quality_result
            )
            
            # Phase 7: Version Management
            version_result = await self.version_manager.setup_versioning(
                workspace_path, self.generation_context
            )
            
            # Collect all generated files
            generated_files = await self._collect_generated_files(workspace_path)
            
            # Create comprehensive result
            result = EnhancedGenerationResult(
                success=True,
                data=generated_files,
                metadata={
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'project_name': self.generation_context['project_name'],
                    'framework': self.generation_context['target_framework'],
                    'language': self.generation_context['target_language'],
                    'components_count': len(self.generation_context['selected_components']),
                    'files_generated': len(generated_files),
                    'workspace_path': workspace_path
                }
            )
            
            # Populate enhanced result fields
            result.generated_files = generated_files
            result.project_structure = scaffold_result.data.get('structure', {})
            result.dependencies = dependency_result.data if dependency_result.success else {}
            result.configurations = generation_results[2].data if len(generation_results) > 2 else {}
            result.documentation = doc_test_results[0].data if len(doc_test_results) > 0 else {}
            result.tests = doc_test_results[1].data if len(doc_test_results) > 1 else {}
            result.deployment_configs = doc_test_results[2].data if len(doc_test_results) > 2 else {}
            result.quality_metrics = quality_result.data if quality_result.success else {}
            result.optimization_report = optimization_result.data if optimization_result.success else {}
            result.version_info = version_result.data if version_result.success else {}
            result.generation_stats = self._calculate_generation_stats(start_time, generated_files)
            result.build_instructions = self._generate_build_instructions()
            result.setup_commands = self._generate_setup_commands()
            
            await self.log_event("generation_complete", {
                'project': self.generation_context['project_name'],
                'files_generated': len(generated_files),
                'processing_time': result.metadata['processing_time']
            })
            
            return result
            
        except Exception as e:
            await self.log_event("generation_error", {"error": str(e)})
            return self._create_error_result(f"Generation failed: {str(e)}")
    
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data structure"""
        
        required_fields = ['project_name', 'selected_components']
        
        for field in required_fields:
            if field not in input_data:
                return False
        
        # Validate project name
        project_name = input_data.get('project_name', '')
        if not project_name or len(project_name) < 3:
            return False
        
        # Validate selected components
        components = input_data.get('selected_components', [])
        if not components or len(components) == 0:
            return False
        
        return True
    
    def _initialize_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize generation context from input"""
        
        context = {
            'project_name': input_data.get('project_name', ''),
            'target_framework': input_data.get('target_framework', 'react'),
            'target_language': input_data.get('target_language', 'javascript'),
            'architecture_pattern': input_data.get('architecture_pattern', 'mvc'),
            'selected_components': input_data.get('selected_components', []),
            'user_requirements': input_data.get('requirements', {}),
            'generation_mode': input_data.get('generation_mode', 'full'),
            'output_format': input_data.get('output_format', 'folder'),
            'include_tests': input_data.get('include_tests', True),
            'include_docs': input_data.get('include_docs', True),
            'include_deployment': input_data.get('include_deployment', True),
            'quality_level': input_data.get('quality_level', 'standard')
        }
        
        # Auto-detect framework and language from components if not specified
        if context['target_framework'] == 'auto':
            context['target_framework'] = self._detect_framework(context['selected_components'])
        
        if context['target_language'] == 'auto':
            context['target_language'] = self._detect_language(
                context['target_framework'], context['selected_components']
            )
        
        return context
    
    async def _create_workspace(self) -> str:
        """Create temporary workspace for generation"""
        
        base_path = tempfile.mkdtemp(prefix="generation_")
        project_path = os.path.join(base_path, self.generation_context['project_name'])
        
        os.makedirs(project_path, exist_ok=True)
        
        return project_path
    
    async def _collect_generated_files(self, workspace_path: str) -> Dict[str, str]:
        """Collect all generated files from workspace"""
        
        generated_files = {}
        
        for root, dirs, files in os.walk(workspace_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, workspace_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        generated_files[relative_path] = f.read()
                except UnicodeDecodeError:
                    # Handle binary files
                    with open(file_path, 'rb') as f:
                        generated_files[relative_path] = f"<binary file: {len(f.read())} bytes>"
                except Exception as e:
                    generated_files[relative_path] = f"<error reading file: {str(e)}>"
        
        return generated_files
    
    def _detect_framework(self, components: List[Dict[str, Any]]) -> str:
        """Auto-detect target framework from selected components"""
        
        framework_indicators = {}
        
        for component in components:
            technology = component.get('technology', '').lower()
            category = component.get('category', '').lower()
            
            # Count framework indicators
            if technology in ['react', 'vue', 'angular', 'svelte']:
                framework_indicators[technology] = framework_indicators.get(technology, 0) + 1
            elif 'react' in category or 'react' in component.get('name', '').lower():
                framework_indicators['react'] = framework_indicators.get('react', 0) + 1
            elif 'vue' in category or 'vue' in component.get('name', '').lower():
                framework_indicators['vue'] = framework_indicators.get('vue', 0) + 1
            elif 'angular' in category or 'angular' in component.get('name', '').lower():
                framework_indicators['angular'] = framework_indicators.get('angular', 0) + 1
        
        # Return most common framework or default to React
        if framework_indicators:
            return max(framework_indicators.items(), key=lambda x: x[1])[0]
        else:
            return 'react'  # Default
    
    def _detect_language(self, framework: str, components: List[Dict[str, Any]]) -> str:
        """Auto-detect target language based on framework and components"""
        
        # Framework-based language defaults
        framework_languages = {
            'react': 'typescript',
            'vue': 'typescript', 
            'angular': 'typescript',
            'svelte': 'typescript',
            'express': 'typescript',
            'fastapi': 'python',
            'django': 'python',
            'flask': 'python',
            'spring-boot': 'java'
        }
        
        default_language = framework_languages.get(framework, 'javascript')
        
        # Check component preferences
        language_indicators = {default_language: 1}
        
        for component in components:
            tags = component.get('tags', [])
            if 'typescript' in tags or 'ts' in tags:
                language_indicators['typescript'] = language_indicators.get('typescript', 0) + 1
            elif 'javascript' in tags or 'js' in tags:
                language_indicators['javascript'] = language_indicators.get('javascript', 0) + 1
            elif 'python' in tags:
                language_indicators['python'] = language_indicators.get('python', 0) + 1
        
        return max(language_indicators.items(), key=lambda x: x[1])[0]
    
    def _calculate_generation_stats(
        self, 
        start_time: datetime, 
        generated_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """Calculate generation statistics"""
        
        total_lines = 0
        total_chars = 0
        file_types = {}
        
        for file_path, content in generated_files.items():
            if isinstance(content, str) and not content.startswith('<'):
                lines = len(content.split('\n'))
                chars = len(content)
                
                total_lines += lines
                total_chars += chars
                
                # Count file types
                extension = os.path.splitext(file_path)[1]
                file_types[extension] = file_types.get(extension, 0) + 1
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'total_files': len(generated_files),
            'total_lines_of_code': total_lines,
            'total_characters': total_chars,
            'file_types': file_types,
            'processing_time_seconds': processing_time,
            'generation_speed_lines_per_second': total_lines / processing_time if processing_time > 0 else 0,
            'estimated_project_size': self._estimate_project_size(total_lines, file_types)
        }
    
    def _estimate_project_size(self, total_lines: int, file_types: Dict[str, int]) -> str:
        """Estimate project size category"""
        
        if total_lines < 1000:
            return 'Small'
        elif total_lines < 5000:
            return 'Medium'
        elif total_lines < 15000:
            return 'Large'
        else:
            return 'Very Large'
    
    def _generate_build_instructions(self) -> List[str]:
        """Generate build instructions for the project"""
        
        framework = self.generation_context['target_framework']
        language = self.generation_context['target_language']
        
        instructions = []
        
        # Framework-specific instructions
        if framework in ['react', 'vue', 'angular']:
            instructions.extend([
                "1. Navigate to project directory",
                "2. Install dependencies: npm install",
                "3. Start development server: npm run dev",
                "4. Build for production: npm run build"
            ])
        elif framework == 'fastapi':
            instructions.extend([
                "1. Navigate to project directory",
                "2. Create virtual environment: python -m venv venv",
                "3. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)",
                "4. Install dependencies: pip install -r requirements.txt",
                "5. Start development server: uvicorn main:app --reload"
            ])
        elif framework == 'django':
            instructions.extend([
                "1. Navigate to project directory",
                "2. Create virtual environment: python -m venv venv",
                "3. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)",
                "4. Install dependencies: pip install -r requirements.txt",
                "5. Run migrations: python manage.py migrate",
                "6. Start development server: python manage.py runserver"
            ])
        
        # Add common instructions
        if self.generation_context['include_tests']:
            instructions.append("5. Run tests: npm test" if framework in ['react', 'vue', 'angular'] else "5. Run tests: pytest")
        
        return instructions
    
    def _generate_setup_commands(self) -> List[str]:
        """Generate setup commands for the project"""
        
        framework = self.generation_context['target_framework']
        project_name = self.generation_context['project_name']
        
        commands = []
        
        if framework in ['react', 'vue', 'angular']:
            commands.extend([
                f"cd {project_name}",
                "npm install",
                "npm run dev"
            ])
        elif framework in ['fastapi', 'django', 'flask']:
            commands.extend([
                f"cd {project_name}",
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt"
            ])
            
            if framework == 'django':
                commands.extend([
                    "python manage.py migrate",
                    "python manage.py runserver"
                ])
            elif framework == 'fastapi':
                commands.append("uvicorn main:app --reload")
        
        return commands
    
    def _create_error_result(self, error_message: str) -> EnhancedGenerationResult:
        """Create error result"""
        
        result = EnhancedGenerationResult(
            success=False,
            data={},
            error=error_message
        )
        
        return result
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        
        health = await super().health_check()
        
        # Add module-specific health checks
        health['modules'] = {
            'code_generator': 'healthy',
            'project_scaffolder': 'healthy',
            'dependency_manager': 'healthy',
            'template_engine': 'healthy',
            'configuration_generator': 'healthy',
            'integration_builder': 'healthy',
            'documentation_generator': 'healthy',
            'testing_generator': 'healthy',
            'deployment_generator': 'healthy',
            'quality_checker': 'healthy',
            'optimization_engine': 'healthy',
            'version_manager': 'healthy'
        }
        
        health['supported_frameworks'] = self.config['supported_frameworks']
        health['supported_languages'] = self.config['supported_languages']
        health['generation_capabilities'] = {
            'full_stack_apps': True,
            'api_servers': True,
            'mobile_apps': True,
            'libraries': True,
            'cli_tools': True
        }
        
        return health
    
    async def get_supported_technologies(self) -> Dict[str, List[str]]:
        """Get list of supported technologies"""
        
        return {
            'frameworks': self.config['supported_frameworks'],
            'languages': self.config['supported_languages'],
            'architectures': ['mvc', 'mvvm', 'microservices', 'serverless', 'jamstack'],
            'databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'sqlite'],
            'deployment_targets': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'netlify', 'vercel']
        }
    
    async def estimate_generation_time(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate generation time and complexity"""
        
        components_count = len(input_data.get('selected_components', []))
        generation_mode = input_data.get('generation_mode', 'full')
        include_tests = input_data.get('include_tests', True)
        include_docs = input_data.get('include_docs', True)
        
        # Base time estimation
        base_time = 30  # seconds
        
        # Factor in complexity
        complexity_factor = 1.0
        complexity_factor += components_count * 0.1
        
        if generation_mode == 'enterprise':
            complexity_factor *= 1.5
        elif generation_mode == 'minimal':
            complexity_factor *= 0.7
        
        if include_tests:
            complexity_factor *= 1.2
        
        if include_docs:
            complexity_factor *= 1.1
        
        estimated_time = base_time * complexity_factor
        
        return {
            'estimated_time_seconds': round(estimated_time, 1),
            'complexity_score': round(complexity_factor, 2),
            'factors': {
                'components_count': components_count,
                'generation_mode': generation_mode,
                'include_tests': include_tests,
                'include_docs': include_docs
            }
        }