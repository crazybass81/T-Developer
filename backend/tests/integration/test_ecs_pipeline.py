#!/usr/bin/env python3
"""
Test script for ECS Pipeline imports
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing ECS Pipeline imports...")

try:
    # Test the import that's failing
    from orchestration.ecs_pipeline import pipeline as ecs_pipeline
    print("✓ ECS Pipeline imported successfully")
    
    # Check if pipeline is initialized
    print(f"  - Pipeline initialized: {ecs_pipeline.initialized}")
    print(f"  - Pipeline agents: {list(ecs_pipeline.agents.keys()) if ecs_pipeline.agents else 'Not loaded'}")
    
except ImportError as e:
    print(f"✗ Failed to import ECS Pipeline: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting individual agent imports...")

try:
    from agents.ecs_integrated.nl_input.main import NLInputAgent
    print("✓ NL Input Agent imported")
except ImportError as e:
    print(f"✗ NL Input Agent import failed: {e}")

try:
    from agents.ecs_integrated.base_agent import AgentContext
    print("✓ AgentContext imported")
except ImportError as e:
    print(f"✗ AgentContext import failed: {e}")

print("\nTesting framework imports...")

try:
    from agents.framework.core.base_agent import BaseAgent
    print("✓ BaseAgent imported from framework")
except ImportError as e:
    print(f"✗ BaseAgent import failed: {e}")

print("\nDone!")