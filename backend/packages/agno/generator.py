"""Code Generator for creating agent implementations.

This module uses Claude (via AWS Bedrock) to generate agent code
based on specifications created by Agno.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..agents.ai_providers import BedrockAIProvider
from ..memory import MemoryHub, ContextType
from .spec import AgentSpec


class CodeGenerator:
    """Generate agent code from specifications using AI.
    
    This is the "Claude Code" component that takes an AgentSpec
    and generates actual implementation code.
    
    Attributes:
        ai_provider: AI provider for code generation
        memory_hub: Memory hub for storing patterns
        template_path: Path to code templates
    """
    
    def __init__(
        self,
        ai_provider: Optional[BedrockAIProvider] = None,
        memory_hub: Optional[MemoryHub] = None,
        template_path: Optional[Path] = None
    ) -> None:
        """Initialize the Code Generator.
        
        Args:
            ai_provider: AI provider (defaults to Bedrock with Claude)
            memory_hub: Memory hub for patterns
            template_path: Path to templates directory
        """
        self.ai_provider = ai_provider or BedrockAIProvider(model="claude-3-haiku")
        self.memory_hub = memory_hub
        self.template_path = template_path or Path(__file__).parent / "templates"
    
    async def generate_agent(
        self,
        spec: AgentSpec,
        use_patterns: bool = True
    ) -> Dict[str, str]:
        """Generate complete agent implementation from specification.
        
        Args:
            spec: Agent specification
            use_patterns: Whether to use learned patterns from memory
            
        Returns:
            Dictionary with generated files:
            - "agent.py": Main agent implementation
            - "test_agent.py": Test suite
            - "README.md": Documentation
        """
        # Gather context
        context = await self._gather_context(spec, use_patterns)
        
        # Generate agent code
        agent_code = await self._generate_agent_code(spec, context)
        
        # Generate test code
        test_code = await self._generate_test_code(spec, agent_code)
        
        # Generate documentation
        documentation = await self._generate_documentation(spec)
        
        # Store successful pattern if memory available
        if self.memory_hub:
            await self._store_pattern(spec, agent_code)
        
        return {
            f"{spec.name.lower()}_agent.py": agent_code,
            f"test_{spec.name.lower()}_agent.py": test_code,
            f"{spec.name}_README.md": documentation
        }
    
    async def _gather_context(
        self,
        spec: AgentSpec,
        use_patterns: bool
    ) -> Dict[str, any]:
        """Gather context for code generation.
        
        Args:
            spec: Agent specification
            use_patterns: Whether to use patterns from memory
            
        Returns:
            Context dictionary
        """
        context = {
            "base_agent_path": "backend.packages.agents.base",
            "memory_hub_path": "backend.packages.memory",
            "patterns": [],
            "similar_agents": []
        }
        
        if use_patterns and self.memory_hub:
            # Search for similar patterns
            patterns = await self.memory_hub.search(
                ContextType.A_CTX,
                tags=["code_pattern", spec.capability.value],
                limit=5
            )
            context["patterns"] = patterns
            
            # Search for similar agent implementations
            similar = await self.memory_hub.search(
                ContextType.S_CTX,
                tags=["agent_implementation", spec.capability.value],
                limit=3
            )
            context["similar_agents"] = similar
        
        return context
    
    async def _generate_agent_code(
        self,
        spec: AgentSpec,
        context: Dict
    ) -> str:
        """Generate the main agent implementation code.
        
        Args:
            spec: Agent specification
            context: Generation context
            
        Returns:
            Python code for the agent
        """
        # Build the generation prompt
        prompt = self._build_generation_prompt(spec, context)
        
        # System prompt for code generation
        system_prompt = """You are an expert Python developer specializing in agent-based systems.
Generate clean, production-ready code following these principles:
1. SOLID principles
2. Type hints for all functions
3. Comprehensive docstrings
4. Error handling
5. Async/await patterns
6. Memory Hub integration
7. Proper logging

