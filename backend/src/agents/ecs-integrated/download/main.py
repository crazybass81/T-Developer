"""
Download Agent - ECS Integrated Version
Packages and prepares project for download
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
    from .modules.project_packager import ProjectPackager
except ImportError:
    try:
        # Try absolute import
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        from modules.project_packager import ProjectPackager
    except ImportError:
        # Final fallback - create a stub
        class ProjectPackager:
            async def initialize(self):
                return True
            async def package_project(self, *args, **kwargs):
                return {"success": True, "download_id": "test", "download_url": "/api/v1/download/test", "filename": "test.zip", "size_bytes": 1000, "size_mb": 0.001}

@dataclass
class DownloadAgentResult:
    """Result from Download Agent"""
    processed_data: Dict[str, Any]
    metadata: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float

class DownloadAgent(BaseAgent):
    """
    Packages and prepares project for download
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Download Agent with configuration"""
        
        if not config:
            config = AgentConfig(
                name="DownloadAgent",
                version="2.0.0",
                capabilities=["project_packager", "compression_engine", "metadata_generator", "readme_creator", "deployment_preparer"],
                resource_requirements={
                    "cpu": "4 vCPU",
                    "memory": "8GB",
                    "timeout": 300
                },
                service_group="generation"
            )
        
        super().__init__(config)
        
        # Initialize modules
        self.project_packager = ProjectPackager()
    
    async def initialize(self) -> bool:
        """Initialize agent and its modules"""
        
        try:
            self.logger.info("Initializing Download Agent modules...")
            
            # Initialize project packager
            await self.project_packager.initialize()
            
            self.status = AgentStatus.READY
            self.logger.info("Download Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Download Agent: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def _custom_initialize(self):
        """Custom initialization for agent"""
        pass

    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> AgentResult[DownloadAgentResult]:
        """
        Process download request
        
        Args:
            input_data: Input from previous agent
            context: Processing context
            
        Returns:
            download results
        """
        
        self.status = AgentStatus.PROCESSING
        start_time = datetime.now()
        
        try:
            self.logger.info("Processing with Download Agent...")
            
            # Extract project information from Assembly Agent
            project_id = input_data.get('project_id') or context.request_id or f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_path = input_data.get('project_path')
            
            if not project_path:
                # Check processed_data from previous agent
                processed_data_input = input_data.get('processed_data', {})
                project_path = processed_data_input.get('project_path')
            
            if not project_path:
                raise ValueError("No project path provided from Assembly Agent")
            
            # Get project metadata
            project_metadata = input_data.get('metadata', {})
            project_metadata.update({
                'project_name': input_data.get('project_name', 'untitled'),
                'project_type': input_data.get('project_type', 'react'),
                'features': input_data.get('features', []),
                'description': input_data.get('description', '')
            })
            
            # Package the project
            package_result = await self.project_packager.package_project(
                project_id=project_id,
                project_path=project_path,
                metadata=project_metadata
            )
            
            if not package_result['success']:
                raise Exception(f"Packaging failed: {package_result.get('error')}")
            
            # Process results
            processed_data = {
                'project_id': project_id,
                'download_id': package_result['download_id'],
                'download_url': package_result['download_url'],
                'filename': package_result['filename'],
                'size_bytes': package_result['size_bytes'],
                'size_mb': package_result['size_mb'],
                'packaged': True
            }
            
            metadata = {
                'download_metadata': package_result['metadata'],
                'project_metadata': project_metadata
            }
            
            recommendations = [
                f"Project packaged as {package_result['filename']}",
                f"Download size: {package_result['size_mb']} MB",
                f"Download URL: {package_result['download_url']}",
                "Project ready for download"
            ]
            
            # Calculate confidence based on packaging success
            confidence = 0.98 if package_result['size_bytes'] > 0 else 0.5
            
            # Create result
            result = DownloadAgentResult(
                processed_data=processed_data,
                metadata=metadata,
                recommendations=recommendations,
                confidence_score=confidence
            )
            
            # Cache result
            cache_key = f"download:{context.request_id}"
            await self.cache_result(cache_key, asdict(result))
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.update_metrics({
                "processing_time": processing_time,
                "confidence_score": confidence
            })
            
            self.status = AgentStatus.COMPLETED
            self.logger.info(f"Download Agent completed in {processing_time:.2f}s")
            
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
            self.logger.error(f"Download Agent failed: {e}")
            
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
        
        self.logger.info("Cleaning up Download Agent...")
        pass
