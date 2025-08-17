"""Tests for Security Gate - Automated security scanning and validation."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from packages.evaluation.security_gate import (
    ScanResult,
    SecurityConfig,
    SecurityGate,
    SecurityScanner,
    VulnerabilityFinding,
)


class TestSecurityConfig:
    """Test security configuration."""

    def test_default_config(self):
        """Test default security configuration."""
        config = SecurityConfig()

        assert config.enable_semgrep is True
        assert config.enable_codeql is True
        assert config.enable_osv is True
        assert config.fail_on_high_severity is True
        assert config.fail_on_medium_severity is False
        assert config.max_allowed_vulnerabilities == 0
        assert config.excluded_rules == []

    def test_custom_config(self):
        """Test custom security configuration."""
        config = SecurityConfig(
            enable_semgrep=True,
            enable_codeql=False,
            fail_on_medium_severity=True,
            max_allowed_vulnerabilities=5,
            excluded_rules=["generic.secrets.security.detected-private-key"],
        )

        assert config.enable_codeql is False
        assert config.fail_on_medium_severity is True
        assert config.max_allowed_vulnerabilities == 5
        assert len(config.excluded_rules) == 1


class TestVulnerabilityFinding:
    """Test vulnerability finding data model."""

    def test_finding_creation(self):
        """Test creating vulnerability finding."""
        finding = VulnerabilityFinding(
            scanner="semgrep",
            rule_id="python.lang.security.audit.subprocess",
            severity="high",
            file_path="src/main.py",
            line_number=42,
            message="Subprocess call with shell=True",
            category="security",
            cwe_id="CWE-78",
        )

        assert finding.scanner == "semgrep"
        assert finding.severity == "high"
        assert finding.line_number == 42
        assert finding.cwe_id == "CWE-78"

    def test_finding_is_critical(self):
        """Test severity classification."""
        critical = VulnerabilityFinding(
            scanner="test",
            rule_id="test",
            severity="critical",
            file_path="test.py",
            line_number=1,
            message="Test",
        )

        high = VulnerabilityFinding(
            scanner="test",
            rule_id="test",
            severity="high",
            file_path="test.py",
            line_number=1,
            message="Test",
        )

        assert critical.is_critical() is True
        assert high.is_critical() is False
        assert critical.is_high_or_above() is True
        assert high.is_high_or_above() is True


class TestSecurityScanner:
    """Test individual security scanners."""

    @pytest.fixture
    def scanner(self):
        """Create security scanner instance."""
        return SecurityScanner()

    @pytest.mark.asyncio
    async def test_run_semgrep(self, scanner, tmp_path):
        """Test running Semgrep scanner."""
        # Create test Python file with potential security issue
        test_file = tmp_path / "vulnerable.py"
        test_file.write_text(
            """
import subprocess
import os

def run_command(user_input):
    # Security issue: shell injection
    subprocess.run(user_input, shell=True)

    # Security issue: hardcoded password
    password = "hardcoded_password_123"

    # Security issue: SQL injection
    query = f"SELECT * FROM users WHERE id = {user_input}"
"""
        )

        # Mock subprocess run
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(
                {
                    "results": [
                        {
                            "check_id": "python.lang.security.audit.subprocess-shell-true",
                            "path": str(test_file),
                            "start": {"line": 7},
                            "extra": {
                                "message": "subprocess call with shell=True",
                                "severity": "ERROR",
                                "metadata": {"cwe": ["CWE-78"]},
                            },
                        }
                    ]
                }
            )

            findings = await scanner.run_semgrep(tmp_path)

            assert len(findings) > 0
            assert findings[0].severity == "high"
            assert "subprocess" in findings[0].message.lower()

    @pytest.mark.asyncio
    async def test_run_codeql(self, scanner, tmp_path):
        """Test running CodeQL scanner."""
        # Mock CodeQL database and analysis
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(
                [
                    {
                        "rule": {"id": "py/sql-injection", "severity": "error"},
                        "message": "SQL injection vulnerability",
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "src/db.py"},
                                    "region": {"startLine": 15},
                                }
                            }
                        ],
                    }
                ]
            )

            findings = await scanner.run_codeql(tmp_path)

            assert len(findings) > 0
            assert findings[0].rule_id == "py/sql-injection"

    @pytest.mark.asyncio
    async def test_run_osv_scanner(self, scanner, tmp_path):
        """Test running OSV vulnerability scanner."""
        # Create requirements.txt with known vulnerable package
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("django==2.2.0\nrequests==2.25.0")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(
                {
                    "results": [
                        {
                            "source": {"path": str(requirements), "type": "requirements"},
                            "packages": [
                                {
                                    "package": {"name": "django", "version": "2.2.0"},
                                    "vulnerabilities": [
                                        {
                                            "id": "GHSA-xxxx-yyyy-zzzz",
                                            "summary": "Django SQL injection",
                                            "severity": [{"type": "CVSS_V3", "score": "HIGH"}],
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                }
            )

            findings = await scanner.run_osv(tmp_path)

            assert len(findings) > 0
            assert "django" in findings[0].message.lower()


class TestSecurityGate:
    """Test main security gate orchestrator."""

    @pytest.fixture
    def gate(self):
        """Create security gate instance."""
        config = SecurityConfig()
        return SecurityGate(config)

    @pytest.mark.asyncio
    async def test_scan_codebase(self, gate, tmp_path):
        """Test scanning entire codebase."""
        # Create test files
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text(
            """
