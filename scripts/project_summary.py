#!/usr/bin/env python3
"""T-Developer MVP Project Summary."""

import os
from pathlib import Path
from datetime import datetime

def count_files(directory: str, extension: str) -> int:
    """Count files with specific extension."""
    path = Path(directory)
    if not path.exists():
        return 0
    return len(list(path.rglob(f"*.{extension}")))

def get_directory_size(directory: str) -> str:
    """Get total size of directory."""
    total_size = 0
    path = Path(directory)
    if not path.exists():
        return "0 KB"
    
    for file in path.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size
    
    # Convert to human readable
    for unit in ["B", "KB", "MB", "GB"]:
        if total_size < 1024.0:
            return f"{total_size:.1f} {unit}"
        total_size /= 1024.0
    return f"{total_size:.1f} TB"

def main():
    """Print project summary."""
    project_root = Path("/home/ec2-user/T-DeveloperMVP")
    
    print("=" * 60)
    print("🚀 T-Developer v2 MVP - Project Summary")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Phase Completion Status
    print("📋 Phase Completion Status:")
    print("-" * 40)
    phases = [
        ("Phase 1: Multi-Agent Architecture", "✅ Completed"),
        ("Phase 2: Core Infrastructure", "✅ Completed"),
        ("Phase 3: Evolution System", "✅ Completed"),
        ("Phase 4: Testing & Validation", "✅ Completed"),
        ("Phase 5: Documentation & Deployment", "✅ Completed")
    ]
    for phase, status in phases:
        print(f"  {status} {phase}")
    print()
    
    # Project Statistics
    print("📊 Project Statistics:")
    print("-" * 40)
    
    # Count Python files
    py_backend = count_files(project_root / "backend", "py")
    py_tests = count_files(project_root / "backend/tests", "py")
    py_lambda = count_files(project_root / "lambda_handlers", "py")
    py_scripts = count_files(project_root / "scripts", "py")
    
    print(f"  Python Files:")
    print(f"    • Backend: {py_backend} files")
    print(f"    • Tests: {py_tests} files")
    print(f"    • Lambda: {py_lambda} files")
    print(f"    • Scripts: {py_scripts} files")
    print(f"    • Total: {py_backend + py_tests + py_lambda + py_scripts} files")
    print()
    
    # Count TypeScript/JavaScript files
    ts_files = count_files(project_root / "frontend/src", "tsx") + count_files(project_root / "frontend/src", "ts")
    
    print(f"  TypeScript/React Files: {ts_files} files")
    print()
    
    # Count other files
    yaml_files = count_files(project_root, "yaml") + count_files(project_root, "yml")
    json_files = count_files(project_root, "json")
    md_files = count_files(project_root, "md")
    
    print(f"  Configuration Files:")
    print(f"    • YAML: {yaml_files} files")
    print(f"    • JSON: {json_files} files")
    print(f"    • Markdown: {md_files} files")
    print()
    
    # Directory sizes
    print("💾 Directory Sizes:")
    print("-" * 40)
    directories = [
        ("Backend", "backend"),
        ("Frontend", "frontend"),
        ("Tests", "backend/tests"),
        ("Lambda", "lambda_handlers"),
        ("Scripts", "scripts"),
        ("Infrastructure", "infrastructure"),
        ("Documentation", "docs")
    ]
    
    for name, path in directories:
        size = get_directory_size(project_root / path)
        print(f"  • {name}: {size}")
    print()
    
    # Key Components
    print("🔧 Key Components:")
    print("-" * 40)
    components = [
        "✅ Multi-Agent System (Research, Planner, Refactor, Evaluator)",
        "✅ SharedContextStore for state management",
        "✅ Evolution Engine with safety mechanisms",
        "✅ Quality Gates (Security, Test, Performance)",
        "✅ AWS Lambda handlers",
        "✅ DynamoDB tables configuration",
        "✅ API Gateway setup",
        "✅ React/TypeScript frontend",
        "✅ Comprehensive test suite",
        "✅ CI/CD pipeline (GitHub Actions)",
        "✅ Monitoring dashboard (Grafana)",
        "✅ Deployment scripts"
    ]
    
    for component in components:
        print(f"  {component}")
    print()
    
    # Available Scripts
    print("🛠️ Available Commands:")
    print("-" * 40)
    commands = [
        ("Run Tests", "python scripts/run_tests.py all"),
        ("Start Backend", "uvicorn backend.main:app --reload"),
        ("Start Frontend", "cd frontend && npm run dev"),
        ("Deploy to Dev", "./scripts/deploy.sh dev all"),
        ("Run Evolution", "python scripts/evolution/run_perfect_evolution.py")
    ]
    
    for name, cmd in commands:
        print(f"  • {name}:")
        print(f"    $ {cmd}")
    print()
    
    # Next Steps
    print("🎯 Next Steps:")
    print("-" * 40)
    print("  1. Configure environment variables (.env)")
    print("  2. Set up AWS credentials")
    print("  3. Install dependencies (pip install -r requirements.txt)")
    print("  4. Run tests to verify setup")
    print("  5. Deploy to AWS or run locally")
    print()
    
    print("=" * 60)
    print("✨ MVP Development Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()