#!/usr/bin/env python3
"""PR-Only Policy Enforcement and Dangerous Command Blocking.

This script enforces security policies:
1. All changes must go through PR (no direct commits to main/develop)
2. Block dangerous commands from being executed
3. Validate that sensitive files are not modified
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Dangerous commands that should be blocked
DANGEROUS_COMMANDS = {
    "rm -rf /",
    "dd if=/dev/zero",
    "chmod -R 777",
    "curl | bash",
    "wget | sh",
    "> /dev/sda",
    "fork bomb",
    ":(){ :|:& };:",
}

# Sensitive file patterns that require extra review
SENSITIVE_FILES = {
    r".*\.env$",
    r".*\.pem$",
    r".*\.key$",
    r".*\.p12$",
    r".*secrets.*",
    r".*credentials.*",
    r".*password.*",
    r".*/aws/.*",
    r".*/\.github/workflows/.*",
}

# Protected branches
PROTECTED_BRANCHES = {"main", "master", "develop", "production"}


class PRPolicyEnforcer:
    """Enforces PR-only policy and security rules."""
    
    def __init__(self):
        """Initialize policy enforcer."""
        self.violations = []
        self.warnings = []
    
    def check_branch_protection(self) -> bool:
        """Check if current branch allows direct commits."""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = result.stdout.strip()
            
            if current_branch in PROTECTED_BRANCHES:
                self.violations.append(
                    f"❌ Direct commits to '{current_branch}' are not allowed. "
                    "Please create a feature branch and submit a PR."
                )
                return False
                
        except subprocess.CalledProcessError as e:
            self.warnings.append(f"⚠️ Could not determine current branch: {e}")
            
        return True
    
    def check_dangerous_commands(self, files: List[Path]) -> bool:
        """Check for dangerous commands in scripts."""
        found_dangerous = False
        
        for file_path in files:
            if file_path.suffix in [".sh", ".bash", ".py", ".yml", ".yaml"]:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    for line_num, line in enumerate(content.split('\n'), 1):
                        for dangerous_cmd in DANGEROUS_COMMANDS:
                            if dangerous_cmd in line:
                                self.violations.append(
                                    f"❌ Dangerous command found in {file_path}:{line_num}\n"
                                    f"   Command: '{dangerous_cmd}'"
                                )
                                found_dangerous = True
                                
                except Exception as e:
                    self.warnings.append(f"⚠️ Could not scan {file_path}: {e}")
                    
        return not found_dangerous
    
    def check_sensitive_files(self, files: List[Path]) -> bool:
        """Check if sensitive files are being modified."""
        sensitive_modified = []
        
        for file_path in files:
            for pattern in SENSITIVE_FILES:
                if re.match(pattern, str(file_path)):
                    sensitive_modified.append(str(file_path))
                    break
                    
        if sensitive_modified:
            self.warnings.append(
                "⚠️ Sensitive files modified (require extra review):\n" +
                "\n".join(f"   - {f}" for f in sensitive_modified)
            )
            
        return True  # Warning only, don't block
    
    def check_commit_signatures(self) -> bool:
        """Check if commits are signed."""
        try:
            result = subprocess.run(
                ["git", "log", "--format=%G?", "-1"],
                capture_output=True,
                text=True,
                check=True
            )
            
            signature_status = result.stdout.strip()
            if signature_status not in ["G", "U"]:  # G=good, U=good but unknown
                self.warnings.append(
                    "⚠️ Latest commit is not signed. "
                    "Consider signing commits with GPG."
                )
                
        except subprocess.CalledProcessError:
            pass
            
        return True
    
    def check_file_permissions(self, files: List[Path]) -> bool:
        """Check for overly permissive file permissions."""
        for file_path in files:
            if file_path.exists():
                # Check if file is world-writable
                stat_info = file_path.stat()
                if stat_info.st_mode & 0o002:
                    self.warnings.append(
                        f"⚠️ File has world-write permissions: {file_path}"
                    )
                    
        return True
    
    def get_changed_files(self) -> List[Path]:
        """Get list of changed files in current commit."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    files.append(Path(line))
                    
            return files
            
        except subprocess.CalledProcessError:
            # If can't get diff, try staged files
            try:
                result = subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                files = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        files.append(Path(line))
                        
                return files
                
            except subprocess.CalledProcessError:
                return []
    
    def enforce_policies(self) -> Tuple[bool, str]:
        """Enforce all policies and return status."""
        print("🔒 Enforcing PR-Only Policy and Security Checks...\n")
        
        # Get changed files
        changed_files = self.get_changed_files()
        print(f"📝 Checking {len(changed_files)} changed files...\n")
        
        # Run all checks
        checks = [
            ("Branch Protection", self.check_branch_protection()),
            ("Dangerous Commands", self.check_dangerous_commands(changed_files)),
            ("Sensitive Files", self.check_sensitive_files(changed_files)),
            ("Commit Signatures", self.check_commit_signatures()),
            ("File Permissions", self.check_file_permissions(changed_files)),
        ]
        
        # Print results
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False
                
        print()
        
        # Print violations
        if self.violations:
            print("🚨 VIOLATIONS FOUND:\n")
            for violation in self.violations:
                print(violation)
            print()
            
        # Print warnings
        if self.warnings:
            print("⚠️ WARNINGS:\n")
            for warning in self.warnings:
                print(warning)
            print()
            
        # Generate summary
        if all_passed and not self.violations:
            summary = "✅ All security policies passed!"
        else:
            summary = "❌ Security policy violations detected. Please fix before committing."
            
        return all_passed and not self.violations, summary
    
    def create_pre_commit_hook(self) -> None:
        """Install as pre-commit hook."""
        hook_path = Path(".git/hooks/pre-commit")
        
        hook_content = """#!/bin/bash
# PR-Only Policy Pre-Commit Hook

python scripts/pr_policy.py
if [ $? -ne 0 ]; then
    echo "❌ Commit blocked due to policy violations"
    exit 1
fi
"""
        
        try:
            hook_path.write_text(hook_content)
            hook_path.chmod(0o755)
            print(f"✅ Pre-commit hook installed at {hook_path}")
        except Exception as e:
            print(f"❌ Failed to install pre-commit hook: {e}")


def main():
    """Main entry point."""
    enforcer = PRPolicyEnforcer()
    
    # Check if we should install as hook
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        enforcer.create_pre_commit_hook()
        return 0
        
    # Run policy enforcement
    passed, summary = enforcer.enforce_policies()
    
    print("=" * 60)
    print(summary)
    print("=" * 60)
    
    # Exit with appropriate code
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())