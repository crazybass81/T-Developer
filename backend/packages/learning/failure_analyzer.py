"""
Failure Analysis System for T-Developer

This module implements comprehensive failure analysis capabilities,
learning from failures to prevent recurrence and build automated
recovery strategies.

The FailureAnalyzer classifies failures, identifies root causes,
and creates prevention rules to improve system reliability.
"""

from __future__ import annotations

import hashlib
import logging
import re
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: int = 30
MAX_STACK_DEPTH: int = 20
MIN_FAILURE_FREQUENCY: int = 2


class FailureCategory(Enum):
    """Categories of failures that can occur."""

    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    LOGIC_ERROR = "logic_error"
    TIMEOUT_ERROR = "timeout_error"
    DEPENDENCY_ERROR = "dependency_error"
    RESOURCE_ERROR = "resource_error"
    SECURITY_ERROR = "security_error"
    TEST_FAILURE = "test_failure"
    INTEGRATION_ERROR = "integration_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


class FailureSeverity(Enum):
    """Severity levels for failures."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FailureContext:
    """Context information for a failure.

    Attributes:
        cycle_id: Evolution cycle where failure occurred
        phase: Phase of evolution (research, planning, implementation, evaluation)
        task: Specific task being executed
        agent: Agent that encountered the failure
        timestamp: When the failure occurred
        environment: Environment information
        inputs: Inputs that led to the failure
        stack_trace: Full stack trace
        error_message: Error message
        file_path: File where error occurred
        line_number: Line number where error occurred
        function_name: Function where error occurred
    """

    cycle_id: str
    phase: str
    task: str
    agent: str
    timestamp: datetime
    environment: dict[str, Any]
    inputs: dict[str, Any]
    stack_trace: str
    error_message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None


@dataclass
class FailurePattern:
    """Pattern identified from failure analysis.

    Attributes:
        id: Unique pattern identifier
        category: Failure category
        signature: Unique signature identifying this failure type
        frequency: How often this pattern occurs
        severity: Severity level
        root_cause: Identified root cause
        triggers: Conditions that trigger this failure
        prevention_rules: Rules to prevent this failure
        recovery_actions: Actions to recover from this failure
        affected_components: Components affected by this failure
        first_seen: When this pattern was first observed
        last_seen: When this pattern was last observed
        examples: Example failure contexts
    """

    id: str
    category: FailureCategory
    signature: str
    frequency: int
    severity: FailureSeverity
    root_cause: str
    triggers: list[str]
    prevention_rules: list[str]
    recovery_actions: list[str]
    affected_components: list[str]
    first_seen: datetime
    last_seen: datetime
    examples: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    confidence: float = 0.8


class FailureClassifier:
    """Classifies failures into categories and determines severity."""

    def __init__(self) -> None:
        """Initialize failure classifier."""
        self.syntax_patterns = [r"SyntaxError", r"IndentationError", r"TabError", r"invalid syntax"]

        self.runtime_patterns = [
            r"AttributeError",
            r"TypeError",
            r"ValueError",
            r"IndexError",
            r"KeyError",
            r"NameError",
            r"ZeroDivisionError",
        ]

        self.timeout_patterns = [
            r"TimeoutError",
            r"asyncio\.TimeoutError",
            r"requests\.exceptions\.Timeout",
            r"timeout",
            r"timed out",
        ]

        self.dependency_patterns = [
            r"ModuleNotFoundError",
            r"ImportError",
            r"No module named",
            r"cannot import name",
        ]

        self.resource_patterns = [
            r"MemoryError",
            r"OutOfMemoryError",
            r"DiskSpaceError",
            r"Permission denied",
            r"FileNotFoundError",
        ]

        self.security_patterns = [
            r"PermissionError",
            r"Unauthorized",
            r"Access denied",
            r"Security violation",
            r"Authentication failed",
        ]

    def classify_failure(self, error_message: str, stack_trace: str) -> FailureCategory:
        """Classify failure based on error message and stack trace.

        Args:
            error_message: Error message
            stack_trace: Stack trace

        Returns:
            Failure category
        """
        combined_text = f"{error_message} {stack_trace}".lower()

        # Check patterns in order of specificity
        if self._matches_patterns(combined_text, self.syntax_patterns):
            return FailureCategory.SYNTAX_ERROR
        elif self._matches_patterns(combined_text, self.timeout_patterns):
            return FailureCategory.TIMEOUT_ERROR
        elif self._matches_patterns(combined_text, self.dependency_patterns):
            return FailureCategory.DEPENDENCY_ERROR
        elif self._matches_patterns(combined_text, self.resource_patterns):
            return FailureCategory.RESOURCE_ERROR
        elif self._matches_patterns(combined_text, self.security_patterns):
            return FailureCategory.SECURITY_ERROR
        elif self._matches_patterns(combined_text, self.runtime_patterns):
            return FailureCategory.RUNTIME_ERROR
        elif "test" in combined_text and ("failed" in combined_text or "error" in combined_text):
            return FailureCategory.TEST_FAILURE
        elif "config" in combined_text or "setting" in combined_text:
            return FailureCategory.CONFIGURATION_ERROR
        elif "integration" in combined_text or "api" in combined_text:
            return FailureCategory.INTEGRATION_ERROR
        else:
            return FailureCategory.UNKNOWN_ERROR

    def determine_severity(
        self, category: FailureCategory, context: FailureContext
    ) -> FailureSeverity:
        """Determine failure severity based on category and context.

        Args:
            category: Failure category
            context: Failure context

        Returns:
            Failure severity
        """
        # Critical failures
        if category in [FailureCategory.SECURITY_ERROR, FailureCategory.RESOURCE_ERROR]:
            return FailureSeverity.CRITICAL

        # High severity failures
        if category in [FailureCategory.DEPENDENCY_ERROR, FailureCategory.INTEGRATION_ERROR]:
            return FailureSeverity.HIGH

        # Check context for severity indicators
        if context.phase == "evaluation" and category == FailureCategory.TEST_FAILURE:
            return FailureSeverity.HIGH

        if "critical" in context.error_message.lower():
            return FailureSeverity.CRITICAL
        elif "error" in context.error_message.lower():
            return FailureSeverity.MEDIUM
        else:
            return FailureSeverity.LOW

    def _matches_patterns(self, text: str, patterns: list[str]) -> bool:
        """Check if text matches any of the given patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


