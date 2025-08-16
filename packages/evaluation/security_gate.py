"""Security Gate - Automated security scanning and vulnerability detection."""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("evaluation.security_gate")


@dataclass
class SecurityConfig:
    """Configuration for security scanning."""

    enable_semgrep: bool = True
    enable_codeql: bool = True
    enable_osv: bool = True
    enable_bandit: bool = True
    fail_on_critical: bool = True
    fail_on_high_severity: bool = True
    fail_on_medium_severity: bool = False
    max_allowed_vulnerabilities: int = 0
    excluded_rules: list[str] = field(default_factory=list)
    excluded_paths: list[str] = field(
        default_factory=lambda: ["tests/", "test_", ".git/", "__pycache__/", ".venv/", "venv/"]
    )
    timeout_seconds: int = 300


@dataclass
class VulnerabilityFinding:
    """Individual vulnerability finding."""

    scanner: str
    rule_id: str
    severity: str  # critical, high, medium, low, info
    file_path: str
    line_number: int
    message: str
    category: str = "security"
    cwe_id: Optional[str] = None
    cve_id: Optional[str] = None
    fix_suggestion: Optional[str] = None

    def is_critical(self) -> bool:
        """Check if finding is critical severity."""
        return self.severity.lower() == "critical"

    def is_high_or_above(self) -> bool:
        """Check if finding is high severity or above."""
        return self.severity.lower() in ["critical", "high", "error"]


@dataclass
class ScanResult:
    """Security scan result."""

    passed: bool = True
    total_findings: int = 0
    critical_count: int = 0
    high_severity_count: int = 0
    medium_severity_count: int = 0
    low_severity_count: int = 0
    info_count: int = 0
    findings: list[VulnerabilityFinding] = field(default_factory=list)
    scan_duration_seconds: float = 0.0
    scanners_used: list[str] = field(default_factory=list)
    error_messages: list[str] = field(default_factory=list)


