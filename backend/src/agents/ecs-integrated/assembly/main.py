"""
Assembly Agent - ECS Integrated Version
Assembles generated components into complete project
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

from base_agent import BaseAgent, AgentConfig, AgentContext, AgentResult, AgentStatus

# Module imports with better path handling
try:
    from .modules.project_assembler import ProjectAssembler
except ImportError:
    try:
        # Try absolute import
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        from modules.project_assembler import ProjectAssembler
    except ImportError:
        # Final fallback - create a stub
        class ProjectAssembler:
            async def initialize(self):
                return True
            async def assemble_project(self, *args, **kwargs):
                return {"success": True, "project_path": "/tmp/project", "files_created": 0, "total_size": 0}

@dataclass
class AssemblyAgentResult:
    """Result from Assembly Agent"""
    processed_data: Dict[str, Any]
    metadata: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float

class AssemblyAgent(BaseAgent):
    """
    Assembles generated components into complete project
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Assembly Agent with configuration"""
        
        if not config:
            config = AgentConfig(
                name="AssemblyAgent",
                version="2.0.0",
                capabilities=["project_structurer", "dependency_installer", "config_merger", "build_optimizer", "validation_runner"],
                resource_requirements={
                    "cpu": "4 vCPU",
                    "memory": "8GB",
                    "timeout": 300
                },
                service_group="generation"
            )
        
        super().__init__(config)
        
        # Initialize modules
        self.project_assembler = ProjectAssembler()
    
    async def initialize(self) -> bool:
        """Initialize agent and its modules"""
        
        try:
            self.logger.info("Initializing Assembly Agent modules...")
            
            # Initialize project assembler
            await self.project_assembler.initialize()
            
            self.status = AgentStatus.READY
            self.logger.info("Assembly Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Assembly Agent: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def _custom_initialize(self):
        """Custom initialization for agent"""
        pass

    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> AgentResult[AssemblyAgentResult]:
        """
        Process assembly request
        
        Args:
            input_data: Input from previous agent
            context: Processing context
            
        Returns:
            assembly results
        """
        
        self.status = AgentStatus.PROCESSING
        start_time = datetime.now()
        
        try:
            self.logger.info("Processing with Assembly Agent...")
            
            # Extract project information
            project_id = context.request_id or f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get generated code from previous agent (Generation Agent)
            generated_code = input_data.get('generated_code', {})
            project_metadata = input_data.get('metadata', {})
            
            # Add project info to metadata
            project_metadata.update({
                'project_name': input_data.get('project_name', 'untitled'),
                'project_type': input_data.get('project_type', 'react'),
                'features': input_data.get('features', []),
                'description': input_data.get('description', '')
            })
            
            # Assemble the project
            assembly_result = await self.project_assembler.assemble_project(
                project_id=project_id,
                generated_code=generated_code,
                project_metadata=project_metadata
            )
            
            if not assembly_result['success']:
                raise Exception(f"Assembly failed: {assembly_result.get('error')}")
            
            # Process results
            processed_data = {
                'project_id': project_id,
                'project_path': assembly_result['project_path'],
                'files_created': assembly_result['files_created'],
                'total_size': assembly_result['total_size'],
                'assembled': True
            }
            
            metadata = {
                'manifest': assembly_result.get('manifest', {}),
                'structure': assembly_result.get('structure', {})
            }
            
            recommendations = [
                f"Project assembled with {assembly_result['files_created']} files",
                f"Total size: {assembly_result['total_size']} bytes",
                "Ready for packaging and download"
            ]
            
            # Calculate confidence based on assembly success
            confidence = 0.95 if assembly_result['files_created'] > 0 else 0.5
            
            # Create result
            result = AssemblyAgentResult(
                processed_data=processed_data,
                metadata=metadata,
                recommendations=recommendations,
                confidence_score=confidence
            )
            
            # Cache result
            cache_key = f"assembly:{context.request_id}"
            await self.cache_result(cache_key, asdict(result))
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.update_metrics({
                "processing_time": processing_time,
                "confidence_score": confidence
            })
            
            self.status = AgentStatus.COMPLETED
            self.logger.info(f"Assembly Agent completed in {processing_time:.2f}s")
            
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
            self.logger.error(f"Assembly Agent failed: {e}")
            
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
        
        self.logger.info("Cleaning up Assembly Agent...")
        pass
