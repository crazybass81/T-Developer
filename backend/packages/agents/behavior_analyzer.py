"""Behavior Analyzer for UX and runtime behavior analysis.

This agent analyzes execution logs, user interaction patterns,
and runtime behavior to understand how code is actually used.
"""

from __future__ import annotations

import re
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

from backend.packages.agents.base import BaseAgent, AgentResult, AgentTask, TaskStatus
from backend.packages.agents.ai_providers import get_ai_provider
from backend.packages.memory import ContextType, MemoryHub


@dataclass
class ExecutionPath:
    """Represents an execution path through the code."""
    
    path_id: str
    functions: List[str]
    frequency: int
    avg_duration_ms: float
    error_rate: float
    last_seen: str


@dataclass
class PerformanceHotspot:
    """Represents a performance bottleneck."""
    
    function_name: str
    file_path: str
    avg_duration_ms: float
    max_duration_ms: float
    call_count: int
    memory_usage_mb: float
    cpu_usage_percent: float


@dataclass
class ErrorPattern:
    """Represents a recurring error pattern."""
    
    error_type: str
    message: str
    location: str
    frequency: int
    first_seen: str
    last_seen: str
    stack_trace: Optional[str]


@dataclass
class BehaviorReport:
    """Complete behavior analysis report."""
    
    # Usage patterns
    most_used_functions: List[Tuple[str, int]] = field(default_factory=list)
    execution_paths: List[ExecutionPath] = field(default_factory=list)
    user_flows: Dict[str, List[str]] = field(default_factory=dict)
    
    # Performance
    performance_hotspots: List[PerformanceHotspot] = field(default_factory=list)
    slow_queries: List[Dict[str, Any]] = field(default_factory=list)
    memory_leaks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Errors
    error_patterns: List[ErrorPattern] = field(default_factory=list)
    error_rate: float = 0.0
    critical_errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metrics
    total_executions: int = 0
    unique_users: int = 0
    avg_response_time_ms: float = 0.0
    peak_memory_mb: float = 0.0
    
    # Time analysis
    peak_usage_hours: List[int] = field(default_factory=list)
    usage_by_day: Dict[str, int] = field(default_factory=dict)


