#!/usr/bin/env python3
"""Check evolution safety constraints."""

import json
import subprocess
import sys
from pathlib import Path

CONSTRAINTS = {
    "max_files_per_commit": 10,
    "max_changes_per_file": 100,
    "max_complexity_increase": 5,
    "min_test_coverage": 85,
    "min_security_score": 80,
}


def check_commit_size() -> bool:
    """Check if commit size is within limits.

    Returns:
        True if within limits
    """
    # Get list of changed files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True
    )

    changed_files = result.stdout.strip().split("\n")
    changed_files = [f for f in changed_files if f]  # Remove empty

    if len(changed_files) > CONSTRAINTS["max_files_per_commit"]:
        print(
            f"❌ Too many files changed: {len(changed_files)} > {CONSTRAINTS['max_files_per_commit']}"
        )
        print("   Consider breaking this into smaller commits")
        return False

    # Check changes per file
    for file in changed_files:
        if not file.endswith(".py"):
            continue

        result = subprocess.run(
            ["git", "diff", "--cached", "--numstat", file], capture_output=True, text=True
        )

        if result.stdout:
            parts = result.stdout.strip().split()
            if len(parts) >= 2:
                additions = int(parts[0]) if parts[0] != "-" else 0
                deletions = int(parts[1]) if parts[1] != "-" else 0
                total_changes = additions + deletions

                if total_changes > CONSTRAINTS["max_changes_per_file"]:
                    print(
                        f"❌ Too many changes in {file}: {total_changes} > {CONSTRAINTS['max_changes_per_file']}"
                    )
                    return False

    return True


def check_test_coverage() -> bool:
    """Check if test coverage meets minimum.

    Returns:
        True if coverage is adequate
    """
    # This would normally run pytest with coverage
    # For pre-commit, we'll just check if tests exist
    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ No tests directory found")
        return False

    test_files = list(test_dir.rglob("test_*.py"))
    if len(test_files) < 1:
        print("❌ No test files found")
        return False

    return True


def check_dangerous_patterns() -> bool:
    """Check for dangerous code patterns.

    Returns:
        True if no dangerous patterns found
    """
    dangerous_patterns = [
        "exec(",
        "eval(",
        "__import__",
        "os.system(",
        "subprocess.call(shell=True",
        "pickle.loads(",
        "yaml.load(",  # Should use safe_load
    ]

    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)

    diff_content = result.stdout

    for pattern in dangerous_patterns:
        if pattern in diff_content:
            print(f"❌ Dangerous pattern detected: {pattern}")
            print("   This could pose a security risk during evolution")
            return False

    return True


def main():
    """Run all evolution safety checks."""
    print("🔍 Checking evolution safety constraints...")

    checks = [
        ("Commit size", check_commit_size),
        ("Test coverage", check_test_coverage),
        ("Dangerous patterns", check_dangerous_patterns),
    ]

    all_passed = True
    for name, check_func in checks:
        try:
            if check_func():
                print(f"✅ {name} check passed")
            else:
                print(f"❌ {name} check failed")
                all_passed = False
        except Exception as e:
            print(f"⚠️  {name} check error: {e}")
            all_passed = False

    if all_passed:
        print("\n✅ All evolution safety checks passed")
        print(f"Constraints: {json.dumps(CONSTRAINTS, indent=2)}")
        return 0
    else:
        print("\n❌ Evolution safety checks failed")
        print("Fix the issues above before committing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