class RootCauseAnalyzer:
    """Analyzes failures to identify root causes."""

    def __init__(self) -> None:
        """Initialize root cause analyzer."""
        self.common_causes = {
            FailureCategory.SYNTAX_ERROR: [
                "Missing parentheses or brackets",
                "Incorrect indentation",
                "Invalid Python syntax",
                "Mixing tabs and spaces",
            ],
            FailureCategory.RUNTIME_ERROR: [
                "Null pointer access",
                "Type mismatch",
                "Index out of bounds",
                "Missing dictionary key",
            ],
            FailureCategory.TIMEOUT_ERROR: [
                "Network timeout",
                "Slow database query",
                "Infinite loop",
                "Resource contention",
            ],
            FailureCategory.DEPENDENCY_ERROR: [
                "Missing package installation",
                "Version incompatibility",
                "Circular imports",
                "Environment mismatch",
            ],
        }

    async def analyze_root_cause(self, context: FailureContext, category: FailureCategory) -> str:
        """Analyze root cause of failure.

        Args:
            context: Failure context
            category: Failure category

        Returns:
            Root cause description
        """
        # Start with common causes for the category
        potential_causes = self.common_causes.get(category, ["Unknown cause"])

        # Analyze stack trace for specific clues
        stack_clues = await self._analyze_stack_trace(context.stack_trace)

        # Analyze error message for specific clues
        message_clues = await self._analyze_error_message(context.error_message)

        # Analyze context for environmental factors
        context_clues = await self._analyze_context(context)

        # Combine all clues to determine most likely root cause
        all_clues = stack_clues + message_clues + context_clues

        if all_clues:
            # Return the most specific clue found
            return all_clues[0]
        else:
            # Return most common cause for this category
            return potential_causes[0]

    async def _analyze_stack_trace(self, stack_trace: str) -> list[str]:
        """Analyze stack trace for root cause clues."""
        clues = []

        if not stack_trace:
            return clues

        lines = stack_trace.split("\n")

        # Look for specific patterns in stack trace
        for line in lines:
            line = line.strip().lower()

            if "connectionerror" in line or "connection refused" in line:
                clues.append("Network connection failure")
            elif "timeout" in line:
                clues.append("Operation timeout")
            elif "permission denied" in line:
                clues.append("Insufficient permissions")
            elif "no such file" in line or "file not found" in line:
                clues.append("Missing file or incorrect path")
            elif "null" in line or "none" in line:
                clues.append("Null pointer or None value access")

        return clues

    async def _analyze_error_message(self, error_message: str) -> list[str]:
        """Analyze error message for root cause clues."""
        clues = []

        if not error_message:
            return clues

        message = error_message.lower()

        # Look for specific error patterns
        if "expected" in message and "got" in message:
            clues.append("Type mismatch or unexpected value")
        elif "cannot import" in message:
            clues.append("Import path error or missing dependency")
        elif "index out of range" in message:
            clues.append("Array/list bounds exceeded")
        elif "key error" in message:
            clues.append("Dictionary key not found")
        elif "attribute error" in message:
            clues.append("Object attribute not found")

        return clues

    async def _analyze_context(self, context: FailureContext) -> list[str]:
        """Analyze failure context for environmental clues."""
        clues = []

        # Check for resource constraints
        if context.environment.get("memory_usage", 0) > 90:
            clues.append("Memory exhaustion")

        if context.environment.get("cpu_usage", 0) > 95:
            clues.append("CPU overload")

        # Check for timing issues
        if context.phase == "implementation" and "timeout" in context.error_message.lower():
            clues.append("Implementation taking too long")

        # Check for input validation issues
        if context.inputs and any(v is None for v in context.inputs.values()):
            clues.append("Invalid or missing input parameters")

        return clues


