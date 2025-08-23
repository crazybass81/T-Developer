"""DeDup Checker for preventing duplicate agent development.

This module implements the DD-Gate (Duplicate Development Gate)
to check for existing agents with similar functionality.
"""

from __future__ import annotations

import difflib
from typing import Dict, List, Optional, Tuple

from ..agents.registry import AgentRegistry, AgentSpec as RegistrySpec
from ..memory import MemoryHub, ContextType
from .spec import AgentSpec


class DeDupChecker:
    """Duplicate development checker (DD-Gate).
    
    This component checks for existing agents with similar functionality
    to prevent duplicate development and encourage reuse.
    
    Attributes:
        registry: Agent registry to search
        memory_hub: Memory hub for historical data
        similarity_threshold: Threshold for considering agents similar (0.0-1.0)
    """
    
    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        memory_hub: Optional[MemoryHub] = None,
        similarity_threshold: float = 0.85
    ) -> None:
        """Initialize the DeDup Checker.
        
        Args:
            registry: Agent registry instance
            memory_hub: Memory hub instance
            similarity_threshold: Similarity threshold (0.85 = 85% similar)
        """
        self.registry = registry or AgentRegistry()
        self.memory_hub = memory_hub
        self.similarity_threshold = similarity_threshold
    
    async def check_duplicate(
        self,
        spec: AgentSpec,
        deep_check: bool = True
    ) -> Tuple[bool, List[Dict[str, any]]]:
        """Check if a similar agent already exists.
        
        Args:
            spec: The agent specification to check
            deep_check: Whether to perform deep similarity analysis
            
        Returns:
            Tuple of (is_duplicate, similar_agents)
            - is_duplicate: True if duplicate found above threshold
            - similar_agents: List of similar agents with similarity scores
        """
        similar_agents = []
        
        # Check against registered agents
        if self.registry:
            registry_results = self._check_registry(spec)
            similar_agents.extend(registry_results)
        
        # Check against memory if available
        if self.memory_hub and deep_check:
            memory_results = await self._check_memory(spec)
            similar_agents.extend(memory_results)
        
        # Sort by similarity score
        similar_agents.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Check if any exceed threshold
        is_duplicate = any(
            agent["similarity"] >= self.similarity_threshold
            for agent in similar_agents
        )
        
        return is_duplicate, similar_agents
    
    def _check_registry(self, spec: AgentSpec) -> List[Dict[str, any]]:
        """Check similarity against registered agents.
        
        Args:
            spec: The agent specification to check
            
        Returns:
            List of similar agents from registry
        """
        results = []
        
        # Get all registered agents
        registered_agents = self.registry.list_agents()
        
        for reg_spec in registered_agents:
            # Calculate similarity
            similarity = self._calculate_similarity(spec, reg_spec)
            
            if similarity > 0.5:  # Only include if >50% similar
                results.append({
                    "name": reg_spec.name,
                    "version": reg_spec.version,
                    "purpose": reg_spec.purpose,
                    "similarity": similarity,
                    "source": "registry",
                    "reusable": True,
                    "suggestion": self._generate_suggestion(spec, reg_spec, similarity)
                })
        
        return results
    
    async def _check_memory(self, spec: AgentSpec) -> List[Dict[str, any]]:
        """Check similarity against historical agents in memory.
        
        Args:
            spec: The agent specification to check
            
        Returns:
            List of similar agents from memory
        """
        if not self.memory_hub:
            return []
        
        results = []
        
        # Search for agent definitions in memory
        agent_memories = await self.memory_hub.search(
            ContextType.A_CTX,
            tags=["agent_definition", "agent_spec"],
            limit=50
        )
        
        for memory in agent_memories:
            if "value" in memory and isinstance(memory["value"], dict):
                mem_spec = memory["value"]
                
                # Calculate similarity based on available fields
                similarity = self._calculate_memory_similarity(spec, mem_spec)
                
                if similarity > 0.5:
                    results.append({
                        "name": mem_spec.get("name", "Unknown"),
                        "purpose": mem_spec.get("purpose", ""),
                        "similarity": similarity,
                        "source": "memory",
                        "reusable": False,  # Memory entries may not be fully implemented
                        "created_at": memory.get("created_at"),
                        "suggestion": f"Similar agent found in memory (created {memory.get('created_at', 'unknown')})"
                    })
        
        return results
    
    def _calculate_similarity(
        self,
        spec1: AgentSpec,
        spec2: RegistrySpec
    ) -> float:
        """Calculate similarity between two agent specifications.
        
        Uses multiple factors:
        - Purpose similarity (40%)
        - Input/output overlap (30%)
        - Capability match (20%)
        - Tag overlap (10%)
        
        Args:
            spec1: First agent specification
            spec2: Second agent specification
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        score = 0.0
        
        # Purpose similarity (40%)
        purpose_sim = self._text_similarity(spec1.purpose, spec2.purpose)
        score += purpose_sim * 0.4
        
        # Input overlap (15%)
        spec1_inputs = {inp.name for inp in spec1.inputs}
        spec2_inputs = set()  # Registry spec might not have detailed inputs
        if hasattr(spec2, 'inputs') and spec2.inputs:
            if isinstance(spec2.inputs, dict):
                spec2_inputs = set(spec2.inputs.keys())
            elif isinstance(spec2.inputs, list):
                spec2_inputs = set(spec2.inputs)
        
        if spec1_inputs and spec2_inputs:
            input_overlap = len(spec1_inputs & spec2_inputs) / max(len(spec1_inputs), len(spec2_inputs))
            score += input_overlap * 0.15
        
        # Output overlap (15%)
        spec1_outputs = {out.name for out in spec1.outputs}
        spec2_outputs = set()
        if hasattr(spec2, 'outputs') and spec2.outputs:
            if isinstance(spec2.outputs, dict):
                spec2_outputs = set(spec2.outputs.keys())
            elif isinstance(spec2.outputs, list):
                spec2_outputs = set(spec2.outputs)
        
        if spec1_outputs and spec2_outputs:
            output_overlap = len(spec1_outputs & spec2_outputs) / max(len(spec1_outputs), len(spec2_outputs))
            score += output_overlap * 0.15
        
        # Capability match (20%)
        # For registry spec, try to infer capability from purpose/tags
        if hasattr(spec2, 'tags') and spec2.tags:
            if spec1.capability.value in ' '.join(spec2.tags).lower():
                score += 0.2
        
        # Tag overlap (10%)
        if spec1.tags and hasattr(spec2, 'tags') and spec2.tags:
            tag_overlap = len(set(spec1.tags) & set(spec2.tags)) / max(len(spec1.tags), len(spec2.tags))
            score += tag_overlap * 0.1
        
        return min(score, 1.0)
    
    def _calculate_memory_similarity(
        self,
        spec: AgentSpec,
        memory_spec: Dict
    ) -> float:
        """Calculate similarity for a memory-stored specification.
        
        Args:
            spec: Agent specification
            memory_spec: Dictionary from memory
            
        Returns:
            Similarity score
        """
        score = 0.0
        
        # Purpose similarity (50% weight for memory)
        if "purpose" in memory_spec:
            purpose_sim = self._text_similarity(spec.purpose, memory_spec["purpose"])
            score += purpose_sim * 0.5
        
        # Name similarity (20%)
        if "name" in memory_spec:
            name_sim = self._text_similarity(spec.name, memory_spec["name"])
            score += name_sim * 0.2
        
        # Capability match (20%)
        if "capability" in memory_spec:
            if spec.capability.value == memory_spec["capability"]:
                score += 0.2
        
        # Tag overlap (10%)
        if "tags" in memory_spec and spec.tags:
            memory_tags = memory_spec["tags"] if isinstance(memory_spec["tags"], list) else []
            if memory_tags:
                tag_overlap = len(set(spec.tags) & set(memory_tags)) / max(len(spec.tags), len(memory_tags))
                score += tag_overlap * 0.1
        
        return min(score, 1.0)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using sequence matching.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # Use SequenceMatcher for similarity
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def _generate_suggestion(
        self,
        new_spec: AgentSpec,
        existing_spec: RegistrySpec,
        similarity: float
    ) -> str:
        """Generate a suggestion for handling the duplicate.
        
        Args:
            new_spec: The new agent specification
            existing_spec: The existing similar agent
            similarity: Similarity score
            
        Returns:
            Suggestion string
        """
        if similarity >= 0.95:
            return f"Use existing agent '{existing_spec.name}' directly - almost identical"
        elif similarity >= 0.85:
            return f"Extend existing agent '{existing_spec.name}' with new features"
        elif similarity >= 0.70:
            return f"Consider refactoring '{existing_spec.name}' to support both use cases"
        else:
            return f"Review '{existing_spec.name}' for reusable components"
    
    async def find_reusable_components(
        self,
        spec: AgentSpec
    ) -> List[Dict[str, any]]:
        """Find reusable components for the new agent.
        
        Args:
            spec: The agent specification
            
        Returns:
            List of reusable components
        """
        components = []
        
        # Search for similar capabilities
        if self.registry:
            agents = self.registry.search(
                purpose_keywords=spec.purpose.split()[:5]  # Use first 5 words
            )
            
            for agent in agents:
                components.append({
                    "type": "agent",
                    "name": agent.name,
                    "purpose": agent.purpose,
                    "reuse_type": "direct" if agent.purpose == spec.purpose else "partial"
                })
        
        # Search for templates and patterns in memory
        if self.memory_hub:
            templates = await self.memory_hub.search(
                ContextType.S_CTX,
                tags=["template", "pattern", spec.capability.value],
                limit=10
            )
            
            for template in templates:
                components.append({
                    "type": "template",
                    "name": template.get("key", "Unknown"),
                    "value": template.get("value"),
                    "reuse_type": "template"
                })
        
        return components