class SecurityScanner:
    """Individual security scanner implementations."""

    async def run_semgrep(self, target_path: Path) -> list[VulnerabilityFinding]:
        """Run Semgrep static analysis."""
        findings = []

        try:
            cmd = ["semgrep", "--config=auto", "--json", "--no-git-ignore", str(target_path)]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)

                for finding in data.get("results", []):
                    severity_map = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}

                    severity = severity_map.get(
                        finding.get("extra", {}).get("severity", "INFO"), "info"
                    )

                    findings.append(
                        VulnerabilityFinding(
                            scanner="semgrep",
                            rule_id=finding.get("check_id", "unknown"),
                            severity=severity,
                            file_path=finding.get("path", ""),
                            line_number=finding.get("start", {}).get("line", 0),
                            message=finding.get("extra", {}).get("message", ""),
                            cwe_id=self._extract_cwe(finding),
                        )
                    )

        except subprocess.TimeoutExpired:
            logger.warning("Semgrep scan timed out")
        except Exception as e:
            logger.error(f"Semgrep scan failed: {e}")

        return findings

    async def run_codeql(self, target_path: Path) -> list[VulnerabilityFinding]:
        """Run CodeQL analysis."""
        findings = []

        try:
            # Create CodeQL database
            db_path = target_path / ".codeql-db"

            create_cmd = [
                "codeql",
                "database",
                "create",
                str(db_path),
                "--language=python",
                f"--source-root={target_path}",
                "--overwrite",
            ]

            subprocess.run(create_cmd, capture_output=True, timeout=120)

            # Analyze database
            results_file = target_path / "codeql-results.json"
            analyze_cmd = [
                "codeql",
                "database",
                "analyze",
                str(db_path),
                "--format=json",
                f"--output={results_file}",
                "python-security-and-quality.qls",
            ]

            result = subprocess.run(analyze_cmd, capture_output=True, text=True, timeout=180)

            if results_file.exists():
                with open(results_file) as f:
                    data = json.load(f)

                for rule_result in data:
                    for alert in rule_result.get("alerts", []):
                        severity_map = {
                            "error": "high",
                            "warning": "medium",
                            "recommendation": "low",
                        }

                        severity = severity_map.get(
                            rule_result.get("rule", {}).get("severity", ""), "info"
                        )

                        location = alert.get("locations", [{}])[0]
                        physical_loc = location.get("physicalLocation", {})

                        findings.append(
                            VulnerabilityFinding(
                                scanner="codeql",
                                rule_id=rule_result.get("rule", {}).get("id", ""),
                                severity=severity,
                                file_path=physical_loc.get("artifactLocation", {}).get("uri", ""),
                                line_number=physical_loc.get("region", {}).get("startLine", 0),
                                message=alert.get("message", ""),
                            )
                        )

        except subprocess.TimeoutExpired:
            logger.warning("CodeQL scan timed out")
        except Exception as e:
            logger.error(f"CodeQL scan failed: {e}")

        return findings

    async def run_osv(self, target_path: Path) -> list[VulnerabilityFinding]:
        """Run OSV vulnerability scanner for dependencies."""
        findings = []

        try:
            cmd = ["osv-scanner", "--json", str(target_path)]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)

                for result_item in data.get("results", []):
                    for package in result_item.get("packages", []):
                        for vuln in package.get("vulnerabilities", []):
                            severity = "high"  # Default for dependency vulns

                            for sev in vuln.get("severity", []):
                                if sev.get("type") == "CVSS_V3":
                                    score = sev.get("score", "")
                                    if "CRITICAL" in score:
                                        severity = "critical"
                                    elif "HIGH" in score:
                                        severity = "high"
                                    elif "MEDIUM" in score:
                                        severity = "medium"
                                    elif "LOW" in score:
                                        severity = "low"

                            findings.append(
                                VulnerabilityFinding(
                                    scanner="osv",
                                    rule_id=vuln.get("id", ""),
                                    severity=severity,
                                    file_path=result_item.get("source", {}).get("path", ""),
                                    line_number=0,
                                    message=f"{package.get('package', {}).get('name', '')} "
                                    f"v{package.get('package', {}).get('version', '')}: "
                                    f"{vuln.get('summary', '')}",
                                    cve_id=vuln.get("id", "")
                                    if "CVE" in vuln.get("id", "")
                                    else None,
                                )
                            )

        except subprocess.TimeoutExpired:
            logger.warning("OSV scan timed out")
        except Exception as e:
            logger.error(f"OSV scan failed: {e}")

        return findings

    async def run_bandit(self, target_path: Path) -> list[VulnerabilityFinding]:
        """Run Bandit security linter for Python."""
        findings = []

        try:
            cmd = ["bandit", "-r", str(target_path), "-f", "json", "-ll"]  # Only medium and above

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.stdout:
                data = json.loads(result.stdout)

                for finding in data.get("results", []):
                    severity_map = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}

                    findings.append(
                        VulnerabilityFinding(
                            scanner="bandit",
                            rule_id=finding.get("test_id", ""),
                            severity=severity_map.get(finding.get("issue_severity", ""), "info"),
                            file_path=finding.get("filename", ""),
                            line_number=finding.get("line_number", 0),
                            message=finding.get("issue_text", ""),
                            cwe_id=f"CWE-{finding.get('issue_cwe', {}).get('id', '')}"
                            if finding.get("issue_cwe")
                            else None,
                        )
                    )

        except subprocess.TimeoutExpired:
            logger.warning("Bandit scan timed out")
        except Exception as e:
            logger.error(f"Bandit scan failed: {e}")

        return findings

    def _extract_cwe(self, finding: dict[str, Any]) -> Optional[str]:
        """Extract CWE ID from finding metadata."""
        metadata = finding.get("extra", {}).get("metadata", {})
        cwe_list = metadata.get("cwe", [])

        if cwe_list and isinstance(cwe_list, list):
            return cwe_list[0]

        return None


