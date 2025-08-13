"""
Common input handler for all agents
Handles various input formats from pipeline
"""

from typing import Any, Dict, Tuple
from dataclasses import dataclass


@dataclass
class AgentContext:
    """Simple context object"""

    pipeline_id: str = ""
    project_id: str = ""
    timestamp: str = ""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


def unwrap_input(input_data: Any) -> Tuple[Dict, Any]:
    """
    Unwrap input data from various formats

    Returns:
        Tuple of (data_dict, context)
    """

    # Handle AgentInput object
    if hasattr(input_data, "data"):
        data = input_data.data
        context = (
            input_data.context if hasattr(input_data, "context") else AgentContext()
        )
        return data, context

    # Handle wrapped dict from pipeline
    if (
        isinstance(input_data, dict)
        and "data" in input_data
        and "context" in input_data
    ):
        data = input_data["data"]
        context_data = input_data["context"]

        # Convert context dict to object if needed
        if isinstance(context_data, dict):
            context = AgentContext(**context_data)
        else:
            context = context_data

        return data, context

    # Handle direct dict or other data
    if isinstance(input_data, dict):
        return input_data, AgentContext()

    # Handle string input
    if isinstance(input_data, str):
        return {"query": input_data}, AgentContext()

    # Default case
    return {"data": input_data}, AgentContext()
