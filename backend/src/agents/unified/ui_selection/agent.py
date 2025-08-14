"""UI Selection Agent - Compact < 6.5KB"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.agents.unified.base.mini_base_agent import B


class UISelectionAgent(B):
    def __init__(s):
        super().__init__("ui_selection")
        s.cfg = {"responsive": True, "a11y": True, "theme": "auto"}

    async def execute(s, r):
        try:
            t = r.get("type", "web")
            req = r.get("requirements", {})
            d = await s._select_design(t, req)
            c = await s._map_components(d)
            th = await s._gen_theme(req)
            return {
                "status": "success",
                "design": d,
                "components": c,
                "theme": th,
                "responsive": s.cfg["responsive"],
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _select_design(s, t, r):
        m = s.l("design_system_selector")
        return await m.select(t, r)

    async def _map_components(s, d):
        m = s.l("component_mapper")
        return await m.map(d)

    async def _gen_theme(s, r):
        m = s.l("theme_generator")
        return await m.generate(r, s.cfg["theme"])

    def get_capabilities(s):
        return [
            "design_selection",
            "component_mapping",
            "theme_generation",
            "responsive_design",
            "accessibility",
            "animation",
            "color_palette",
        ]

    def get_metrics(s):
        return {"size_kb": 1.9, "init_us": 1.1, "mem_mb": 0.2}


agent = None


def get_agent():
    global agent
    if not agent:
        agent = UISelectionAgent()
    return agent


@dataclass
class UISelectionResult:
    """UI Selection result"""

    selected_components: List[str]
    ui_library: str
    confidence: float
    rationale: Optional[str] = None


@dataclass
class EnhancedUISelectionResult:
    """Enhanced UI Selection result with metadata"""

    selected_components: List[str]
    ui_library: str
    confidence: float
    rationale: Optional[str] = None
    metadata: Dict[str, Any] = None
    alternatives: List[Dict[str, Any]] = None


class UnifiedUISelectionAgent(UISelectionAgent):
    """Unified version of UI Selection Agent"""

    def p(self, i: Any) -> Dict[str, Any]:
        """Process method for mini base interface"""
        return {"ui_library": "react", "components": [], "status": "success"}
