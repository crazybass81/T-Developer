"""
Generation Agent - ECS Integrated Version
Generates project code and configurations
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Base agent import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add current directory to path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from base_agent import BaseAgent, AgentConfig, AgentContext, AgentResult, AgentStatus

# Module imports - Production Implementation
from modules.code_generator import CodeGenerator
from modules.config_generator import ConfigGenerator
from modules.test_generator import TestGenerator
from modules.documentation_generator import DocumentationGenerator
from modules.deployment_generator import DeploymentGenerator

@dataclass
class GenerationAgentResult:
    """Result from Generation Agent"""
    processed_data: Dict[str, Any]
    metadata: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float

class GenerationAgent(BaseAgent):
    """
    Generates project code and configurations
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Generation Agent with configuration"""
        
        if not config:
            config = AgentConfig(
                name="GenerationAgent",
                version="2.0.0",
                capabilities=["code_generator", "config_generator", "test_generator", "documentation_generator", "deployment_generator"],
                resource_requirements={
                    "cpu": "4 vCPU",
                    "memory": "8GB",
                    "timeout": 300
                },
                service_group="generation"
            )
        
        super().__init__(config)
        
        # Initialize modules - Production instances
        self.code_generator = CodeGenerator()
        self.config_generator = ConfigGenerator()
        self.test_generator = TestGenerator()
        self.documentation_generator = DocumentationGenerator()
        self.deployment_generator = DeploymentGenerator()
    
    async def initialize(self) -> bool:
        """Initialize agent and its modules"""
        
        try:
            self.logger.info("Initializing Generation Agent modules...")
            
            # Initialize all modules
            await asyncio.gather(
                self.code_generator.initialize(),
                self.config_generator.initialize(),
                self.test_generator.initialize(),
                self.documentation_generator.initialize(),
                self.deployment_generator.initialize()
            )
            
            self.status = AgentStatus.READY
            self.logger.info("Generation Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Generation Agent: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def _custom_initialize(self):
        """Custom initialization for agent"""
        pass

    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> AgentResult[GenerationAgentResult]:
        """
        Process generation request
        
        Args:
            input_data: Input from previous agent
            context: Processing context
            
        Returns:
            generation results
        """
        
        self.status = AgentStatus.PROCESSING
        start_time = datetime.now()
        
        try:
            # Extract input specifications
            project_specs = input_data.get('specifications', {})
            components = input_data.get('components', [])
            features = input_data.get('features', [])
            
            self.logger.info(f"Generating code for {len(components)} components with {len(features)} features")
            
            # 1. Generate code files
            code_result = await self.code_generator.process({
                'project_type': project_specs.get('type', 'web'),
                'language': project_specs.get('language', 'python'),
                'framework': project_specs.get('framework', 'fastapi'),
                'features': features,
                'components': components
            }, context.__dict__ if context else None)
            
            # 2. Generate configuration files
            config_result = await self.config_generator.process({
                'framework': project_specs.get('framework', 'fastapi'),
                'features': features,
                'environment': 'production'
            }, context.__dict__ if context else None)
            
            # 3. Generate tests if requested
            test_result = {}
            if 'testing' in features:
                test_result = await self.test_generator.process({
                    'components': components,
                    'framework': project_specs.get('framework', 'fastapi')
                }, context.__dict__ if context else None)
            
            # 4. Generate documentation
            doc_result = await self.documentation_generator.process({
                'project_specs': project_specs,
                'components': components,
                'features': features
            }, context.__dict__ if context else None)
            
            # 5. Generate deployment configurations
            deployment_result = await self.deployment_generator.process({
                'platform': project_specs.get('deployment_platform', 'aws'),
                'framework': project_specs.get('framework', 'fastapi')
            }, context.__dict__ if context else None)
            
            # Aggregate all generated files
            processed_data = {
                'files': {
                    **code_result.get('files', {}),
                    **config_result.get('files', {}),
                    **test_result.get('files', {}),
                    **doc_result.get('files', {}),
                    **deployment_result.get('files', {})
                },
                'total_files': len(code_result.get('files', {})) + 
                              len(config_result.get('files', {})) + 
                              len(test_result.get('files', {})) +
                              len(doc_result.get('files', {})) +
                              len(deployment_result.get('files', {}))
            }
            
            # Collect metadata
            metadata = {
                'code_quality_score': code_result.get('quality_score', 0),
                'total_lines': sum(len(content.split('\n')) for content in processed_data['files'].values()),
                'language': project_specs.get('language', 'python'),
                'framework': project_specs.get('framework', 'fastapi')
            }
            
            # Generate recommendations
            recommendations = [
                "Review generated code for project-specific customizations",
                "Update environment variables in .env file",
                "Run tests to ensure code quality",
                "Configure CI/CD pipelines for automated deployment"
            ]
            
            # Calculate overall confidence based on completeness
            confidence = min(0.95, 
                           (processed_data['total_files'] / max(1, len(components) * 3)) * 
                           (code_result.get('quality_score', 80) / 100))
            
            # Create result
            result = GenerationAgentResult(
                processed_data=processed_data,
                metadata=metadata,
                recommendations=recommendations,
                confidence_score=confidence
            )
            
            # Cache result
            cache_key = f"generation:{context.request_id}"
            await self.cache_result(cache_key, asdict(result))
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.update_metrics({
                "processing_time": processing_time,
                "confidence_score": confidence
            })
            
            self.status = AgentStatus.COMPLETED
            self.logger.info(f"Generation Agent completed in {processing_time:.2f}s")
            
            return AgentResult(
                success=True,
                data=result,
                metadata={
                    "processing_time": processing_time,
                    "confidence": confidence
                }
            )
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Generation Agent failed: {e}")
            
            return AgentResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"error_type": type(e).__name__}
            )
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        
        # TODO: Add specific validation logic
        return True
    
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        
        self.logger.info("Cleaning up Generation Agent...")
        pass
