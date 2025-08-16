#!/usr/bin/env python3
"""Validate that no API keys or secrets are being committed."""

import re
import sys


# Patterns that indicate potential secrets
SECRET_PATTERNS = [
    # API Keys
    (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
    (r'sk-ant-api[0-9]{2}-[a-zA-Z0-9\-_]{80,}', 'Anthropic API Key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'[0-9a-zA-Z/+=]{40}', 'AWS Secret Key (potential)'),
    
    # Tokens
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Token'),
    (r'ghs_[a-zA-Z0-9]{36}', 'GitHub Secret'),
    (r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}', 'GitHub PAT'),
    
    # Generic patterns
    (r'["\']?[Aa][Pp][Ii][_-]?[Kk][Ee][Yy]["\']?\s*[:=]\s*["\'][^"\']{20,}["\']', 'API Key'),
    (r'["\']?[Ss][Ee][Cc][Rr][Ee][Tt]["\']?\s*[:=]\s*["\'][^"\']{20,}["\']', 'Secret'),
    (r'["\']?[Tt][Oo][Kk][Ee][Nn]["\']?\s*[:=]\s*["\'][^"\']{20,}["\']', 'Token'),
    (r'["\']?[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]["\']?\s*[:=]\s*["\'][^"\']{8,}["\']', 'Password'),
]

# Files/paths to skip
SKIP_PATTERNS = [
    '.env.example',
    '.env.template',
    'test_',
    '__pycache__',
    '.git/',
]


def check_file(filepath: str) -> list:
    """Check a file for potential secrets.
    
    Args:
        filepath: Path to file to check
        
    Returns:
        List of found secrets
    """
    # Skip certain files
    for skip in SKIP_PATTERNS:
        if skip in filepath:
            return []
    
    found_secrets = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern, description in SECRET_PATTERNS:
                    if re.search(pattern, line):
                        # Check if it's a false positive (example/template)
                        if any(word in line.lower() for word in ['example', 'template', 'dummy', 'xxx', '...']):
                            continue
                        
                        found_secrets.append({
                            'file': filepath,
                            'line': line_num,
                            'type': description,
                            'content': line[:80] + '...' if len(line) > 80 else line
                        })
    except Exception as e:
        print(f"⚠️  Could not read {filepath}: {e}")
    
    return found_secrets


def main():
    """Check all files for secrets."""
    if len(sys.argv) < 2:
        return 0
    
    all_secrets = []
    
    for filepath in sys.argv[1:]:
        secrets = check_file(filepath)
        all_secrets.extend(secrets)
    
    if all_secrets:
        print("🚨 POTENTIAL SECRETS DETECTED!")
        print("=" * 60)
        for secret in all_secrets:
            print(f"File: {secret['file']}:{secret['line']}")
            print(f"Type: {secret['type']}")
            print(f"Line: {secret['content']}")
            print("-" * 40)
        
        print("\n❌ Commit blocked: Remove secrets before committing")
        print("Tips:")
        print("1. Use environment variables for secrets")
        print("2. Add secrets to .env file (not .env.example)")
        print("3. Use AWS Secrets Manager for production")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())