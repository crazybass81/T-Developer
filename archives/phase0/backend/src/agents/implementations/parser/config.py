"""
T-Developer MVP - Parser Agent Configuration

Configuration settings for Parser Agent

Author: T-Developer Team
Created: 2024
"""

from typing import Dict, Any

PARSER_CONFIG = {
    "model": {
        "primary": "anthropic.claude-3-sonnet-v2:0",
        "fallback": "gpt-4-turbo-preview",
        "temperature": 0.2,
        "max_tokens": 4000
    },
    "parsing": {
        "max_requirements": 100,
        "min_confidence": 0.7,
        "enable_validation": True,
        "enable_nlp_preprocessing": True
    },
    "performance": {
        "timeout_seconds": 30,
        "max_retries": 3,
        "parallel_processing": True,
        "cache_enabled": True
    },
    "output": {
        "include_metadata": True,
        "include_confidence_scores": True,
        "structured_format": "json"
    }
}

def get_parser_config() -> Dict[str, Any]:
    """Get parser configuration"""
    return PARSER_CONFIG

def update_parser_config(updates: Dict[str, Any]) -> None:
    """Update parser configuration"""
    PARSER_CONFIG.update(updates)