def safe_function():
    return "Hello, World!"
"""
        )

        # Mock scanner results
        gate.scanner = AsyncMock()
        gate.scanner.run_semgrep.return_value = []
        gate.scanner.run_codeql.return_value = []
        gate.scanner.run_osv.return_value = []

        result = await gate.scan_codebase(tmp_path)

        assert result.passed is True
        assert result.total_findings == 0
        assert len(result.findings) == 0

    @pytest.mark.asyncio
    async def test_scan_with_findings(self, gate, tmp_path):
        """Test scanning with security findings."""
        # Mock scanner to return findings
        gate.scanner = AsyncMock()

        high_finding = VulnerabilityFinding(
            scanner="semgrep",
            rule_id="test-high",
            severity="high",
            file_path="test.py",
            line_number=10,
            message="High severity issue",
        )

        gate.scanner.run_semgrep.return_value = [high_finding]
        gate.scanner.run_codeql.return_value = []
        gate.scanner.run_osv.return_value = []

        result = await gate.scan_codebase(tmp_path)

        assert result.passed is False  # Fails due to high severity
        assert result.total_findings == 1
        assert result.high_severity_count == 1

    @pytest.mark.asyncio
    async def test_filter_excluded_rules(self, gate):
        """Test filtering excluded rules."""
        findings = [
            VulnerabilityFinding(
                scanner="semgrep",
                rule_id="excluded.rule",
                severity="high",
                file_path="test.py",
                line_number=1,
                message="Should be excluded",
            ),
            VulnerabilityFinding(
                scanner="semgrep",
                rule_id="included.rule",
                severity="high",
                file_path="test.py",
                line_number=2,
                message="Should be included",
            ),
        ]

        gate.config.excluded_rules = ["excluded.rule"]
        filtered = gate.filter_findings(findings)

        assert len(filtered) == 1
        assert filtered[0].rule_id == "included.rule"

    @pytest.mark.asyncio
    async def test_generate_report(self, gate):
        """Test generating security report."""
        result = ScanResult(
            passed=False,
            total_findings=2,
            critical_count=1,
            high_severity_count=1,
            medium_severity_count=0,
            low_severity_count=0,
            findings=[
                VulnerabilityFinding(
                    scanner="semgrep",
                    rule_id="python.security.injection",
                    severity="critical",
                    file_path="src/db.py",
                    line_number=42,
                    message="SQL injection vulnerability",
                    category="security",
                    cwe_id="CWE-89",
                )
            ],
            scan_duration_seconds=5.2,
        )

        report = await gate.generate_report(result)

        assert "Security Scan Report" in report
        assert "FAILED" in report
        assert "Critical: 1" in report
        assert "SQL injection" in report
        assert "src/db.py:42" in report

    @pytest.mark.asyncio
    async def test_create_github_comment(self, gate):
        """Test creating GitHub PR comment."""
        result = ScanResult(
            passed=False,
            total_findings=1,
            high_severity_count=1,
            findings=[
                VulnerabilityFinding(
                    scanner="codeql",
                    rule_id="py/path-injection",
                    severity="high",
                    file_path="src/files.py",
                    line_number=15,
                    message="Path injection vulnerability",
                )
            ],
        )

        comment = await gate.create_github_comment(result)

        assert "## 🔒 Security Scan Results" in comment
        assert "❌ **FAILED**" in comment
        assert "Path injection" in comment
        assert "src/files.py" in comment

    def test_should_fail_build(self, gate):
        """Test build failure decision logic."""
        # Should fail on critical
        result_critical = ScanResult(passed=False, critical_count=1, findings=[])
        assert gate.should_fail_build(result_critical) is True

        # Should fail on high if configured
        gate.config.fail_on_high_severity = True
        result_high = ScanResult(passed=False, high_severity_count=1, findings=[])
        assert gate.should_fail_build(result_high) is True

        # Should not fail on medium by default
        result_medium = ScanResult(passed=False, medium_severity_count=1, findings=[])
        assert gate.should_fail_build(result_medium) is False

        # Should fail if exceeds max vulnerabilities
        gate.config.max_allowed_vulnerabilities = 2
        result_many = ScanResult(passed=False, total_findings=3, findings=[])
        assert gate.should_fail_build(result_many) is True
