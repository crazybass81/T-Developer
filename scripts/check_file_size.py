#!/usr/bin/env python3
"""Check that agent files are under 6.5KB limit."""

import os
import sys
from pathlib import Path


MAX_SIZE_BYTES = 6656  # 6.5 KB = 6.5 * 1024


def check_file_size(filepath: str) -> bool:
    """Check if file is within size limit.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if within limit
    """
    path = Path(filepath)
    
    if not path.exists():
        return True  # New file, will check after creation
    
    size = path.stat().st_size
    size_kb = size / 1024
    
    if size > MAX_SIZE_BYTES:
        print(f"❌ File too large: {filepath}")
        print(f"   Size: {size_kb:.2f} KB (limit: 6.5 KB)")
        print(f"   Excess: {(size - MAX_SIZE_BYTES) / 1024:.2f} KB")
        
        # Provide suggestions
        print("\n   Suggestions to reduce size:")
        print("   • Extract helper functions to shared modules")
        print("   • Remove unnecessary comments")
        print("   • Use more concise variable names")
        print("   • Move constants to config files")
        print("   • Split into multiple smaller agents")
        
        return False
    
    # Warning if getting close to limit
    if size > MAX_SIZE_BYTES * 0.9:
        print(f"⚠️  File approaching size limit: {filepath}")
        print(f"   Size: {size_kb:.2f} KB (limit: 6.5 KB)")
        print(f"   Remaining: {(MAX_SIZE_BYTES - size) / 1024:.2f} KB")
    
    return True


def main():
    """Check all agent files for size compliance."""
    if len(sys.argv) < 2:
        return 0
    
    all_good = True
    
    for filepath in sys.argv[1:]:
        # Only check agent files
        if 'packages/agents/' in filepath and filepath.endswith('.py'):
            if not check_file_size(filepath):
                all_good = False
    
    if all_good:
        print("✅ All agent files within size limit")
        return 0
    else:
        print("\n❌ Some agent files exceed size limit")
        print("Agent files must be under 6.5KB for optimal performance")
        return 1


if __name__ == "__main__":
    sys.exit(main())