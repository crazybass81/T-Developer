"""Agno Manager - The core agent definition and design manager.

This is the main entry point for creating new agents in the T-Developer system.
Agno handles the complete lifecycle from requirements to deployed agents.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..agents.registry import AgentRegistry
from ..memory import MemoryHub, ContextType
from .dedup import DeDupChecker
from .generator import CodeGenerator
from .spec import (
    AgentSpec,
    AgentInputSchema,
    AgentOutputSchema,
    AgentPolicy,
    AgentCapability,
    MemoryAccess
)


class AgnoManager:
    """Agent Definition and Design Manager.
    
    Agno is responsible for the complete agent creation lifecycle:
    1. Analyzing requirements
    2. Checking for duplicates (DD-Gate)
    3. Creating agent specifications
    4. Requesting implementation from Claude
    5. Validating and registering agents
    
    This implements the Agno component from the architecture documentation.
    
    Attributes:
        memory_hub: Memory Hub for context storage
        registry: Agent Registry for tracking agents
        dedup_checker: DD-Gate implementation
        code_generator: Claude Code generator
        specs_path: Path to store agent specifications
    """
    
    def __init__(
        self,
        memory_hub: Optional[MemoryHub] = None,
        registry: Optional[AgentRegistry] = None,
        specs_path: Optional[Path] = None
    ) -> None:
        """Initialize Agno Manager.
        
        Args:
            memory_hub: Memory Hub instance
            registry: Agent Registry instance
            specs_path: Path to store specifications
        """
        self.memory_hub = memory_hub or MemoryHub()
        self.registry = registry or AgentRegistry()
        self.dedup_checker = DeDupChecker(registry, memory_hub)
        self.code_generator = CodeGenerator(memory_hub=memory_hub)
        self.specs_path = specs_path or Path("/tmp/t-developer/specs")
        self.specs_path.mkdir(parents=True, exist_ok=True)
    
    async def create_agent(
        self,
        requirements: Dict[str, Any],
        auto_implement: bool = True,
        force_create: bool = False
    ) -> Dict[str, Any]:
        """Create a new agent from requirements.
        
        This is the main entry point for agent creation.
        
        Args:
            requirements: Agent requirements including:
                - name: Agent name
                - purpose: What the agent does
                - inputs: Expected inputs
                - outputs: Expected outputs
                - capabilities: What it can do
            auto_implement: Whether to automatically generate code
            force_create: Skip duplicate check (requires ADR)
            
        Returns:
            Dictionary containing:
                - spec: The agent specification
                - duplicate_check: Duplicate check results
                - implementation: Generated code (if auto_implement)
                - registration: Registration status
        """
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "requirements": requirements
        }
        
        # Step 1: Analyze requirements and create spec
        spec = await self._analyze_requirements(requirements)
        result["spec"] = spec.to_yaml()
        
        # Step 2: Check for duplicates (DD-Gate)
        if not force_create:
            is_duplicate, similar_agents = await self.dedup_checker.check_duplicate(spec)
            result["duplicate_check"] = {
                "is_duplicate": is_duplicate,
                "similar_agents": similar_agents[:5]  # Top 5 similar
            }
            
            if is_duplicate:
                result["status"] = "duplicate_found"
                result["suggestion"] = similar_agents[0]["suggestion"] if similar_agents else "Use existing agent"
                
                # Store in memory for learning
                await self._store_duplicate_attempt(spec, similar_agents)
                
                return result
        else:
            result["duplicate_check"] = {"skipped": True, "reason": "force_create=True"}
        
        # Step 3: Find reusable components
        reusable = await self.dedup_checker.find_reusable_components(spec)
        result["reusable_components"] = reusable
        
        # Step 4: Save specification
        spec_path = self.specs_path / f"{spec.name}_v{spec.version}.yaml"
        spec.save_to_file(spec_path)
        result["spec_path"] = str(spec_path)
        
        # Step 5: Auto-implement if requested
        if auto_implement:
            implementation = await self._implement_agent(spec, reusable)
            result["implementation"] = implementation
            
            # Validate generated code
            if "agent.py" in implementation:
                is_valid, errors = await self.code_generator.validate_generated_code(
                    implementation["agent.py"],
                    spec
                )
                result["validation"] = {
                    "valid": is_valid,
                    "errors": errors
                }
        
        # Step 6: Register agent
        registration = await self._register_agent(spec)
        result["registration"] = registration
        
        # Step 7: Store in memory for future reference
        await self._store_agent_creation(spec, result)
        
        result["status"] = "created"
        return result
    
    async def _analyze_requirements(
        self,
        requirements: Dict[str, Any]
    ) -> AgentSpec:
        """Analyze requirements and create agent specification.
        
        Args:
            requirements: Raw requirements dictionary
            
        Returns:
            Complete agent specification
        """
        # Extract basic information
        name = requirements.get("name", "UnnamedAgent")
        purpose = requirements.get("purpose", "")
        version = requirements.get("version", "1.0.0")
        
        # Determine capability
        capability_str = requirements.get("capability", "analyze").lower()
        capability = AgentCapability.ANALYZE  # Default
        for cap in AgentCapability:
            if cap.value in capability_str:
                capability = cap
                break
        
        # Parse inputs
        inputs = []
        for inp in requirements.get("inputs", []):
            if isinstance(inp, dict):
                inputs.append(AgentInputSchema(
                    name=inp.get("name", "input"),
                    type=inp.get("type", "string"),
                    required=inp.get("required", True),
                    description=inp.get("description", "")
                ))
            elif isinstance(inp, str):
                # Simple string input
                inputs.append(AgentInputSchema(
                    name=inp,
                    type="string",
                    required=True,
                    description=f"{inp} input"
                ))
        
        # Parse outputs
        outputs = []
        for out in requirements.get("outputs", []):
            if isinstance(out, dict):
                outputs.append(AgentOutputSchema(
                    name=out.get("name", "output"),
                    type=out.get("type", "dict"),
                    description=out.get("description", "")
                ))
            elif isinstance(out, str):
                outputs.append(AgentOutputSchema(
                    name=out,
                    type="dict",
                    description=f"{out} output"
                ))
        
        # Parse policies
        policy_dict = requirements.get("policies", {})
        policies = AgentPolicy(
            ai_first=policy_dict.get("ai_first", True),
            dedup_required=policy_dict.get("dedup_required", True),
            pii_allowed=policy_dict.get("pii_allowed", False),
            timeout_seconds=policy_dict.get("timeout_seconds", 300)
        )
        
        # Parse memory access
        memory = requirements.get("memory", {})
        memory_read = [
            MemoryAccess(ctx) for ctx in memory.get("read", ["S_CTX"])
        ]
        memory_write = [
            MemoryAccess(ctx) for ctx in memory.get("write", ["A_CTX", "S_CTX"])
        ]
        
        # Create specification
        spec = AgentSpec(
            name=name,
            version=version,
            purpose=purpose,
            capability=capability,
            inputs=inputs,
            outputs=outputs,
            policies=policies,
            memory_read=memory_read,
            memory_write=memory_write,
            dependencies=requirements.get("dependencies", []),
            tools=requirements.get("tools", []),
            tests=requirements.get("tests", []),
            tags=requirements.get("tags", [capability.value, "agno_created"])
        )
        
        # Validate specification
        errors = spec.validate()
        if errors:
            # Try to fix common issues
            if "purpose is required" in errors and not purpose:
                spec.purpose = f"Agent for {capability.value} operations"
            if "At least one input is required" in errors and not inputs:
                spec.inputs = [AgentInputSchema(
                    name="data",
                    type="dict",
                    required=True,
                    description="Input data"
                )]
            if "At least one output is required" in errors and not outputs:
                spec.outputs = [AgentOutputSchema(
                    name="result",
                    type="dict",
                    description="Operation result"
                )]
        
        return spec
    
    async def _implement_agent(
        self,
        spec: AgentSpec,
        reusable_components: List[Dict]
    ) -> Dict[str, str]:
        """Request implementation from Claude Code.
        
        Args:
            spec: Agent specification
            reusable_components: Components that can be reused
            
        Returns:
            Dictionary with generated files
        """
        # Generate implementation
        implementation = await self.code_generator.generate_agent(
            spec,
            use_patterns=True
        )
        
        # Add reusable component information to documentation
        if reusable_components and f"{spec.name}_README.md" in implementation:
            readme = implementation[f"{spec.name}_README.md"]
            readme += "\n\n## Reusable Components\n\n"
            for component in reusable_components[:5]:
                readme += f"- **{component['name']}**: {component.get('purpose', 'N/A')} (Type: {component['type']})\n"
            implementation[f"{spec.name}_README.md"] = readme
        
        return implementation
    
    async def _register_agent(self, spec: AgentSpec) -> Dict[str, Any]:
        """Register agent in the registry.
        
        Args:
            spec: Agent specification
            
        Returns:
            Registration result
        """
        try:
            # Convert to registry format
            registry_spec = {
                "name": spec.name,
                "version": spec.version,
                "purpose": spec.purpose,
                "inputs": {inp.name: inp.type for inp in spec.inputs},
                "outputs": {out.name: out.type for out in spec.outputs},
                "policies": spec.policies.dict(),
                "memory": {
                    "read": [m.value for m in spec.memory_read],
                    "write": [m.value for m in spec.memory_write]
                },
                "owner": "agno",
                "tags": spec.tags
            }
            
            # Register (registry expects a different format)
            from ..agents.registry import AgentSpec as RegistrySpec
            reg_spec = RegistrySpec(**registry_spec)
            
            success = self.registry.register(
                None,  # No class yet
                reg_spec,
                None   # No instance yet
            )
            
            return {
                "registered": success,
                "registry_name": spec.name,
                "version": spec.version
            }
            
        except Exception as e:
            return {
                "registered": False,
                "error": str(e)
            }
    
    async def _store_duplicate_attempt(
        self,
        spec: AgentSpec,
        similar_agents: List[Dict]
    ) -> None:
        """Store duplicate attempt for learning.
        
        Args:
            spec: The attempted specification
            similar_agents: List of similar existing agents
        """
        if not self.memory_hub:
            return
        
        await self.memory_hub.put(
            ContextType.A_CTX,
            f"duplicate_attempt_{spec.name}_{datetime.utcnow().timestamp()}",
            {
                "attempted_spec": spec.to_yaml(),
                "similar_agents": similar_agents[:3],
                "timestamp": datetime.utcnow().isoformat()
            },
            ttl_seconds=86400 * 7,  # Keep for 7 days
            tags=["duplicate_attempt", "learning", spec.capability.value]
        )
    
    async def _store_agent_creation(
        self,
        spec: AgentSpec,
        result: Dict[str, Any]
    ) -> None:
        """Store successful agent creation for future reference.
        
        Args:
            spec: The agent specification
            result: Creation result
        """
        if not self.memory_hub:
            return
        
        # Store in agent context
        await self.memory_hub.put(
            ContextType.A_CTX,
            f"agent_creation_{spec.name}_{spec.version}",
            {
                "spec": spec.to_yaml(),
                "result": {
                    "status": result.get("status"),
                    "validation": result.get("validation"),
                    "registration": result.get("registration")
                },
                "timestamp": result.get("timestamp")
            },
            ttl_seconds=86400 * 30,  # Keep for 30 days
            tags=["agent_creation", spec.capability.value, "agno"]
        )
        
        # Store summary in shared context
        await self.memory_hub.put(
            ContextType.S_CTX,
            f"latest_agent_{spec.name}",
            {
                "name": spec.name,
                "version": spec.version,
                "purpose": spec.purpose,
                "capability": spec.capability.value,
                "created": result.get("timestamp")
            },
            ttl_seconds=3600 * 24,  # Keep for 24 hours
            tags=["latest_agent", "agno"]
        )
    
    async def list_specifications(self) -> List[Dict[str, Any]]:
        """List all agent specifications.
        
        Returns:
            List of specification summaries
        """
        specs = []
        
        # Read from specs directory
        for spec_file in self.specs_path.glob("*.yaml"):
            try:
                spec = AgentSpec.load_from_file(spec_file)
                specs.append({
                    "name": spec.name,
                    "version": spec.version,
                    "purpose": spec.purpose,
                    "capability": spec.capability.value,
                    "file": str(spec_file)
                })
            except Exception as e:
                # Skip invalid files
                continue
        
        return specs
    
    async def get_agent_spec(self, name: str, version: Optional[str] = None) -> Optional[AgentSpec]:
        """Get a specific agent specification.
        
        Args:
            name: Agent name
            version: Optional version (latest if not specified)
            
        Returns:
            Agent specification or None if not found
        """
        if version:
            spec_file = self.specs_path / f"{name}_v{version}.yaml"
            if spec_file.exists():
                return AgentSpec.load_from_file(spec_file)
        else:
            # Find latest version
            pattern = f"{name}_v*.yaml"
            files = sorted(self.specs_path.glob(pattern))
            if files:
                return AgentSpec.load_from_file(files[-1])
        
        return None