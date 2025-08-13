"""
🧬 T-Developer AI Analysis Prompts
Optimized prompts for Claude/GPT analysis <6.5KB
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PromptTemplate:
    """Prompt template with metadata"""

    name: str
    template: str
    max_tokens: int


class AnalysisPrompts:
    """Optimized AI analysis prompts"""

    def __init__(self):
        self.templates = {
            "code_analysis": PromptTemplate(
                name="code_analysis",
                template="""Analyze Python code for T-Developer:

{code}

CONSTRAINTS: <6.5KB, <3μs instantiation

Return JSON:
{{
  "capabilities": ["cap1", "cap2"],
  "memory_score": 8.5,
  "bottlenecks": ["issue1"],
  "suggestions": ["opt1", "opt2"],
  "classification": "processor|handler|manager"
}}""",
                max_tokens=400,
            ),
            "capability_extraction": PromptTemplate(
                name="capability_extraction",
                template="""Extract capabilities from:

{code}

Format: capability:confidence
Example:
api_requests:0.9
data_validation:0.7""",
                max_tokens=150,
            ),
            "memory_optimization": PromptTemplate(
                name="memory_optimization",
                template="""Optimize for 6.5KB ({size} bytes):

{code}

Provide:
1. Size reduction (max 3)
2. Code optimizations (max 3)""",
                max_tokens=200,
            ),
            "performance_analysis": PromptTemplate(
                name="performance_analysis",
                template="""Performance analysis for <3μs target:

{code}

JSON format:
{{
  "blockers": ["heavy_import"],
  "optimizations": ["lazy_loading"],
  "score": 7.2
}}""",
                max_tokens=200,
            ),
        }

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get prompt template"""
        return self.templates.get(name)

    def format_prompt(self, name: str, **kwargs) -> str:
        """Format prompt with variables"""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        return template.template.format(**kwargs)

    def get_analysis_prompt(self, code: str) -> str:
        """Get main analysis prompt"""
        return self.format_prompt("code_analysis", code=code)

    def get_capability_prompt(self, code: str) -> str:
        """Get capability extraction prompt"""
        return self.format_prompt("capability_extraction", code=code)

    def get_optimization_prompt(self, code: str, size: int) -> str:
        """Get optimization prompt"""
        return self.format_prompt("memory_optimization", code=code, size=size)

    def get_performance_prompt(self, code: str) -> str:
        """Get performance prompt"""
        return self.format_prompt("performance_analysis", code=code)


# Global instance and convenience functions
PROMPTS = AnalysisPrompts()


def analyze_code(code: str) -> str:
    """Get code analysis prompt"""
    return PROMPTS.get_analysis_prompt(code)


def extract_capabilities(code: str) -> str:
    """Get capability extraction prompt"""
    return PROMPTS.get_capability_prompt(code)


def optimize_memory(code: str, size: int) -> str:
    """Get memory optimization prompt"""
    return PROMPTS.get_optimization_prompt(code, size)


def analyze_performance(code: str) -> str:
    """Get performance analysis prompt"""
    return PROMPTS.get_performance_prompt(code)


def get_prompt(prompt_type: str, code: str, **kwargs) -> str:
    """Quick prompt selection"""
    prompt_map = {
        "analyze": analyze_code,
        "capabilities": extract_capabilities,
        "optimize": lambda c: optimize_memory(c, len(c.encode())),
        "performance": analyze_performance,
    }

    if prompt_type not in prompt_map:
        raise ValueError(f"Unknown prompt type: {prompt_type}")

    return prompt_map[prompt_type](code)
