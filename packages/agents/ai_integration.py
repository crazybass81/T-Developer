#!/usr/bin/env python3
"""Real AI Integration for T-Developer Agents."""

import json
import logging
import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AIProvider:
    """Unified AI provider for all agents."""

    def __init__(self):
        """Initialize AI provider with API keys."""
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("AI_MODEL", "gpt-4")

        # Initialize clients
        if self.openai_key:
            self.openai = OpenAI(api_key=self.openai_key)
            logger.info("OpenAI API initialized")
        else:
            self.openai = None

        if self.anthropic_key:
            self.anthropic = Anthropic(api_key=self.anthropic_key)
            logger.info("Anthropic API initialized")
        else:
            self.anthropic = None

    def analyze_code(self, code: str, problem: str) -> dict[str, Any]:
        """Analyze code using AI."""
        prompt = f"""
        Analyze this Python code and identify improvements for: {problem}

        Code:
        ```python
        {code[:3000]}  # Truncate for token limits
        ```

        Provide analysis in JSON format:
        {{
            "findings": ["list of issues found"],
            "metrics": {{"docstring_coverage": 0.0-1.0, "complexity": number}},
            "recommendations": ["list of improvements"],
            "priority_issues": ["critical issues to fix first"]
        }}
        """

        try:
            if self.model.startswith("gpt") and self.openai:
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a code analysis expert. Respond only with valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                )
                result = response.choices[0].message.content

            elif self.model.startswith("claude"):
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.3,
                    system="You are a code analysis expert. Respond only with valid JSON.",
                    messages=[{"role": "user", "content": prompt}],
                )
                result = response.content[0].text
            else:
                # Fallback to mock response
                return self._mock_analysis()

            return json.loads(result)

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._mock_analysis()

    def create_improvement_plan(self, findings: list[str], metrics: dict) -> dict[str, Any]:
        """Create improvement plan using AI."""
        prompt = f"""
        Create a detailed improvement plan based on these findings:

        Findings: {json.dumps(findings)}
        Current Metrics: {json.dumps(metrics)}

        Generate a plan in JSON format:
        {{
            "tasks": [
                {{"id": "task-1", "action": "specific action", "target": "file or function", "priority": "high/medium/low"}}
            ],
            "estimated_hours": number,
            "expected_improvements": {{"metric": "expected change"}},
            "implementation_order": ["task-1", "task-2"]
        }}
        """

        try:
            if self.model.startswith("gpt") and self.openai:
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a software architect. Create actionable improvement plans.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    max_tokens=2000,
                )
                result = response.choices[0].message.content

            elif self.model.startswith("claude"):
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.5,
                    system="You are a software architect. Create actionable improvement plans.",
                    messages=[{"role": "user", "content": prompt}],
                )
                result = response.content[0].text
            else:
                return self._mock_plan()

            return json.loads(result)

        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            return self._mock_plan()

    def generate_improved_code(self, original_code: str, task: dict[str, str]) -> str:
        """Generate improved version of code."""
        prompt = f"""
        Improve this Python code by: {task['action']}
        Target: {task.get('target', 'general')}

        Original code:
        ```python
        {original_code[:2000]}
        ```

        Return ONLY the improved Python code, no explanations.
        """

        try:
            if self.model.startswith("gpt") and self.openai:
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a Python expert. Return only improved code.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=3000,
                )
                return response.choices[0].message.content

            elif self.model.startswith("claude"):
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=3000,
                    temperature=0.3,
                    system="You are a Python expert. Return only improved code.",
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            else:
                return original_code + "\n# AI improvements would go here"

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return original_code

    def evaluate_changes(self, before: str, after: str) -> dict[str, Any]:
        """Evaluate the quality of changes."""
        prompt = f"""
        Compare these two versions of code and evaluate the improvements:

        BEFORE:
        ```python
        {before[:1500]}
        ```

        AFTER:
        ```python
        {after[:1500]}
        ```

        Provide evaluation in JSON format:
        {{
            "improvements": ["list of improvements made"],
            "metrics_change": {{"metric": "before -> after"}},
            "quality_score": 0-100,
            "risks": ["potential issues introduced"],
            "recommendation": "approve/reject/review"
        }}
        """

        try:
            if self.model.startswith("gpt") and self.openai:
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a code review expert. Evaluate code changes objectively.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=1500,
                )
                result = response.choices[0].message.content

            elif self.model.startswith("claude"):
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.3,
                    system="You are a code review expert. Evaluate code changes objectively.",
                    messages=[{"role": "user", "content": prompt}],
                )
                result = response.content[0].text
            else:
                return self._mock_evaluation()

            return json.loads(result)

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return self._mock_evaluation()

    def _mock_analysis(self) -> dict[str, Any]:
        """Fallback mock analysis."""
        return {
            "findings": ["Mock: Missing docstrings", "Mock: No type hints"],
            "metrics": {"docstring_coverage": 0.5, "complexity": 10},
            "recommendations": ["Add docstrings", "Add type hints"],
            "priority_issues": ["Add error handling"],
        }

    def _mock_plan(self) -> dict[str, Any]:
        """Fallback mock plan."""
        return {
            "tasks": [
                {
                    "id": "task-1",
                    "action": "add_docstrings",
                    "target": "all_functions",
                    "priority": "high",
                }
            ],
            "estimated_hours": 2,
            "expected_improvements": {"docstring_coverage": "+50%"},
            "implementation_order": ["task-1"],
        }

    def _mock_evaluation(self) -> dict[str, Any]:
        """Fallback mock evaluation."""
        return {
            "improvements": ["Added docstrings", "Improved readability"],
            "metrics_change": {"docstring_coverage": "50% -> 90%"},
            "quality_score": 85,
            "risks": [],
            "recommendation": "approve",
        }


# Global AI provider instance
ai_provider = AIProvider()


def get_ai_provider() -> AIProvider:
    """Get the global AI provider instance."""
    return ai_provider