class PreventionRuleGenerator:
    """Generates prevention rules from failure patterns."""

    def __init__(self) -> None:
        """Initialize prevention rule generator."""
        self.rule_templates = {
            FailureCategory.SYNTAX_ERROR: [
                "Run syntax validation before execution",
                "Use linting tools to catch syntax errors",
                "Implement pre-commit hooks for syntax checking",
            ],
            FailureCategory.TIMEOUT_ERROR: [
                "Implement timeout limits for operations",
                "Add retry logic with exponential backoff",
                "Monitor operation duration and alert on slow operations",
            ],
            FailureCategory.DEPENDENCY_ERROR: [
                "Validate all dependencies before execution",
                "Pin dependency versions in requirements",
                "Implement dependency health checks",
            ],
            FailureCategory.RESOURCE_ERROR: [
                "Monitor resource usage continuously",
                "Implement resource limits and quotas",
                "Add resource cleanup after operations",
            ],
        }

    async def generate_prevention_rules(
        self, pattern: FailurePattern, context_examples: list[FailureContext]
    ) -> list[str]:
        """Generate prevention rules for a failure pattern.

        Args:
            pattern: Failure pattern
            context_examples: Example failure contexts

        Returns:
            List of prevention rules
        """
        rules = []

        # Start with template rules for the category
        template_rules = self.rule_templates.get(pattern.category, [])
        rules.extend(template_rules)

        # Generate specific rules based on pattern analysis
        specific_rules = await self._generate_specific_rules(pattern, context_examples)
        rules.extend(specific_rules)

        # Remove duplicates while preserving order
        seen = set()
        unique_rules = []
        for rule in rules:
            if rule not in seen:
                seen.add(rule)
                unique_rules.append(rule)

        return unique_rules

    async def _generate_specific_rules(
        self, pattern: FailurePattern, contexts: list[FailureContext]
    ) -> list[str]:
        """Generate specific rules based on pattern analysis."""
        rules = []

        # Analyze common factors across contexts
        common_files = self._find_common_files(contexts)
        common_functions = self._find_common_functions(contexts)
        common_inputs = self._find_common_inputs(contexts)

        # Generate rules for common files
        if common_files:
            for file_path in common_files[:3]:  # Top 3 most common
                rules.append(f"Add extra validation for operations in {file_path}")

        # Generate rules for common functions
        if common_functions:
            for function in common_functions[:3]:  # Top 3 most common
                rules.append(f"Add error handling wrapper for {function}")

        # Generate rules for common input patterns
        if common_inputs:
            rules.append("Validate input parameters before processing")
            rules.append("Add input sanitization for common failure cases")

        # Pattern-specific rules
        if pattern.frequency >= 5:
            rules.append(f"Implement automated detection for {pattern.signature}")

        if "null" in pattern.root_cause.lower() or "none" in pattern.root_cause.lower():
            rules.append("Add null/None checks before object access")

        if "timeout" in pattern.root_cause.lower():
            rules.append("Reduce operation timeout or optimize performance")

        return rules

    def _find_common_files(self, contexts: list[FailureContext]) -> list[str]:
        """Find files that appear in multiple failure contexts."""
        file_counts = {}

        for context in contexts:
            if context.file_path:
                file_counts[context.file_path] = file_counts.get(context.file_path, 0) + 1

        # Return files that appear in at least 2 contexts
        common_files = [file for file, count in file_counts.items() if count >= 2]
        return sorted(common_files, key=lambda x: file_counts[x], reverse=True)

    def _find_common_functions(self, contexts: list[FailureContext]) -> list[str]:
        """Find functions that appear in multiple failure contexts."""
        function_counts = {}

        for context in contexts:
            if context.function_name:
                function_counts[context.function_name] = (
                    function_counts.get(context.function_name, 0) + 1
                )

        # Return functions that appear in at least 2 contexts
        common_functions = [func for func, count in function_counts.items() if count >= 2]
        return sorted(common_functions, key=lambda x: function_counts[x], reverse=True)

    def _find_common_inputs(self, contexts: list[FailureContext]) -> dict[str, Any]:
        """Find input patterns that appear in multiple failure contexts."""
        input_patterns = {}

        for context in contexts:
            for key, value in context.inputs.items():
                pattern_key = f"{key}:{type(value).__name__}"
                input_patterns[pattern_key] = input_patterns.get(pattern_key, 0) + 1

        # Return patterns that appear in at least 2 contexts
        return {pattern: count for pattern, count in input_patterns.items() if count >= 2}


