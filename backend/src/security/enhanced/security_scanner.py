"""SecurityScanner - Day 39
Code security scanning and vulnerability patching - Size: ~6.5KB"""
import ast
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class VulnerabilityLevel(Enum):
    """Vulnerability severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityScanner:
    """Scan generated code for vulnerabilities - Size optimized to 6.5KB"""

    def __init__(self):
        self.vulnerabilities = []
        self.patches = []
        self.audit_log = []
        self.patterns = {
            # SQL Injection patterns
            "sql_injection": [
                r"f['\"].*SELECT.*{.*}",
                r"\".*SELECT.*\" \+ ",
                r"query = .*\+ input",
            ],
            # Command Injection
            "command_injection": [
                r"os\.system\(",
                r"subprocess\.call\(.*shell=True",
                r"eval\(",
                r"exec\(",
            ],
            # Path Traversal
            "path_traversal": [r"\.\.\/", r"open\(.*user_input", r"os\.path\.join\(.*request\."],
            # Hardcoded secrets
            "hardcoded_secrets": [
                r"password\s*=\s*['\"].*['\"]",
                r"api_key\s*=\s*['\"].*['\"]",
                r"secret\s*=\s*['\"].*['\"]",
            ],
            # XSS
            "xss": [r"innerHTML\s*=", r"document\.write\(", r"\.html\(.*user"],
        }
        self.permissions = {"read": [], "write": [], "execute": [], "admin": []}

    def scan_code(self, code: str, filename: str = "unknown") -> Dict[str, Any]:
        """Scan code for vulnerabilities"""
        scan_result = {
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "risk_score": 0,
        }

        # Pattern-based scanning
        for vuln_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    vuln = {
                        "type": vuln_type,
                        "level": self._determine_level(vuln_type),
                        "line": code[: match.start()].count("\n") + 1,
                        "code": match.group()[:50],  # Truncate for size
                        "description": self._get_description(vuln_type),
                    }
                    scan_result["vulnerabilities"].append(vuln)
                    self.vulnerabilities.append(vuln)

        # AST-based scanning for Python code
        if filename.endswith(".py"):
            ast_vulns = self._scan_ast(code)
            scan_result["vulnerabilities"].extend(ast_vulns)

        # Calculate risk score
        scan_result["risk_score"] = self._calculate_risk_score(scan_result["vulnerabilities"])

        # Log scan
        self._log_audit(
            "scan", {"filename": filename, "vulnerabilities": len(scan_result["vulnerabilities"])}
        )

        # Auto-patch if critical
        if scan_result["risk_score"] > 80:
            patches = self.auto_patch(code, scan_result["vulnerabilities"])
            scan_result["patches"] = patches

        return scan_result

    def _scan_ast(self, code: str) -> List[Dict[str, Any]]:
        """AST-based vulnerability scanning"""
        vulns = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Check for dangerous functions
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["eval", "exec", "__import__"]:
                            vulns.append(
                                {
                                    "type": "dangerous_function",
                                    "level": VulnerabilityLevel.HIGH,
                                    "line": node.lineno if hasattr(node, "lineno") else 0,
                                    "code": node.func.id,
                                    "description": f"Dangerous function: {node.func.id}",
                                }
                            )

                # Check for assert in production
                if isinstance(node, ast.Assert):
                    vulns.append(
                        {
                            "type": "assert_in_production",
                            "level": VulnerabilityLevel.LOW,
                            "line": node.lineno if hasattr(node, "lineno") else 0,
                            "code": "assert",
                            "description": "Assert statements should not be used in production",
                        }
                    )
        except:
            pass  # If AST parsing fails, continue with pattern matching

        return vulns

    def auto_patch(self, code: str, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Automatically patch vulnerabilities"""
        patches = []
        patched_code = code

        for vuln in vulnerabilities:
            if vuln["level"] in [VulnerabilityLevel.CRITICAL, VulnerabilityLevel.HIGH]:
                patch = self._generate_patch(vuln, code)
                if patch:
                    patches.append(patch)
                    patched_code = self._apply_patch(patched_code, patch)
                    self.patches.append(patch)

        return patches

    def _generate_patch(self, vuln: Dict[str, Any], code: str) -> Optional[Dict[str, Any]]:
        """Generate patch for vulnerability"""
        patch = {"vulnerability": vuln, "timestamp": datetime.now().isoformat()}

        if vuln["type"] == "sql_injection":
            patch["fix"] = "Use parameterized queries"
            patch["code"] = "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
        elif vuln["type"] == "command_injection":
            patch["fix"] = "Use subprocess with list arguments"
            patch["code"] = "subprocess.run(['command', 'arg'], check=True)"
        elif vuln["type"] == "hardcoded_secrets":
            patch["fix"] = "Use environment variables"
            patch["code"] = "password = os.environ.get('PASSWORD')"
        elif vuln["type"] == "path_traversal":
            patch["fix"] = "Validate and sanitize paths"
            patch["code"] = "safe_path = os.path.normpath(os.path.join(base_dir, user_input))"
        else:
            return None

        return patch

    def _apply_patch(self, code: str, patch: Dict[str, Any]) -> str:
        """Apply patch to code"""
        # Simple replacement for demonstration
        vuln_code = patch["vulnerability"]["code"]
        patch_code = patch["code"]

        if vuln_code in code:
            return code.replace(vuln_code, patch_code)

        return code

    def check_permissions(self, user_id: str, resource: str, action: str) -> bool:
        """Check user permissions"""
        # Check if user has permission for action on resource
        if action == "admin":
            return user_id in self.permissions["admin"]
        elif action == "write":
            return user_id in self.permissions["write"] or user_id in self.permissions["admin"]
        elif action == "execute":
            return user_id in self.permissions["execute"] or user_id in self.permissions["admin"]
        else:  # read
            return (
                user_id in self.permissions["read"]
                or user_id in self.permissions["write"]
                or user_id in self.permissions["admin"]
            )

    def grant_permission(self, user_id: str, permission: str) -> Dict[str, Any]:
        """Grant permission to user"""
        if permission in self.permissions:
            if user_id not in self.permissions[permission]:
                self.permissions[permission].append(user_id)
                self._log_audit("grant_permission", {"user_id": user_id, "permission": permission})
                return {"success": True, "message": f"Granted {permission} to {user_id}"}

        return {"success": False, "message": "Invalid permission"}

    def revoke_permission(self, user_id: str, permission: str) -> Dict[str, Any]:
        """Revoke permission from user"""
        if permission in self.permissions and user_id in self.permissions[permission]:
            self.permissions[permission].remove(user_id)
            self._log_audit("revoke_permission", {"user_id": user_id, "permission": permission})
            return {"success": True, "message": f"Revoked {permission} from {user_id}"}

        return {"success": False, "message": "Permission not found"}

    def _determine_level(self, vuln_type: str) -> VulnerabilityLevel:
        """Determine vulnerability level"""
        critical = ["sql_injection", "command_injection"]
        high = ["path_traversal", "hardcoded_secrets", "dangerous_function"]
        medium = ["xss"]

        if vuln_type in critical:
            return VulnerabilityLevel.CRITICAL
        elif vuln_type in high:
            return VulnerabilityLevel.HIGH
        elif vuln_type in medium:
            return VulnerabilityLevel.MEDIUM
        else:
            return VulnerabilityLevel.LOW

    def _get_description(self, vuln_type: str) -> str:
        """Get vulnerability description"""
        descriptions = {
            "sql_injection": "SQL injection vulnerability detected",
            "command_injection": "Command injection vulnerability detected",
            "path_traversal": "Path traversal vulnerability detected",
            "hardcoded_secrets": "Hardcoded credentials detected",
            "xss": "Cross-site scripting vulnerability detected",
            "dangerous_function": "Use of dangerous function",
            "assert_in_production": "Assert statement in production code",
        }
        return descriptions.get(vuln_type, "Security vulnerability detected")

    def _calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]]) -> int:
        """Calculate risk score"""
        score = 0
        weights = {
            VulnerabilityLevel.CRITICAL: 30,
            VulnerabilityLevel.HIGH: 20,
            VulnerabilityLevel.MEDIUM: 10,
            VulnerabilityLevel.LOW: 5,
            VulnerabilityLevel.INFO: 1,
        }

        for vuln in vulnerabilities:
            level = vuln.get("level", VulnerabilityLevel.LOW)
            score += weights.get(level, 5)

        return min(100, score)  # Cap at 100

    def _log_audit(self, action: str, details: Dict[str, Any]):
        """Log audit entry"""
        entry = {"timestamp": datetime.now().isoformat(), "action": action, "details": details}
        self.audit_log.append(entry)

        # Keep only last 1000 entries for size
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        return self.audit_log[-limit:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get security metrics"""
        vuln_by_level = {}
        for vuln in self.vulnerabilities:
            level = vuln["level"].value if isinstance(vuln["level"], Enum) else vuln["level"]
            vuln_by_level[level] = vuln_by_level.get(level, 0) + 1

        return {
            "total_scans": len([e for e in self.audit_log if e["action"] == "scan"]),
            "total_vulnerabilities": len(self.vulnerabilities),
            "vulnerabilities_by_level": vuln_by_level,
            "patches_applied": len(self.patches),
            "audit_log_size": len(self.audit_log),
        }
