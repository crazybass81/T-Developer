"""
Agent Loader - Fixed import strategy for unified agents
"""

import sys
from pathlib import Path

# Add backend to Python path
backend_path = str(Path(__file__).parent.parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


def get_agent_classes():
    """Load all agent classes with proper imports"""

    agents = {}

    # Import each agent directly
    try:
        from src.agents.unified.nl_input.agent import UnifiedNLInputAgent

        agents["nl_input"] = UnifiedNLInputAgent
    except ImportError as e:
        print(f"Failed to import nl_input: {e}")

    try:
        from src.agents.unified.ui_selection.agent import UnifiedUISelectionAgent

        agents["ui_selection"] = UnifiedUISelectionAgent
    except ImportError as e:
        print(f"Failed to import ui_selection: {e}")

    try:
        from src.agents.unified.parser.agent import UnifiedParserAgent

        agents["parser"] = UnifiedParserAgent
    except ImportError as e:
        print(f"Failed to import parser: {e}")

    try:
        from src.agents.unified.component_decision.agent import ComponentDecisionAgent

        agents["component_decision"] = ComponentDecisionAgent
    except ImportError as e:
        print(f"Failed to import component_decision: {e}")

    try:
        from src.agents.unified.match_rate.agent import MatchRateAgent

        agents["match_rate"] = MatchRateAgent
    except ImportError as e:
        print(f"Failed to import match_rate: {e}")

    try:
        from src.agents.unified.search.agent import SearchAgent

        agents["search"] = SearchAgent
    except ImportError as e:
        print(f"Failed to import search: {e}")

    try:
        from src.agents.unified.generation.agent import GenerationAgent

        agents["generation"] = GenerationAgent
    except ImportError as e:
        print(f"Failed to import generation: {e}")

    try:
        from src.agents.unified.assembly.agent import AssemblyAgent

        agents["assembly"] = AssemblyAgent
    except ImportError as e:
        print(f"Failed to import assembly: {e}")

    try:
        from src.agents.unified.download.agent import DownloadAgent

        agents["download"] = DownloadAgent
    except ImportError as e:
        print(f"Failed to import download: {e}")

    return agents


# Load all agents on module import
AGENT_CLASSES = get_agent_classes()
print(f"✅ Loaded {len(AGENT_CLASSES)} agent classes: {list(AGENT_CLASSES.keys())}")
