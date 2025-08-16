"""Tests for SecurityScanner Agent Integration via A2A.

Phase 4: P4-T2 - SecurityScanner Agent Integration
"""

from unittest.mock import patch

import pytest

from packages.a2a.agents.security_scanner import (
    AutoFixer,
    Finding,
    FixValidation,
    RemediationEngine,
    ScanRequest,
    ScanResult,
    SecurityScannerAgent,
    Severity,
)


class TestSecurityScannerAgent:
    """Test SecurityScanner agent integration."""

    @pytest.fixture
    def scanner(self):
        """Create security scanner agent."""
        return SecurityScannerAgent(
            agent_id="security-scanner-v1", endpoint="https://security.example.com"
        )

    def test_agent_registration(self, scanner):
        """Test agent registration with capabilities."""
        capabilities = scanner.get_capabilities()

        assert len(capabilities) > 0
        assert any(cap.name == "vulnerability_scan" for cap in capabilities)
        assert any(cap.name == "dependency_check" for cap in capabilities)
        assert any(cap.name == "secret_detection" for cap in capabilities)

    @pytest.mark.asyncio
    async def test_scan_request_adapter(self, scanner):
        """Test adapting scan requests to agent format."""
        request = ScanRequest(
            repository="https://github.com/example/repo",
            branch="main",
            scan_types=["vulnerability", "secrets"],
            severity_threshold=Severity.MEDIUM,
        )

        adapted = await scanner.adapt_request(request)

        assert adapted["repository"] == request.repository
        assert adapted["branch"] == request.branch
        assert "vulnerability" in adapted["scan_types"]
        assert adapted["min_severity"] == "MEDIUM"

    @pytest.mark.asyncio
    async def test_parse_scan_results(self, scanner):
        """Test parsing scan results from agent."""
        raw_results = {
            "findings": [
                {
                    "type": "vulnerability",
                    "severity": "HIGH",
                    "title": "SQL Injection",
                    "file": "app.py",
                    "line": 42,
                    "description": "User input not sanitized",
                    "cve": "CVE-2021-12345",
                },
                {
                    "type": "secret",
                    "severity": "CRITICAL",
                    "title": "API Key Exposed",
                    "file": ".env",
                    "line": 5,
                    "description": "Hardcoded API key found",
                },
            ],
            "summary": {"total": 2, "critical": 1, "high": 1},
        }

        result = await scanner.parse_results(raw_results)

        assert isinstance(result, ScanResult)
        assert len(result.findings) == 2
        assert result.findings[0].severity == Severity.HIGH
        assert result.findings[1].severity == Severity.CRITICAL
        assert result.summary["total"] == 2

    @pytest.mark.asyncio
    async def test_vulnerability_scan(self, scanner, tmp_path):
        """Test vulnerability scanning."""
        # Create test file with vulnerability
        test_file = tmp_path / "vulnerable.py"
        test_file.write_text(
            """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()
"""
        )

        # Mock agent response
        with patch.object(scanner, "_call_agent") as mock_call:
            mock_call.return_value = {
                "findings": [
                    {"type": "sql_injection", "severity": "HIGH", "file": str(test_file), "line": 7}
                ]
            }

            result = await scanner.scan_vulnerabilities(tmp_path)

            assert len(result.findings) > 0
            assert result.findings[0].type == "sql_injection"

    @pytest.mark.asyncio
    async def test_secret_detection(self, scanner, tmp_path):
        """Test secret detection in code."""
        # Create file with secret
        config_file = tmp_path / "config.py"
        config_file.write_text(
            """
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "super_secret_password"
"""
        )

        # Mock agent response
        with patch.object(scanner, "_call_agent") as mock_call:
            mock_call.return_value = {
                "findings": [
                    {
                        "type": "secret",
                        "severity": "CRITICAL",
                        "file": str(config_file),
                        "line": 2,
                        "secret_type": "api_key",
                    },
                    {
                        "type": "secret",
                        "severity": "HIGH",
                        "file": str(config_file),
                        "line": 3,
                        "secret_type": "password",
                    },
                ]
            }

            result = await scanner.scan_secrets(tmp_path)

            assert len(result.findings) == 2
            assert all(f.type == "secret" for f in result.findings)

    @pytest.mark.asyncio
    async def test_dependency_scan(self, scanner, tmp_path):
        """Test dependency vulnerability scanning."""
        # Create requirements file
        req_file = tmp_path / "requirements.txt"
        req_file.write_text(
            """
flask==1.0.2
requests==2.20.0
django==2.0.0
"""
        )

        # Mock agent response with vulnerabilities
        with patch.object(scanner, "_call_agent") as mock_call:
            mock_call.return_value = {
                "findings": [
                    {
                        "type": "dependency",
                        "severity": "HIGH",
                        "package": "flask",
                        "version": "1.0.2",
                        "vulnerability": "CVE-2019-1010083",
                        "fixed_version": "1.0.3",
                    }
                ]
            }

            result = await scanner.scan_dependencies(tmp_path)

            assert len(result.findings) > 0
            assert result.findings[0].type == "dependency"