class RecoveryStrategyGenerator:
    """Generates automated recovery strategies for failures."""

    def __init__(self) -> None:
        """Initialize recovery strategy generator."""
        self.recovery_templates = {
            FailureCategory.TIMEOUT_ERROR: [
                "Retry operation with exponential backoff",
                "Reduce operation scope and retry",
                "Switch to alternative implementation",
            ],
            FailureCategory.DEPENDENCY_ERROR: [
                "Install missing dependencies automatically",
                "Use alternative dependency if available",
                "Skip optional dependencies and continue",
            ],
            FailureCategory.RESOURCE_ERROR: [
                "Clean up unused resources",
                "Reduce resource allocation",
                "Wait for resources to become available",
            ],
            FailureCategory.RUNTIME_ERROR: [
                "Use default values for missing data",
                "Skip problematic operation and continue",
                "Rollback to previous stable state",
            ],
        }

    async def generate_recovery_actions(
        self, pattern: FailurePattern, contexts: list[FailureContext]
    ) -> list[str]:
        """Generate recovery actions for a failure pattern.

        Args:
            pattern: Failure pattern
            contexts: Example failure contexts

        Returns:
            List of recovery actions
        """
        actions = []

        # Start with template actions for the category
        template_actions = self.recovery_templates.get(pattern.category, [])
        actions.extend(template_actions)

        # Generate specific actions based on pattern analysis
        specific_actions = await self._generate_specific_actions(pattern, contexts)
        actions.extend(specific_actions)

        # Remove duplicates while preserving order
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)

        return unique_actions

    async def _generate_specific_actions(
        self, pattern: FailurePattern, contexts: list[FailureContext]
    ) -> list[str]:
        """Generate specific recovery actions based on pattern analysis."""
        actions = []

        # Analyze recovery opportunities
        if "file not found" in pattern.root_cause.lower():
            actions.append("Create missing file with default content")
            actions.append("Use alternative file path if available")

        if "connection" in pattern.root_cause.lower():
            actions.append("Retry connection with different endpoint")
            actions.append("Use cached data if available")

        if "permission" in pattern.root_cause.lower():
            actions.append("Request elevated permissions")
            actions.append("Use alternative method with lower permissions")

        if pattern.frequency >= 5:
            actions.append("Implement automated recovery workflow")

        # Phase-specific recovery actions
        phase_actions = self._get_phase_specific_actions(contexts)
        actions.extend(phase_actions)

        return actions

    def _get_phase_specific_actions(self, contexts: list[FailureContext]) -> list[str]:
        """Get recovery actions specific to evolution phases."""
        actions = []
        phases = [context.phase for context in contexts]

        if "research" in phases:
            actions.append("Use alternative research sources")
            actions.append("Reduce research scope and continue")

        if "planning" in phases:
            actions.append("Generate simpler plan")
            actions.append("Use predefined plan template")

        if "implementation" in phases:
            actions.append("Rollback to last working implementation")
            actions.append("Use simpler implementation approach")

        if "evaluation" in phases:
            actions.append("Skip problematic evaluation metric")
            actions.append("Use alternative evaluation method")

        return actions


