#!/usr/bin/env python3
"""
Script to create remaining agents and their modules
Based on the established pattern from NL Input and UI Selection agents
"""

import os
import json
from pathlib import Path

# Define agent configurations
AGENTS = {
    "parser": {
        "name": "Parser Agent",
        "description": "Parses and structures project data",
        "modules": [
            "syntax_analyzer",
            "structure_extractor", 
            "dependency_resolver",
            "code_generator_config",
            "validation_engine"
        ],
        "service_group": "analysis"
    },
    "component_decision": {
        "name": "Component Decision Agent",
        "description": "Decides on component architecture",
        "modules": [
            "component_analyzer",
            "architecture_selector",
            "dependency_manager",
            "integration_planner",
            "optimization_advisor"
        ],
        "service_group": "decision"
    },
    "match_rate": {
        "name": "Match Rate Agent",
        "description": "Calculates template match rates",
        "modules": [
            "similarity_calculator",
            "feature_matcher",
            "gap_analyzer",
            "confidence_scorer",
            "recommendation_engine"
        ],
        "service_group": "decision"
    },
    "search": {
        "name": "Search Agent",
        "description": "Searches for existing components and solutions",
        "modules": [
            "code_searcher",
            "library_finder",
            "solution_matcher",
            "api_explorer",
            "documentation_finder"
        ],
        "service_group": "decision"
    },
    "generation": {
        "name": "Generation Agent",
        "description": "Generates project code and configurations",
        "modules": [
            "code_generator",
            "config_generator",
            "test_generator",
            "documentation_generator",
            "deployment_generator"
        ],
        "service_group": "generation"
    },
    "assembly": {
        "name": "Assembly Agent",
        "description": "Assembles generated components into complete project",
        "modules": [
            "project_structurer",
            "dependency_installer",
            "config_merger",
            "build_optimizer",
            "validation_runner"
        ],
        "service_group": "generation"
    },
    "download": {
        "name": "Download Agent",
        "description": "Packages and prepares project for download",
        "modules": [
            "project_packager",
            "compression_engine",
            "metadata_generator",
            "readme_creator",
            "deployment_preparer"
        ],
        "service_group": "generation"
    }
}

# Main agent template
MAIN_AGENT_TEMPLATE = '''"""
{name} - ECS Integrated Version
{description}
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

# Module imports
{module_imports}

@dataclass
class {class_name}Result:
    """Result from {name}"""
    processed_data: Dict[str, Any]
    metadata: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float

class {class_name}(BaseAgent):
    """
    {description}
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize {name} with configuration"""
        
        if not config:
            config = AgentConfig(
                name="{class_name}",
                version="2.0.0",
                capabilities={capabilities},
                resource_requirements={{
                    "cpu": "{cpu}",
                    "memory": "{memory}",
                    "timeout": 300
                }},
                service_group="{service_group}"
            )
        
        super().__init__(config)
        
        # Initialize modules
{module_init}
    
    async def initialize(self) -> bool:
        """Initialize agent and its modules"""
        
        try:
            self.logger.info("Initializing {name} modules...")
            
            # Initialize all modules
            await asyncio.gather(
{module_init_calls}
            )
            
            self.status = AgentStatus.READY
            self.logger.info("{name} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {name}: {{e}}")
            self.status = AgentStatus.ERROR
            return False
    
    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> AgentResult[{class_name}Result]:
        """
        Process {agent_type} request
        
        Args:
            input_data: Input from previous agent
            context: Processing context
            
        Returns:
            {agent_type} results
        """
        
        self.status = AgentStatus.PROCESSING
        start_time = datetime.now()
        
        try:
            # Process with modules
            processed_data = {{}}
            metadata = {{}}
            recommendations = []
            
            # TODO: Implement actual processing logic
            self.logger.info("Processing with {name}...")
            
            # Calculate confidence
            confidence = 0.85
            
            # Create result
            result = {class_name}Result(
                processed_data=processed_data,
                metadata=metadata,
                recommendations=recommendations,
                confidence_score=confidence
            )
            
            # Cache result
            cache_key = f"{cache_key}:{{context.request_id}}"
            await self.cache_result(cache_key, asdict(result))
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.update_metrics({{
                "processing_time": processing_time,
                "confidence_score": confidence
            }})
            
            self.status = AgentStatus.COMPLETED
            self.logger.info(f"{name} completed in {{processing_time:.2f}}s")
            
            return AgentResult(
                success=True,
                data=result,
                metadata={{
                    "processing_time": processing_time,
                    "confidence": confidence
                }}
            )
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"{name} failed: {{e}}")
            
            return AgentResult(
                success=False,
                data=None,
                error=str(e),
                metadata={{"error_type": type(e).__name__}}
            )
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        
        # TODO: Add specific validation logic
        return True
    
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        
        self.logger.info("Cleaning up {name}...")
        pass
'''