The code should extend BaseAgent and implement all required methods.
Return ONLY the Python code without any explanation."""
        
        # Generate code using AI
        code = await self.ai_provider.complete(
            prompt=prompt,
            system=system_prompt,
            max_tokens=4096,
            temperature=0.3  # Lower temperature for more consistent code
        )
        
        # Clean up the generated code
        code = self._clean_generated_code(code)
        
        return code
    
    def _build_generation_prompt(self, spec: AgentSpec, context: Dict) -> str:
        """Build the prompt for code generation.
        
        Args:
            spec: Agent specification
            context: Generation context
            
        Returns:
            Prompt string
        """
        # Convert spec to readable format
        spec_yaml = spec.to_yaml()
        
        # Build prompt parts
        prompt_parts = [
            f"Generate a Python agent implementation based on this specification:",
            "",
            "=== SPECIFICATION ===",
            spec_yaml,
            "",
            "=== REQUIREMENTS ===",
            f"1. Agent name: {spec.name}Agent",
            f"2. Inherits from: BaseAgent",
            f"3. Main capability: {spec.capability.value}",
            f"4. Must implement execute() method",
            f"5. Must validate inputs according to spec",
            f"6. Must use Memory Hub for contexts: {', '.join([m.value for m in spec.memory_read])}",
            f"7. Must write to contexts: {', '.join([m.value for m in spec.memory_write])}",
            ""
        ]
        
        # Add input/output details
        prompt_parts.extend([
            "=== INPUTS ===",
        ])
        for inp in spec.inputs:
            prompt_parts.append(f"- {inp.name} ({inp.type}): {inp.description}")
        
        prompt_parts.extend([
            "",
            "=== OUTPUTS ===",
        ])
        for out in spec.outputs:
            prompt_parts.append(f"- {out.name} ({out.type}): {out.description}")
        
        # Add pattern examples if available
        if context.get("patterns"):
            prompt_parts.extend([
                "",
                "=== SIMILAR PATTERNS (for reference) ===",
                "Use these patterns where appropriate:",
            ])
            for pattern in context["patterns"][:2]:
                if "value" in pattern and "code" in pattern["value"]:
                    prompt_parts.append(f"Pattern: {pattern.get('key', 'Unknown')}")
        
        # Add import requirements
        prompt_parts.extend([
            "",
            "=== REQUIRED IMPORTS ===",
            "from __future__ import annotations",
            "import asyncio",
            "from typing import Dict, Any, List, Optional",
            f"from {context['base_agent_path']} import BaseAgent, AgentTask, AgentResult",
            f"from {context['memory_hub_path']} import ContextType",
            "",
            "Generate the complete agent class implementation."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _generate_test_code(
        self,
        spec: AgentSpec,
        agent_code: str
    ) -> str:
        """Generate test suite for the agent.
        
        Args:
            spec: Agent specification
            agent_code: Generated agent code
            
        Returns:
            Python test code
        """
        prompt = f"""Generate a comprehensive test suite for this agent:

Agent Name: {spec.name}Agent
Purpose: {spec.purpose}

Key test cases needed:
1. Test successful execution with valid inputs
2. Test input validation
3. Test error handling
4. Test memory read/write operations
5. Test timeout handling
6. Test retry logic

Agent specification inputs:
{[f"- {inp.name} ({inp.type}): {inp.description}" for inp in spec.inputs]}

Agent specification outputs:
{[f"- {out.name} ({out.type}): {out.description}" for out in spec.outputs]}

Generate pytest test code with async tests, fixtures, and proper mocking.
Include at least 5 test cases covering different scenarios.
Return ONLY the Python test code."""
        
        system_prompt = """You are an expert at writing comprehensive test suites.
Generate clean pytest code with:
1. Proper fixtures
2. Async test functions
3. Mock objects for dependencies
4. Parametrized tests where appropriate
5. Clear test names and docstrings"""
        
        test_code = await self.ai_provider.complete(
            prompt=prompt,
            system=system_prompt,
            max_tokens=4096,
            temperature=0.3
        )
        
        return self._clean_generated_code(test_code)
    
    async def _generate_documentation(self, spec: AgentSpec) -> str:
        """Generate README documentation for the agent.
        
        Args:
            spec: Agent specification
            
        Returns:
            Markdown documentation
        """
        prompt = f"""Generate comprehensive README.md documentation for this agent:

Agent: {spec.name}Agent
Version: {spec.version}
Purpose: {spec.purpose}
Capability: {spec.capability.value}

Inputs: {[f"{inp.name} ({inp.type})" for inp in spec.inputs]}
Outputs: {[f"{out.name} ({out.type})" for out in spec.outputs]}

Memory Access:
- Read: {[m.value for m in spec.memory_read]}
- Write: {[m.value for m in spec.memory_write]}

Policies:
- AI First: {spec.policies.ai_first}
- DeDup Required: {spec.policies.dedup_required}
- Timeout: {spec.policies.timeout_seconds}s

Generate a complete README with:
1. Overview
2. Installation
3. Usage examples
4. API reference
5. Configuration
6. Testing
7. Contributing

Return ONLY the markdown content."""
        
        documentation = await self.ai_provider.complete(
            prompt=prompt,
            system="You are a technical writer creating clear, comprehensive documentation.",
            max_tokens=2048,
            temperature=0.5
        )
        
        return documentation
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean up generated code.
        
        Args:
            code: Raw generated code
            
        Returns:
            Cleaned code
        """
        # Remove markdown code blocks if present
        if "```python" in code:
            start = code.find("```python") + 9
            end = code.find("```", start)
            code = code[start:end].strip()
        elif "```" in code:
            start = code.find("```") + 3
            end = code.find("```", start)
            code = code[start:end].strip()
        
        return code.strip()
    
    async def _store_pattern(
        self,
        spec: AgentSpec,
        code: str
    ) -> None:
        """Store successful code pattern in memory.
        
        Args:
            spec: Agent specification
            code: Generated code
        """
        if not self.memory_hub:
            return
        
        # Store in agent context
        await self.memory_hub.put(
            ContextType.A_CTX,
            f"pattern_{spec.name}_{spec.capability.value}",
            {
                "spec": spec.to_yaml(),
                "code": code,
                "capability": spec.capability.value,
                "success": True
            },
            ttl_seconds=86400 * 30,  # Keep for 30 days
            tags=["code_pattern", spec.capability.value, "agno_generated"]
        )
        
        # Store summary in shared context
        await self.memory_hub.put(
            ContextType.S_CTX,
            f"latest_generation_{spec.name}",
            {
                "agent": spec.name,
                "capability": spec.capability.value,
                "purpose": spec.purpose,
                "generated": True
            },
            ttl_seconds=3600,  # Keep for 1 hour
            tags=["agent_implementation", spec.capability.value]
        )
    
    async def validate_generated_code(
        self,
        code: str,
        spec: AgentSpec
    ) -> Tuple[bool, List[str]]:
        """Validate generated code against specification.
        
        Args:
            code: Generated Python code
            spec: Agent specification
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        # Check for required class name
        expected_class = f"{spec.name}Agent"
        if f"class {expected_class}" not in code:
            errors.append(f"Missing expected class name: {expected_class}")
        
        # Check for execute method
        if "async def execute" not in code:
            errors.append("Missing async execute method")
        
        # Check for required imports
        if "from" not in code or "import" not in code:
            errors.append("Missing import statements")
        
        # Check for BaseAgent inheritance
        if "BaseAgent" not in code:
            errors.append("Not inheriting from BaseAgent")
        
        # Use AI to validate logic
        if not errors:
            validation_prompt = f"""Analyze this generated Python code for correctness:

{code}

Check for:
1. Syntax errors
2. Logic errors
3. Missing error handling
4. Incorrect async usage
5. Memory Hub usage issues

Return a JSON object with:
{{"valid": true/false, "errors": ["error1", "error2"]}}"""
            
            try:
                result = await self.ai_provider.complete(
                    prompt=validation_prompt,
                    system="You are a Python code reviewer. Return only valid JSON.",
                    max_tokens=1024,
                    temperature=0.1
                )
                
                # Parse result
                if "{" in result and "}" in result:
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    json_str = result[start:end]
                    validation = json.loads(json_str)
                    
                    if not validation.get("valid", True):
                        errors.extend(validation.get("errors", []))
            except Exception as e:
                errors.append(f"Validation check failed: {str(e)}")
        
        return len(errors) == 0, errors