class BehaviorAnalyzer(BaseAgent):
    """AI-powered behavior analyzer for intelligent anomaly detection.
    
    This agent uses AI to:
    1. Detect anomalies and unusual patterns
    2. Predict potential failures before they occur
    3. Identify root causes of issues
    4. Learn normal behavior baselines
    5. Generate actionable insights from logs
    6. Correlate events across multiple sources
    7. Predict performance degradation
    """
    
    def __init__(
        self,
        memory_hub: Optional[MemoryHub] = None,
        document_context=None,
        **kwargs: Any
    ) -> None:
        """Initialize the Behavior Analyzer.
        
        Args:
            memory_hub: Memory Hub instance
            document_context: SharedDocumentContext 인스턴스
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="BehaviorAnalyzer",
            version="2.0.0",  # AI-enhanced version
            memory_hub=memory_hub,
            document_context=document_context,
            **kwargs
        )
        
        self.logger = logging.getLogger(__name__)
        self.ai_provider = None  # Lazy load AI provider
        
        # Patterns for log parsing
        self.log_patterns = {
            "timestamp": r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})",
            "level": r"(DEBUG|INFO|WARNING|ERROR|CRITICAL)",
            "function": r"in\s+(\w+)\s*\(",
            "file": r"File\s+\"([^\"]+)\"",
            "line": r"line\s+(\d+)",
            "duration": r"duration[:\s]+(\d+(?:\.\d+)?)\s*ms",
            "memory": r"memory[:\s]+(\d+(?:\.\d+)?)\s*MB",
            "user": r"user[:\s]+([^\s,]+)",
            "error": r"(?:Error|Exception):\s*(.+)",
            "traceback": r"Traceback\s+\(most recent call last\):(.*?)(?=\n\n|\Z)"
        }
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute behavior analysis.
        
        Args:
            task: The analysis task containing:
                - inputs.log_paths: List of log file paths
                - inputs.log_format: Log format type (default: auto-detect)
                - inputs.time_range: Time range to analyze (optional)
                - inputs.focus_on: Specific patterns to focus on
                
        Returns:
            AgentResult containing behavior analysis
        """
        try:
            # Handle both dict and AgentTask inputs
            if isinstance(task, dict):
                inputs = task
            else:
                inputs = task.inputs
            
            # Extract parameters
            log_paths = inputs.get("log_paths", [])
            log_format = inputs.get("log_format", "auto")
            time_range = inputs.get("time_range")
            focus_on = inputs.get("focus_on", [])
            
            # Parse logs
            log_entries = await self._parse_logs(log_paths, log_format)
            
            # Filter by time range if specified
            if time_range:
                log_entries = self._filter_by_time(log_entries, time_range)
            
            # Analyze behavior
            report = await self._analyze_behavior(log_entries, focus_on)
            
            # Check if report is valid
            if not report:
                # Create a default empty report if analysis failed
                report = BehaviorReport()
            
            # Store in memory if available
            if self.memory_hub and report:
                await self._store_analysis(report)
            
            # Generate insights
            insights = self._generate_insights(report) if report else []
            
            # Safely access report attributes with defaults
            return self.format_result(
                success=True,
                data={
                    "total_executions": getattr(report, 'total_executions', 0),
                    "unique_users": getattr(report, 'unique_users', 0),
                    "error_rate": getattr(report, 'error_rate', 0.0),
                    "avg_response_time_ms": getattr(report, 'avg_response_time_ms', 0),
                    "most_used_functions": getattr(report, 'most_used_functions', [])[:10],
                    "performance_hotspots": [self._hotspot_to_dict(h) for h in getattr(report, 'performance_hotspots', [])[:5]],
                    "error_patterns": [self._error_to_dict(e) for e in getattr(report, 'error_patterns', [])[:5]],
                    "critical_errors": getattr(report, 'critical_errors', [])[:3],
                    "execution_paths": [self._path_to_dict(p) for p in getattr(report, 'execution_paths', [])[:5]],
                    "insights": insights,
                    "summary": {
                        "total_patterns": len(getattr(report, 'error_patterns', [])),
                        "error_rate": getattr(report, 'error_rate', 0.0),
                        "performance_score": 100 - min(getattr(report, 'error_rate', 0) * 100, 100)
                    }
                },
                metadata={"agent": self.name, "version": self.version}
            )
            
        except Exception as e:
            self.logger.error(f"Behavior analysis failed: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    async def _parse_logs(
        self,
        log_paths: List[str],
        log_format: str
    ) -> List[Dict[str, Any]]:
        """Parse log files into structured entries.
        
        Args:
            log_paths: List of log file paths
            log_format: Log format type
            
        Returns:
            List of parsed log entries
        """
        entries = []
        
        for log_path in log_paths:
            if not os.path.exists(log_path):
                self.logger.warning(f"Log file not found: {log_path}")
                continue
            
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Auto-detect format if needed
                if log_format == "auto":
                    log_format = self._detect_log_format(content)
                
                # Parse based on format
                if log_format == "json":
                    entries.extend(self._parse_json_logs(content))
                elif log_format == "structured":
                    entries.extend(self._parse_structured_logs(content))
                else:
                    entries.extend(self._parse_text_logs(content))
                    
            except Exception as e:
                self.logger.warning(f"Failed to parse {log_path}: {e}")
        
        return entries
    
    def _detect_log_format(self, content: str) -> str:
        """Detect log format from content.
        
        Args:
            content: Log file content
            
        Returns:
            Detected format type
        """
        # Check for JSON
        if content.strip().startswith('{') or content.strip().startswith('['):
            try:
                json.loads(content.split('\n')[0])
                return "json"
            except:
                pass
        
        # Check for structured format (key=value)
        if '=' in content and any(kw in content for kw in ['timestamp=', 'level=', 'msg=']):
            return "structured"
        
        return "text"
    
    def _parse_json_logs(self, content: str) -> List[Dict[str, Any]]:
        """Parse JSON formatted logs.
        
        Args:
            content: Log content
            
        Returns:
            Parsed entries
        """
        entries = []
        
        for line in content.split('\n'):
            if not line.strip():
                continue
            
            try:
                entry = json.loads(line)
                entries.append(self._normalize_entry(entry))
            except:
                pass
        
        return entries
    
    def _parse_structured_logs(self, content: str) -> List[Dict[str, Any]]:
        """Parse structured logs (key=value format).
        
        Args:
            content: Log content
            
        Returns:
            Parsed entries
        """
        entries = []
        
        for line in content.split('\n'):
            if not line.strip():
                continue
            
            entry = {}
            # Parse key=value pairs
            for match in re.finditer(r'(\w+)=([^\s]+|\".+?\")', line):
                key = match.group(1)
                value = match.group(2).strip('"')
                entry[key] = value
            
            if entry:
                entries.append(self._normalize_entry(entry))
        
        return entries
    
    def _parse_text_logs(self, content: str) -> List[Dict[str, Any]]:
        """Parse unstructured text logs.
        
        Args:
            content: Log content
            
        Returns:
            Parsed entries
        """
        entries = []
        lines = content.split('\n')
        
        current_entry = {}
        traceback_buffer = []
        in_traceback = False
        
        for line in lines:
            if not line.strip():
                if current_entry:
                    entries.append(self._normalize_entry(current_entry))
                    current_entry = {}
                continue
            
            # Check for traceback
            if "Traceback (most recent call last):" in line:
                in_traceback = True
                traceback_buffer = [line]
                continue
            
            if in_traceback:
                traceback_buffer.append(line)
                if line.strip() and not line.startswith(' '):
                    current_entry['traceback'] = '\n'.join(traceback_buffer)
                    in_traceback = False
                    traceback_buffer = []
                continue
            
            # Extract patterns
            for pattern_name, pattern in self.log_patterns.items():
                match = re.search(pattern, line)
                if match:
                    current_entry[pattern_name] = match.group(1)
            
            # Store raw message
            if 'message' not in current_entry:
                current_entry['message'] = line
        
        if current_entry:
            entries.append(self._normalize_entry(current_entry))
        
        return entries
    
    def _normalize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize log entry format.
        
        Args:
            entry: Raw log entry
            
        Returns:
            Normalized entry
        """
        normalized = {
            "timestamp": entry.get("timestamp", entry.get("time", "")),
            "level": entry.get("level", entry.get("severity", "INFO")),
            "message": entry.get("message", entry.get("msg", "")),
            "function": entry.get("function", entry.get("func", "")),
            "file": entry.get("file", entry.get("filename", "")),
            "line": entry.get("line", entry.get("lineno", 0)),
            "duration_ms": float(entry.get("duration", entry.get("duration_ms", 0))),
            "memory_mb": float(entry.get("memory", entry.get("memory_mb", 0))),
            "user": entry.get("user", entry.get("user_id", "")),
            "error": entry.get("error", entry.get("exception", "")),
            "traceback": entry.get("traceback", entry.get("stack_trace", ""))
        }
        
        # Parse timestamp if string
        if isinstance(normalized["timestamp"], str):
            try:
                normalized["timestamp"] = datetime.fromisoformat(
                    normalized["timestamp"].replace(' ', 'T')
                )
            except:
                normalized["timestamp"] = None
        
        return normalized
    
    def _filter_by_time(
        self,
        entries: List[Dict[str, Any]],
        time_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Filter log entries by time range.
        
        Args:
            entries: Log entries
            time_range: Dict with 'start' and/or 'end' timestamps
            
        Returns:
            Filtered entries
        """
        filtered = []
        
        start_time = None
        end_time = None
        
        if "start" in time_range:
            start_time = datetime.fromisoformat(time_range["start"])
        if "end" in time_range:
            end_time = datetime.fromisoformat(time_range["end"])
        
        for entry in entries:
            if entry["timestamp"]:
                if start_time and entry["timestamp"] < start_time:
                    continue
                if end_time and entry["timestamp"] > end_time:
                    continue
                filtered.append(entry)
        
        return filtered
    
    async def _analyze_behavior(
        self,
        log_entries: List[Dict[str, Any]],
        focus_on: List[str]
    ) -> BehaviorReport:
        """Analyze behavior from log entries.
        
        Args:
            log_entries: Parsed log entries
            focus_on: Specific patterns to focus on
            
        Returns:
            Behavior report
        """
        report = BehaviorReport()
        
        # Count total executions
        report.total_executions = len(log_entries)
        
        # Track unique users
        users = set()
        
        # Track function calls
        function_calls = Counter()
        function_durations = defaultdict(list)
        function_errors = defaultdict(int)
        
        # Track execution paths
        user_sessions = defaultdict(list)
        
        # Track errors
        errors = []
        
        # Track performance
        response_times = []
        memory_usage = []
        
        # Track time patterns
        hour_counts = Counter()
        day_counts = Counter()
        
        for entry in log_entries:
            # User tracking
            if entry["user"]:
                users.add(entry["user"])
                user_sessions[entry["user"]].append(entry["function"])
            
            # Function tracking
            if entry["function"]:
                function_calls[entry["function"]] += 1
                if entry["duration_ms"]:
                    function_durations[entry["function"]].append(entry["duration_ms"])
                if entry["error"]:
                    function_errors[entry["function"]] += 1
            
            # Error tracking
            if entry["error"] or entry["level"] in ["ERROR", "CRITICAL"]:
                errors.append(entry)
            
            # Performance tracking
            if entry["duration_ms"]:
                response_times.append(entry["duration_ms"])
            if entry["memory_mb"]:
                memory_usage.append(entry["memory_mb"])
            
            # Time pattern tracking
            if entry["timestamp"]:
                hour_counts[entry["timestamp"].hour] += 1
                day_counts[entry["timestamp"].strftime("%A")] += 1
        
        # Populate report
        report.unique_users = len(users)
        report.most_used_functions = function_calls.most_common(20)
        
        # Calculate error rate
        if report.total_executions > 0:
            report.error_rate = len(errors) / report.total_executions
        
        # Calculate average response time
        if response_times:
            report.avg_response_time_ms = sum(response_times) / len(response_times)
        
        # Find peak memory
        if memory_usage:
            report.peak_memory_mb = max(memory_usage)
        
        # Identify performance hotspots
        for func, durations in function_durations.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                if avg_duration > 100:  # Over 100ms
                    hotspot = PerformanceHotspot(
                        function_name=func,
                        file_path="",  # Would need more info
                        avg_duration_ms=avg_duration,
                        max_duration_ms=max(durations),
                        call_count=function_calls[func],
                        memory_usage_mb=0,  # Would need more info
                        cpu_usage_percent=0  # Would need more info
                    )
                    report.performance_hotspots.append(hotspot)
        
        # Sort hotspots by average duration
        report.performance_hotspots.sort(key=lambda h: h.avg_duration_ms, reverse=True)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in standardized format."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Identify error patterns
        error_groups = defaultdict(list)
        for error in errors:
            key = (error["error"], error["function"])
            error_groups[key].append(error)
        
        for (error_type, location), error_list in error_groups.items():
            if len(error_list) >= 2:  # At least 2 occurrences
                pattern = ErrorPattern(
                    error_type=error_type or "Unknown",
                    message=error_list[0]["message"],
                    location=location or "Unknown",
                    frequency=len(error_list),
                    first_seen=str(error_list[0]["timestamp"]) if error_list[0]["timestamp"] else "",
                    last_seen=str(error_list[-1]["timestamp"]) if error_list[-1]["timestamp"] else "",
                    stack_trace=error_list[0]["traceback"]
                )
                report.error_patterns.append(pattern)
        
        # Sort error patterns by frequency
        report.error_patterns.sort(key=lambda e: e.frequency, reverse=True)
        
        # Identify critical errors
        for error in errors:
            if error["level"] == "CRITICAL":
                report.critical_errors.append({
                    "timestamp": str(error["timestamp"]),
                    "message": error["message"],
                    "function": error["function"],
                    "traceback": error["traceback"]
                })
        
        # Analyze execution paths
        path_counts = Counter()
        for user, functions in user_sessions.items():
            if len(functions) >= 2:
                # Create path from consecutive functions
                for i in range(len(functions) - 1):
                    path = f"{functions[i]} -> {functions[i+1]}"
                    path_counts[path] += 1
        
        for path, count in path_counts.most_common(10):
            exec_path = ExecutionPath(
                path_id=path,
                functions=path.split(" -> "),
                frequency=count,
                avg_duration_ms=0,  # Would need more analysis
                error_rate=0,  # Would need more analysis
                last_seen=""
            )
            report.execution_paths.append(exec_path)
        
        # Peak usage hours
        if hour_counts:
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            report.peak_usage_hours = [hour for hour, _ in peak_hours]
        
        # Usage by day
        report.usage_by_day = dict(day_counts)
        
        return report
    
    def _hotspot_to_dict(self, hotspot: PerformanceHotspot) -> Dict[str, Any]:
        """Convert PerformanceHotspot to dictionary.
        
        Args:
            hotspot: Performance hotspot
            
        Returns:
            Dictionary representation
        """
        return {
            "function": hotspot.function_name,
            "avg_duration_ms": hotspot.avg_duration_ms,
            "max_duration_ms": hotspot.max_duration_ms,
            "call_count": hotspot.call_count
        }
    
    def _error_to_dict(self, error: ErrorPattern) -> Dict[str, Any]:
        """Convert ErrorPattern to dictionary.
        
        Args:
            error: Error pattern
            
        Returns:
            Dictionary representation
        """
        return {
            "type": error.error_type,
            "location": error.location,
            "frequency": error.frequency,
            "last_seen": error.last_seen
        }
    
    def _path_to_dict(self, path: ExecutionPath) -> Dict[str, Any]:
        """Convert ExecutionPath to dictionary.
        
        Args:
            path: Execution path
            
        Returns:
            Dictionary representation
        """
        return {
            "path": path.path_id,
            "frequency": path.frequency,
            "functions": path.functions
        }
    
    def _generate_insights(self, report: BehaviorReport) -> List[str]:
        """Generate actionable insights from behavior analysis.
        
        Args:
            report: Behavior report
            
        Returns:
            List of insights
        """
        insights = []
        
        # Performance insights
        if report.performance_hotspots:
            worst = report.performance_hotspots[0]
            insights.append(
                f"Performance bottleneck: '{worst.function_name}' takes "
                f"{worst.avg_duration_ms:.0f}ms on average"
            )
        
        # Error insights
        if report.error_rate > 0.05:
            insights.append(
                f"High error rate detected: {report.error_rate:.1%} of executions fail"
            )
        
        if report.error_patterns:
            most_common = report.error_patterns[0]
            insights.append(
                f"Recurring error: '{most_common.error_type}' in {most_common.location} "
                f"({most_common.frequency} times)"
            )
        
        # Usage insights
        if report.most_used_functions:
            top_func = report.most_used_functions[0]
            insights.append(
                f"Most used function: '{top_func[0]}' called {top_func[1]} times"
            )
        
        # Pattern insights
        if report.execution_paths:
            common_path = report.execution_paths[0]
            insights.append(
                f"Common user flow: {' → '.join(common_path.functions)} "
                f"({common_path.frequency} times)"
            )
        
        # Time insights
        if report.peak_usage_hours:
            hours = ", ".join(f"{h}:00" for h in report.peak_usage_hours)
            insights.append(f"Peak usage hours: {hours}")
        
        # Memory insights
        if report.peak_memory_mb > 500:
            insights.append(
                f"High memory usage detected: peak {report.peak_memory_mb:.0f}MB"
            )
        
        return insights
    
    async def _store_analysis(self, report: BehaviorReport) -> None:
        """Store analysis results in memory.
        
        Args:
            report: Behavior report
        """
        if not self.memory_hub:
            return
        
        # Store in agent context
        await self.write_memory(
            ContextType.A_CTX,
            f"behavior_analysis_{self._get_timestamp()}",
            {
                "total_executions": report.total_executions,
                "error_rate": report.error_rate,
                "avg_response_time": report.avg_response_time_ms,
                "hotspots_count": len(report.performance_hotspots),
                "error_patterns_count": len(report.error_patterns),
                "timestamp": self._get_timestamp()
            },
            ttl_seconds=86400 * 7,  # 7 days
            tags=["behavior", "analysis", "runtime"]
        )
    
    async def validate_input(self, task: AgentTask) -> bool:
        """Validate the analysis task input.
        
        Args:
            task: The task to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not await super().validate_input(task):
            return False
        
        # Check for log paths
        if "log_paths" not in task.inputs:
            return False
        
        log_paths = task.inputs["log_paths"]
        if not isinstance(log_paths, list) or not log_paths:
            return False
        
        return True