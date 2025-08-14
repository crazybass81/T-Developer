"""Base Agent Interface for T-Developer Evolution System"""
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List


class BaseEvolutionAgent(ABC):
    """Base class for all evolution agents - reusable across projects"""

    def __init__(self, name: str, version: str = "1.0.0") -> Any:
        """Function __init__(self, name, version)"""
        self.name = name
        self.version = version
        self.created_at = datetime.now()
        self.execution_history = []
        self.metadata = {}

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method - must be implemented by each agent"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass

    def log_execution(self, input_data: Dict, output_data: Dict) -> Any:
        """Log execution history for analysis"""
        self.execution_history.append(
            {"timestamp": datetime.now().isoformat(), "input": input_data, "output": output_data}
        )

    def export_as_module(self) -> Dict:
        """Export agent as reusable module"""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.get_capabilities(),
            "interface": {"input": "Dict[str, Any]", "output": "Dict[str, Any]", "async": True},
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Serialize agent configuration"""
        return json.dumps(
            {
                "name": self.name,
                "version": self.version,
                "created_at": self.created_at.isoformat(),
                "capabilities": self.get_capabilities(),
                "metadata": self.metadata,
            }
        )