# Module template
MODULE_TEMPLATE = '''"""
{module_name} Module
{description}
"""

from typing import Dict, Any, List, Optional

class {class_name}:
    """{description}"""
    
    def __init__(self):
        """Initialize {module_name}"""
        pass
    
    async def initialize(self):
        """Initialize module resources"""
        pass
    
    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process {module_type} request
        
        Args:
            input_data: Input data
            context: Processing context
            
        Returns:
            Processed results
        """
        
        # TODO: Implement actual processing logic
        return {{
            "status": "processed",
            "data": input_data
        }}
'''

def create_agent_structure():
    """Create directory structure and files for all agents"""
    
    base_path = Path("/home/ec2-user/T-DeveloperMVP/backend/src/agents/ecs-integrated")
    
    for agent_key, agent_config in AGENTS.items():
        # Create agent directory
        agent_dir = base_path / agent_key
        modules_dir = agent_dir / "modules"
        modules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__ files
        (agent_dir / "__init__.py").write_text(f'"""{agent_config["name"]}"""')
        (modules_dir / "__init__.py").write_text(f'"""{agent_config["name"]} Modules"""')
        
        # Prepare template variables
        class_name = ''.join(word.capitalize() for word in agent_key.split('_')) + "Agent"
        
        # Module imports
        module_imports = '\n'.join([
            f'from .modules.{module} import {camel_case(module)}'
            for module in agent_config["modules"]
        ])
        
        # Module initialization
        module_init = '\n'.join([
            f'        self.{module} = {camel_case(module)}()'
            for module in agent_config["modules"]
        ])
        
        # Module init calls
        module_init_calls = ',\n'.join([
            f'                self.{module}.initialize()'
            for module in agent_config["modules"]
        ])
        
        # Determine resources based on service group
        if agent_config["service_group"] == "analysis":
            cpu, memory = "1 vCPU", "2GB"
        elif agent_config["service_group"] == "decision":
            cpu, memory = "2 vCPU", "4GB"
        else:  # generation
            cpu, memory = "4 vCPU", "8GB"
        
        # Generate main agent file
        main_content = MAIN_AGENT_TEMPLATE.format(
            name=agent_config["name"],
            description=agent_config["description"],
            class_name=class_name,
            module_imports=module_imports,
            capabilities=json.dumps(agent_config["modules"]),
            cpu=cpu,
            memory=memory,
            service_group=agent_config["service_group"],
            module_init=module_init,
            module_init_calls=module_init_calls,
            agent_type=agent_key,
            cache_key=agent_key
        )
        
        (agent_dir / "main.py").write_text(main_content)
        
        # Create module files
        for module in agent_config["modules"]:
            module_content = MODULE_TEMPLATE.format(
                module_name=module.replace('_', ' ').title(),
                description=f"Handles {module.replace('_', ' ')} for {agent_config['name']}",
                class_name=camel_case(module),
                module_type=module
            )
            
            (modules_dir / f"{module}.py").write_text(module_content)
        
        print(f"✅ Created {agent_config['name']} with {len(agent_config['modules'])} modules")

def camel_case(snake_str):
    """Convert snake_case to CamelCase"""
    components = snake_str.split('_')
    return ''.join(x.capitalize() for x in components)

if __name__ == "__main__":
    create_agent_structure()
    print("\n🎉 All agents created successfully!")