class TestRemediationEngine:
    """Test automated remediation functionality."""

    @pytest.fixture
    def engine(self):
        """Create remediation engine."""
        return RemediationEngine()

    @pytest.mark.asyncio
    async def test_build_fix_suggestions(self, engine):
        """Test building fix suggestions for findings."""
        findings = [
            Finding(
                type="sql_injection",
                severity=Severity.HIGH,
                file="app.py",
                line=10,
                description="SQL injection vulnerability",
            ),
            Finding(
                type="secret",
                severity=Severity.CRITICAL,
                file="config.py",
                line=5,
                description="Hardcoded API key",
            ),
        ]

        suggestions = await engine.build_suggestions(findings)

        assert len(suggestions) == 2
        assert suggestions[0]["finding_type"] == "sql_injection"
        assert "parameterized" in suggestions[0]["fix_description"].lower()
        assert suggestions[1]["finding_type"] == "secret"
        assert "environment" in suggestions[1]["fix_description"].lower()

    @pytest.mark.asyncio
    async def test_generate_patches(self, engine, tmp_path):
        """Test generating patches for vulnerabilities."""
        # Create vulnerable file
        vuln_file = tmp_path / "vulnerable.py"
        vuln_file.write_text(
            """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute(query)
"""
        )

        finding = Finding(
            type="sql_injection",
            severity=Severity.HIGH,
            file=str(vuln_file),
            line=2,
            description="SQL injection",
        )

        patch = await engine.generate_patch(finding)

        assert patch is not None
        assert "old_code" in patch
        assert "new_code" in patch
        assert "?" in patch["new_code"]  # Parameterized query


class TestAutoFixer:
    """Test automatic fix application."""

    @pytest.fixture
    def fixer(self):
        """Create auto fixer."""
        return AutoFixer()

    @pytest.mark.asyncio
    async def test_auto_fix_sql_injection(self, fixer, tmp_path):
        """Test auto-fixing SQL injection."""
        # Create vulnerable file
        file_path = tmp_path / "db.py"
        file_path.write_text(
            """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()
"""
        )

        finding = Finding(
            type="sql_injection",
            severity=Severity.HIGH,
            file=str(file_path),
            line=6,
            description="SQL injection vulnerability",
        )

        fixed = await fixer.fix(finding)

        assert fixed is True

        # Check file was modified
        content = file_path.read_text()
        assert "?" in content  # Parameterized query marker
        assert "execute(query, " in content  # Parameters passed separately

    @pytest.mark.asyncio
    async def test_auto_fix_hardcoded_secret(self, fixer, tmp_path):
        """Test auto-fixing hardcoded secrets."""
        # Create file with secret
        file_path = tmp_path / "config.py"
        file_path.write_text(
            """
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:pass@localhost/db"
"""
        )

        finding = Finding(
            type="secret",
            severity=Severity.CRITICAL,
            file=str(file_path),
            line=1,
            description="Hardcoded API key",
        )

        fixed = await fixer.fix(finding)

        assert fixed is True

        # Check file was modified
        content = file_path.read_text()
        assert "os.environ" in content or "getenv" in content
        assert "sk-1234567890abcdef" not in content

    @pytest.mark.asyncio
    async def test_fix_with_backup(self, fixer, tmp_path):
        """Test that fixes create backups."""
        file_path = tmp_path / "test.py"
        original_content = "original content"
        file_path.write_text(original_content)

        finding = Finding(
            type="test",
            severity=Severity.LOW,
            file=str(file_path),
            line=1,
            description="Test finding",
        )

        with patch.object(fixer, "_apply_fix") as mock_apply:
            mock_apply.return_value = True
            await fixer.fix(finding, create_backup=True)

        # Check backup was created
        backup_files = list(tmp_path.glob("*.backup"))
        assert len(backup_files) > 0


class TestFixValidation:
    """Test fix validation functionality."""

    @pytest.fixture
    def validator(self):
        """Create fix validator."""
        return FixValidation()

    @pytest.mark.asyncio
    async def test_validate_fix(self, validator, tmp_path):
        """Test validating that a fix resolved the issue."""
        # Create fixed file
        file_path = tmp_path / "fixed.py"
        file_path.write_text(
            """
import os

API_KEY = os.environ.get('API_KEY')
"""
        )

        finding = Finding(
            type="secret",
            severity=Severity.CRITICAL,
            file=str(file_path),
            line=3,
            description="Hardcoded secret (now fixed)",
        )

        # Mock re-scan showing no findings
        with patch.object(validator, "_rescan") as mock_rescan:
            mock_rescan.return_value = []

            is_fixed = await validator.validate(finding)

            assert is_fixed is True

    @pytest.mark.asyncio
    async def test_validate_partial_fix(self, validator):
        """Test detecting partial fixes."""
        finding = Finding(
            type="sql_injection",
            severity=Severity.HIGH,
            file="app.py",
            line=10,
            description="Multiple SQL injections",
        )

        # Mock re-scan still showing the SAME finding at SAME location
        with patch.object(validator, "_rescan") as mock_rescan:
            mock_rescan.return_value = [
                Finding(
                    type="sql_injection",
                    severity=Severity.HIGH,
                    file="app.py",
                    line=10,  # Same line - not fixed
                    description="SQL injection still present",
                )
            ]

            is_fixed = await validator.validate(finding)

            assert is_fixed is False  # Not fixed - same issue at same location

    @pytest.mark.asyncio
    async def test_validate_with_tests(self, validator):
        """Test running tests after fix to ensure nothing broke."""
        finding = Finding(
            type="vulnerability",
            severity=Severity.MEDIUM,
            file="src/main.py",
            line=20,
            description="Fixed vulnerability",
        )

        # Mock test execution
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0  # Tests pass

            is_valid = await validator.validate_with_tests(finding)

            assert is_valid is True
            mock_run.assert_called_once()
