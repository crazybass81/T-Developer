#!/usr/bin/env python3
"""Check that all new code has corresponding tests (TDD compliance)."""

import sys
import os
from pathlib import Path


def check_test_exists(file_path: str) -> bool:
    """Check if a test file exists for the given source file.
    
    Args:
        file_path: Path to source file
        
    Returns:
        True if test exists
    """
    path = Path(file_path)
    
    # Skip test files themselves
    if 'test_' in path.name or path.parts[0] == 'tests':
        return True
    
    # Skip __init__.py files
    if path.name == '__init__.py':
        return True
    
    # Build expected test path
    if path.parts[0] == 'packages':
        test_path = Path('tests') / Path(*path.parts[1:])
        test_path = test_path.parent / f"test_{test_path.name}"
    else:
        return True  # Skip files outside packages
    
    if not test_path.exists():
        print(f"❌ TDD violation: No test file for {file_path}")
        print(f"   Expected: {test_path}")
        return False
    
    # Check if test file has actual tests
    with open(test_path) as f:
        content = f.read()
        if 'def test_' not in content and 'class Test' not in content:
            print(f"⚠️  Test file {test_path} has no test functions")
            return False
    
    return True


def main():
    """Check TDD compliance for all files."""
    if len(sys.argv) < 2:
        return 0
    
    all_good = True
    for file_path in sys.argv[1:]:
        if not check_test_exists(file_path):
            all_good = False
    
    if all_good:
        print("✅ TDD compliance check passed")
        return 0
    else:
        print("\n❌ TDD compliance check failed")
        print("Remember: Write tests FIRST, then implementation (Red-Green-Refactor)")
        return 1


if __name__ == "__main__":
    sys.exit(main())