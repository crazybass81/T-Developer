"""
Log Aggregator and Analyzer
Day 5: TDD Implementation - GREEN Phase
Generated: 2024-11-18

Aggregates and analyzes logs from Evolution System components
"""

import json
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional

import boto3

logger = logging.getLogger(__name__)


class LogAggregator:
    """Aggregate and analyze system logs"""

    def __init__(self, region: str = "us-east-1"):
        """Initialize log aggregator"""
        self.region = region
        self.logs = []
        self.aggregated_data = {}

        # Initialize CloudWatch Logs client
        try:
            self.cloudwatch_logs = boto3.client("logs", region_name=region)
        except Exception as e:
            logger.warning(f"CloudWatch Logs client initialization failed: {e}")
            self.cloudwatch_logs = None

        # Patterns for log parsing
        self.patterns = {
            "instantiation": re.compile(r"Agent (\S+) instantiated in ([\d.]+)μs"),
            "memory": re.compile(r"Memory usage for (\S+): ([\d.]+)KB"),
            "error": re.compile(r"Error: (.+)"),
            "warning": re.compile(r"Warning: (.+)"),
            "evolution_cycle": re.compile(r"Evolution cycle (\d+) completed"),
            "fitness": re.compile(r"Fitness score: ([\d.]+)"),
            "safety_violation": re.compile(r"Safety violation: (.+)"),
            "memory_limit": re.compile(r"Memory limit exceeded"),
        }

    def add_log(self, log_entry: Dict):
        """Add a log entry"""
        if "timestamp" not in log_entry:
            log_entry["timestamp"] = datetime.utcnow().isoformat()

        self.logs.append(log_entry)

    def aggregate(self, logs: Optional[List[Dict]] = None) -> Dict:
        """Aggregate logs by component"""
        if logs is None:
            logs = self.logs

        aggregated = defaultdict(
            lambda: {
                "total_count": 0,
                "error_count": 0,
                "warn_count": 0,
                "info_count": 0,
                "debug_count": 0,
                "messages": [],
            }
        )

        for log in logs:
            component = log.get("component", "unknown")
            level = log.get("level", "INFO").upper()

            aggregated[component]["total_count"] += 1

            if level == "ERROR":
                aggregated[component]["error_count"] += 1
            elif level == "WARN" or level == "WARNING":
                aggregated[component]["warn_count"] += 1
            elif level == "INFO":
                aggregated[component]["info_count"] += 1
            elif level == "DEBUG":
                aggregated[component]["debug_count"] += 1

            aggregated[component]["messages"].append(
                {
                    "level": level,
                    "message": log.get("message", ""),
                    "timestamp": log.get("timestamp"),
                }
            )

        self.aggregated_data = dict(aggregated)
        return self.aggregated_data

    def extract_patterns(self, logs: Optional[List[Dict]] = None) -> Dict:
        """Extract patterns from log messages"""
        if logs is None:
            logs = self.logs

        extracted = {
            "instantiation_times": [],
            "memory_usage": [],
            "evolution_cycles": [],
            "fitness_scores": [],
            "error_patterns": defaultdict(int),
            "warning_patterns": defaultdict(int),
            "safety_violations": [],
        }

        for log in logs:
            message = log.get("message", "")

            # Extract instantiation times
            match = self.patterns["instantiation"].search(message)
            if match:
                extracted["instantiation_times"].append(
                    {"agent": match.group(1), "time_us": float(match.group(2))}
                )

            # Extract memory usage
            match = self.patterns["memory"].search(message)
            if match:
                extracted["memory_usage"].append(
                    {"agent": match.group(1), "memory_kb": float(match.group(2))}
                )

            # Extract evolution cycles
            match = self.patterns["evolution_cycle"].search(message)
            if match:
                extracted["evolution_cycles"].append(int(match.group(1)))

            # Extract fitness scores
            match = self.patterns["fitness"].search(message)
            if match:
                extracted["fitness_scores"].append(float(match.group(1)))

            # Extract errors
            match = self.patterns["error"].search(message)
            if match:
                extracted["error_patterns"][match.group(1)] += 1

            # Extract warnings
            match = self.patterns["warning"].search(message)
            if match:
                extracted["warning_patterns"][match.group(1)] += 1

            # Extract safety violations
            match = self.patterns["safety_violation"].search(message)
            if match:
                extracted["safety_violations"].append(match.group(1))

            # Check for memory limit exceeded
            if self.patterns["memory_limit"].search(message):
                extracted["error_patterns"]["memory_limit_exceeded"] += 1

        return extracted

    def send_to_cloudwatch(self, log_group: str, log_stream: str, events: List[Dict]) -> Dict:
        """Send logs to CloudWatch Logs"""
        if not self.cloudwatch_logs:
            return {"success": False, "error": "CloudWatch Logs client not initialized"}

        try:
            # Ensure log stream exists
            try:
                self.cloudwatch_logs.create_log_stream(
                    logGroupName=log_group, logStreamName=log_stream
                )
            except self.cloudwatch_logs.exceptions.ResourceAlreadyExistsException:
                pass  # Stream already exists

            # Prepare log events
            log_events = []
            for event in events:
                if isinstance(event.get("timestamp"), str):
                    # Parse ISO format timestamp
                    timestamp = int(
                        datetime.fromisoformat(
                            event["timestamp"].replace("Z", "+00:00")
                        ).timestamp()
                        * 1000
                    )
                else:
                    timestamp = event.get("timestamp", int(datetime.utcnow().timestamp() * 1000))

                log_events.append(
                    {"timestamp": timestamp, "message": event.get("message", json.dumps(event))}
                )

            # Send to CloudWatch
            response = self.cloudwatch_logs.put_log_events(
                logGroupName=log_group, logStreamName=log_stream, logEvents=log_events
            )

            return {"success": True, "response": response}

        except Exception as e:
            logger.error(f"Failed to send logs to CloudWatch: {e}")
            return {"success": False, "error": str(e)}

    def get_aggregated_logs(self) -> Dict:
        """Get aggregated logs"""
        if not self.aggregated_data:
            self.aggregate()
        return self.aggregated_data

    def analyze_error_trends(self, time_window_minutes: int = 60) -> Dict:
        """Analyze error trends over time"""
        from datetime import timedelta

        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=time_window_minutes)

        # Filter recent logs
        recent_logs = []
        for log in self.logs:
            try:
                log_time = datetime.fromisoformat(log.get("timestamp", "").replace("Z", "+00:00"))
                if log_time >= cutoff_time:
                    recent_logs.append(log)
            except Exception:
                continue

        # Count errors by component
        error_counts = defaultdict(int)
        error_messages = defaultdict(list)

        for log in recent_logs:
            if log.get("level", "").upper() == "ERROR":
                component = log.get("component", "unknown")
                error_counts[component] += 1
                error_messages[component].append(log.get("message", ""))

        # Identify trending errors
        trending_errors = []
        for component, count in error_counts.items():
            if count >= 3:  # Threshold for trending
                trending_errors.append(
                    {
                        "component": component,
                        "count": count,
                        "sample_messages": error_messages[component][:3],
                    }
                )

        return {
            "time_window_minutes": time_window_minutes,
            "total_errors": sum(error_counts.values()),
            "errors_by_component": dict(error_counts),
            "trending_errors": trending_errors,
        }

    def get_summary_statistics(self) -> Dict:
        """Get summary statistics for logs"""
        total_logs = len(self.logs)

        if total_logs == 0:
            return {"total_logs": 0}

        # Count by level
        level_counts = Counter(log.get("level", "INFO").upper() for log in self.logs)

        # Count by component
        component_counts = Counter(log.get("component", "unknown") for log in self.logs)

        # Extract patterns
        patterns = self.extract_patterns()

        return {
            "total_logs": total_logs,
            "level_distribution": dict(level_counts),
            "component_distribution": dict(component_counts),
            "error_rate": level_counts.get("ERROR", 0) / total_logs,
            "warning_rate": level_counts.get("WARN", 0) / total_logs,
            "instantiation_count": len(patterns["instantiation_times"]),
            "avg_instantiation_time": (
                sum(t["time_us"] for t in patterns["instantiation_times"])
                / len(patterns["instantiation_times"])
            )
            if patterns["instantiation_times"]
            else 0,
            "safety_violation_count": len(patterns["safety_violations"]),
            "unique_error_types": len(patterns["error_patterns"]),
        }

    def export_for_analysis(self) -> Dict:
        """Export aggregated data for analysis"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": self.get_summary_statistics(),
            "aggregated": self.get_aggregated_logs(),
            "patterns": self.extract_patterns(),
            "error_trends": self.analyze_error_trends(),
        }

    def clear_logs(self):
        """Clear stored logs"""
        self.logs = []
        self.aggregated_data = {}