class SecurityGate:
    """Main security gate orchestrator."""

    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize security gate."""
        self.config = config or SecurityConfig()
        self.scanner = SecurityScanner()

    async def scan_codebase(self, target_path: Path) -> ScanResult:
        """Scan entire codebase for security vulnerabilities."""
        start_time = time.time()
        result = ScanResult()
        all_findings = []

        # Run enabled scanners in parallel
        tasks = []

        if self.config.enable_semgrep:
            tasks.append(self.scanner.run_semgrep(target_path))
            result.scanners_used.append("semgrep")

        if self.config.enable_codeql:
            tasks.append(self.scanner.run_codeql(target_path))
            result.scanners_used.append("codeql")

        if self.config.enable_osv:
            tasks.append(self.scanner.run_osv(target_path))
            result.scanners_used.append("osv")

        if self.config.enable_bandit:
            tasks.append(self.scanner.run_bandit(target_path))
            result.scanners_used.append("bandit")

        # Gather results
        if tasks:
            scan_results = await asyncio.gather(*tasks, return_exceptions=True)

            for scan_result in scan_results:
                if isinstance(scan_result, Exception):
                    result.error_messages.append(str(scan_result))
                elif scan_result:
                    all_findings.extend(scan_result)

        # Filter excluded rules
        filtered_findings = self.filter_findings(all_findings)

        # Count by severity
        for finding in filtered_findings:
            severity = finding.severity.lower()

            if severity == "critical":
                result.critical_count += 1
            elif severity in ["high", "error"]:
                result.high_severity_count += 1
            elif severity in ["medium", "warning"]:
                result.medium_severity_count += 1
            elif severity == "low":
                result.low_severity_count += 1
            else:
                result.info_count += 1

        result.findings = filtered_findings
        result.total_findings = len(filtered_findings)

        # Determine pass/fail
        result.passed = not self.should_fail_build(result)

        result.scan_duration_seconds = time.time() - start_time

        return result

    def filter_findings(self, findings: list[VulnerabilityFinding]) -> list[VulnerabilityFinding]:
        """Filter findings based on excluded rules and paths."""
        filtered = []

        for finding in findings:
            # Check excluded rules
            if finding.rule_id in self.config.excluded_rules:
                continue

            # Check excluded paths
            skip = False
            for excluded_path in self.config.excluded_paths:
                if excluded_path in finding.file_path:
                    skip = True
                    break

            if not skip:
                filtered.append(finding)

        return filtered

    def should_fail_build(self, result: ScanResult) -> bool:
        """Determine if build should fail based on findings."""
        if result.critical_count > 0 and self.config.fail_on_critical:
            return True

        if result.high_severity_count > 0 and self.config.fail_on_high_severity:
            return True

        if result.medium_severity_count > 0 and self.config.fail_on_medium_severity:
            return True

        if result.total_findings > self.config.max_allowed_vulnerabilities:
            return True

        return False

    async def generate_report(self, result: ScanResult) -> str:
        """Generate human-readable security report."""
        report = ["# Security Scan Report\n"]

        # Summary
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        report.append(f"## Status: {status}\n")

        report.append(f"**Scan Duration:** {result.scan_duration_seconds:.2f} seconds\n")
        report.append(f"**Scanners Used:** {', '.join(result.scanners_used)}\n")
        report.append(f"**Total Findings:** {result.total_findings}\n")

        # Breakdown by severity
        report.append("\n## Severity Breakdown\n")
        report.append(f"- Critical: {result.critical_count}")
        report.append(f"- High: {result.high_severity_count}")
        report.append(f"- Medium: {result.medium_severity_count}")
        report.append(f"- Low: {result.low_severity_count}")
        report.append(f"- Info: {result.info_count}")

        # Detailed findings
        if result.findings:
            report.append("\n## Detailed Findings\n")

            # Group by severity
            for severity in ["critical", "high", "medium", "low", "info"]:
                severity_findings = [f for f in result.findings if f.severity.lower() == severity]

                if severity_findings:
                    report.append(f"\n### {severity.upper()} Severity\n")

                    for finding in severity_findings:
                        report.append(f"\n**[{finding.scanner}] {finding.rule_id}**")
                        report.append(f"- File: `{finding.file_path}:{finding.line_number}`")
                        report.append(f"- Message: {finding.message}")

                        if finding.cwe_id:
                            report.append(f"- CWE: {finding.cwe_id}")
                        if finding.cve_id:
                            report.append(f"- CVE: {finding.cve_id}")
                        if finding.fix_suggestion:
                            report.append(f"- Fix: {finding.fix_suggestion}")

        # Errors
        if result.error_messages:
            report.append("\n## Errors\n")
            for error in result.error_messages:
                report.append(f"- {error}")

        return "\n".join(report)

    async def create_github_comment(self, result: ScanResult) -> str:
        """Create GitHub PR comment with scan results."""
        status_emoji = "✅" if result.passed else "❌"
        status_text = "**PASSED**" if result.passed else "**FAILED**"

        comment = [
            "## 🔒 Security Scan Results\n",
            f"{status_emoji} {status_text}\n",
            f"**Total Vulnerabilities:** {result.total_findings}\n",
        ]

        if result.critical_count > 0:
            comment.append(f"🔴 **Critical:** {result.critical_count}")
        if result.high_severity_count > 0:
            comment.append(f"🟠 **High:** {result.high_severity_count}")
        if result.medium_severity_count > 0:
            comment.append(f"🟡 **Medium:** {result.medium_severity_count}")
        if result.low_severity_count > 0:
            comment.append(f"🟢 **Low:** {result.low_severity_count}")

        # Add top 3 critical/high findings
        critical_high = [f for f in result.findings if f.severity.lower() in ["critical", "high"]][
            :3
        ]

        if critical_high:
            comment.append("\n### ⚠️ Top Security Issues\n")

            for finding in critical_high:
                comment.append(
                    f"- **{finding.severity.upper()}**: {finding.message} "
                    f"(`{finding.file_path}:{finding.line_number}`)"
                )

        if not result.passed:
            comment.append(
                "\n❗ **Action Required:** Please fix security vulnerabilities before merging."
            )

        return "\n".join(comment)