class FailureAnalyzer:
    """Main failure analysis system.

    Analyzes failures from evolution cycles to identify patterns,
    root causes, and generate prevention rules and recovery strategies.

    Example:
        >>> analyzer = FailureAnalyzer()
        >>> await analyzer.initialize()
        >>> patterns = await analyzer.analyze_failures(failure_contexts)
        >>> rules = await analyzer.get_prevention_rules()
    """

    def __init__(self) -> None:
        """Initialize failure analyzer."""
        self.classifier = FailureClassifier()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.prevention_generator = PreventionRuleGenerator()
        self.recovery_generator = RecoveryStrategyGenerator()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Storage for failure patterns
        self.failure_patterns: dict[str, FailurePattern] = {}
        self.failure_contexts: list[FailureContext] = []

    async def initialize(self) -> None:
        """Initialize the failure analyzer."""
        self.logger.info("Failure analyzer initialized")

    async def analyze_failure(
        self,
        cycle_id: str,
        phase: str,
        task: str,
        agent: str,
        error: Exception,
        context: dict[str, Any],
    ) -> FailureContext:
        """Analyze a single failure and create failure context.

        Args:
            cycle_id: Evolution cycle ID
            phase: Phase where failure occurred
            task: Task being executed
            agent: Agent that encountered failure
            error: The exception that occurred
            context: Additional context information

        Returns:
            Failure context object
        """
        # Extract error information
        error_message = str(error)
        stack_trace = traceback.format_exc()

        # Parse stack trace for file and line information
        file_path, line_number, function_name = self._parse_stack_trace(stack_trace)

        # Create failure context
        failure_context = FailureContext(
            cycle_id=cycle_id,
            phase=phase,
            task=task,
            agent=agent,
            timestamp=datetime.now(),
            environment=await self._get_environment_info(),
            inputs=context.get("inputs", {}),
            stack_trace=stack_trace,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
        )

        # Store failure context
        self.failure_contexts.append(failure_context)

        # Update failure patterns
        await self._update_failure_patterns(failure_context)

        self.logger.info(f"Analyzed failure in {phase}:{task} - {error_message[:100]}")
        return failure_context

    async def analyze_failures(self, contexts: list[FailureContext]) -> list[FailurePattern]:
        """Analyze multiple failures to identify patterns.

        Args:
            contexts: List of failure contexts to analyze

        Returns:
            List of identified failure patterns
        """
        if not contexts:
            return []

        self.logger.info(f"Analyzing {len(contexts)} failure contexts")

        # Group failures by signature
        signature_groups = await self._group_failures_by_signature(contexts)

        patterns = []
        for signature, group_contexts in signature_groups.items():
            if len(group_contexts) >= MIN_FAILURE_FREQUENCY:
                pattern = await self._create_failure_pattern(signature, group_contexts)
                if pattern:
                    patterns.append(pattern)

        self.logger.info(f"Identified {len(patterns)} failure patterns")
        return patterns

    async def _update_failure_patterns(self, context: FailureContext) -> None:
        """Update failure patterns with new failure context."""
        signature = await self._generate_failure_signature(context)

        if signature in self.failure_patterns:
            # Update existing pattern
            pattern = self.failure_patterns[signature]
            pattern.frequency += 1
            pattern.last_seen = context.timestamp
            pattern.examples.append(context.cycle_id)

            # Limit examples to last 10
            if len(pattern.examples) > 10:
                pattern.examples = pattern.examples[-10:]
        else:
            # Create new pattern
            category = self.classifier.classify_failure(context.error_message, context.stack_trace)
            severity = self.classifier.determine_severity(category, context)
            root_cause = await self.root_cause_analyzer.analyze_root_cause(context, category)

            pattern = FailurePattern(
                id=f"failure_{hashlib.md5(signature.encode()).hexdigest()[:8]}",
                category=category,
                signature=signature,
                frequency=1,
                severity=severity,
                root_cause=root_cause,
                triggers=[],
                prevention_rules=[],
                recovery_actions=[],
                affected_components=[context.agent],
                first_seen=context.timestamp,
                last_seen=context.timestamp,
                examples=[context.cycle_id],
            )

            self.failure_patterns[signature] = pattern

    async def _group_failures_by_signature(
        self, contexts: list[FailureContext]
    ) -> dict[str, list[FailureContext]]:
        """Group failure contexts by signature."""
        groups = {}

        for context in contexts:
            signature = await self._generate_failure_signature(context)
            if signature not in groups:
                groups[signature] = []
            groups[signature].append(context)

        return groups

    async def _generate_failure_signature(self, context: FailureContext) -> str:
        """Generate unique signature for failure type."""
        # Extract key components for signature
        error_type = (
            type(context.error_message).__name__
            if hasattr(context.error_message, "__class__")
            else "Unknown"
        )

        # Extract error class from message
        if ":" in context.error_message:
            error_type = context.error_message.split(":")[0].strip()

        # Normalize error message (remove specific values)
        normalized_message = re.sub(r"\d+", "<NUMBER>", context.error_message)
        normalized_message = re.sub(r"'[^']*'", "'<STRING>'", normalized_message)
        normalized_message = re.sub(r'"[^"]*"', '"<STRING>"', normalized_message)

        # Create signature from key components
        signature_parts = [
            error_type,
            context.phase,
            context.agent,
            normalized_message[:100],  # First 100 chars of normalized message
        ]

        # Add file path if available
        if context.file_path:
            signature_parts.append(context.file_path)

        signature = "|".join(signature_parts)
        return hashlib.md5(signature.encode()).hexdigest()

    async def _create_failure_pattern(
        self, signature: str, contexts: list[FailureContext]
    ) -> Optional[FailurePattern]:
        """Create failure pattern from grouped contexts."""
        if not contexts:
            return None

        # Use first context as template
        template_context = contexts[0]

        # Classify failure
        category = self.classifier.classify_failure(
            template_context.error_message, template_context.stack_trace
        )

        severity = self.classifier.determine_severity(category, template_context)
        root_cause = await self.root_cause_analyzer.analyze_root_cause(template_context, category)

        # Create pattern
        pattern = FailurePattern(
            id=f"failure_{hashlib.md5(signature.encode()).hexdigest()[:8]}",
            category=category,
            signature=signature,
            frequency=len(contexts),
            severity=severity,
            root_cause=root_cause,
            triggers=await self._extract_triggers(contexts),
            prevention_rules=[],
            recovery_actions=[],
            affected_components=list(set(c.agent for c in contexts)),
            first_seen=min(c.timestamp for c in contexts),
            last_seen=max(c.timestamp for c in contexts),
            examples=[c.cycle_id for c in contexts[-5:]],  # Last 5 examples
        )

        # Generate prevention rules and recovery actions
        pattern.prevention_rules = await self.prevention_generator.generate_prevention_rules(
            pattern, contexts
        )
        pattern.recovery_actions = await self.recovery_generator.generate_recovery_actions(
            pattern, contexts
        )

        return pattern

    async def _extract_triggers(self, contexts: list[FailureContext]) -> list[str]:
        """Extract common triggers from failure contexts."""
        triggers = []

        # Analyze common input patterns
        input_patterns = {}
        for context in contexts:
            for key, value in context.inputs.items():
                pattern = f"{key}={type(value).__name__}"
                input_patterns[pattern] = input_patterns.get(pattern, 0) + 1

        # Add patterns that appear in most contexts
        threshold = len(contexts) * 0.7  # 70% of contexts
        for pattern, count in input_patterns.items():
            if count >= threshold:
                triggers.append(f"Input pattern: {pattern}")

        # Analyze common phases and tasks
        phases = [c.phase for c in contexts]
        tasks = [c.task for c in contexts]

        if len(set(phases)) == 1:
            triggers.append(f"Phase: {phases[0]}")

        if len(set(tasks)) == 1:
            triggers.append(f"Task: {tasks[0]}")

        # Analyze environmental factors
        high_memory_count = sum(1 for c in contexts if c.environment.get("memory_usage", 0) > 80)
        if high_memory_count >= threshold:
            triggers.append("High memory usage")

        return triggers

    def _parse_stack_trace(
        self, stack_trace: str
    ) -> tuple[Optional[str], Optional[int], Optional[str]]:
        """Parse stack trace to extract file, line, and function information."""
        if not stack_trace:
            return None, None, None

        lines = stack_trace.split("\n")

        # Look for the last meaningful stack frame (not from this analyzer)
        for line in reversed(lines):
            if 'File "' in line and "line " in line:
                # Extract file path
                file_match = re.search(r'File "([^"]+)"', line)
                file_path = file_match.group(1) if file_match else None

                # Extract line number
                line_match = re.search(r"line (\d+)", line)
                line_number = int(line_match.group(1)) if line_match else None

                # Extract function name (usually on next line)
                function_name = None
                line_index = lines.index(line)
                if line_index + 1 < len(lines):
                    next_line = lines[line_index + 1].strip()
                    if next_line and not next_line.startswith("File"):
                        function_name = next_line

                return file_path, line_number, function_name

        return None, None, None

    async def _get_environment_info(self) -> dict[str, Any]:
        """Get current environment information."""
        try:
            import psutil

            return {
                "memory_usage": psutil.virtual_memory().percent,
                "cpu_usage": psutil.cpu_percent(interval=0.1),
                "disk_usage": psutil.disk_usage("/").percent,
                "load_average": psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0,
            }
        except ImportError:
            return {"memory_usage": 0, "cpu_usage": 0, "disk_usage": 0, "load_average": 0}

    async def get_prevention_rules(self) -> list[str]:
        """Get all prevention rules from analyzed patterns.

        Returns:
            List of all prevention rules
        """
        all_rules = []

        for pattern in self.failure_patterns.values():
            all_rules.extend(pattern.prevention_rules)

        # Remove duplicates while preserving order
        seen = set()
        unique_rules = []
        for rule in all_rules:
            if rule not in seen:
                seen.add(rule)
                unique_rules.append(rule)

        return unique_rules

    async def get_recovery_strategies(self) -> dict[str, list[str]]:
        """Get recovery strategies organized by failure category.

        Returns:
            Dictionary of recovery strategies by category
        """
        strategies = {}

        for pattern in self.failure_patterns.values():
            category = pattern.category.value
            if category not in strategies:
                strategies[category] = []
            strategies[category].extend(pattern.recovery_actions)

        # Remove duplicates in each category
        for category in strategies:
            seen = set()
            unique_actions = []
            for action in strategies[category]:
                if action not in seen:
                    seen.add(action)
                    unique_actions.append(action)
            strategies[category] = unique_actions

        return strategies

    async def get_failure_statistics(self) -> dict[str, Any]:
        """Get statistics about analyzed failures.

        Returns:
            Dictionary containing failure statistics
        """
        if not self.failure_patterns:
            return {"total_patterns": 0}

        patterns = list(self.failure_patterns.values())

        stats = {
            "total_patterns": len(patterns),
            "total_failures": sum(p.frequency for p in patterns),
            "categories": {},
            "severities": {},
            "most_frequent_pattern": max(patterns, key=lambda p: p.frequency).signature,
            "most_recent_failure": max(patterns, key=lambda p: p.last_seen).last_seen.isoformat(),
            "critical_patterns": len(
                [p for p in patterns if p.severity == FailureSeverity.CRITICAL]
            ),
            "prevention_rules_count": len(await self.get_prevention_rules()),
        }

        # Category breakdown
        for pattern in patterns:
            category = pattern.category.value
            if category not in stats["categories"]:
                stats["categories"][category] = {"count": 0, "frequency": 0}
            stats["categories"][category]["count"] += 1
            stats["categories"][category]["frequency"] += pattern.frequency

        # Severity breakdown
        for pattern in patterns:
            severity = pattern.severity.value
            if severity not in stats["severities"]:
                stats["severities"][severity] = {"count": 0, "frequency": 0}
            stats["severities"][severity]["count"] += 1
            stats["severities"][severity]["frequency"] += pattern.frequency

        return stats
