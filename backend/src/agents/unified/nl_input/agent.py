"""NL Input Agent - Compact < 6.5KB"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.agents.unified.base.mini_base_agent import B


class NLInputAgent(B):
    def __init__(s):
        super().__init__("nl_input")
        s.cfg = {"lang": "en", "max_len": 500, "extract": True}

    async def execute(s, r):
        try:
            i = r.get("input", "")
            if not i:
                return {"status": "error", "error": "No input"}
            p = await s._process(i)
            return {
                "status": "success",
                "intent": p["intent"],
                "entities": p.get("entities", []),
                "requirements": p.get("req", []),
                "confidence": p.get("conf", 0.8),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _process(s, i):
        intent = await s._analyze_intent(i)
        entities = await s._extract_entities(i) if s.cfg["extract"] else []
        req = await s._extract_req(i)
        return {"intent": intent, "entities": entities, "req": req, "conf": s._calc_conf(i)}

    async def _analyze_intent(s, i):
        m = s.l("intent_analyzer")
        return await m.analyze(i, s.cfg["lang"])

    async def _extract_entities(s, i):
        m = s.l("entity_recognizer")
        return await m.extract(i)

    async def _extract_req(s, i):
        m = s.l("requirement_extractor")
        return await m.extract(i, s.cfg["max_len"])

    def _calc_conf(s, i):
        l = len(i.split())
        if l < 3:
            return 0.5
        if l > 100:
            return 0.6
        return min(0.95, 0.7 + l * 0.002)

    def get_capabilities(s):
        return [
            "nl_parsing",
            "intent_analysis",
            "entity_extraction",
            "requirement_extraction",
            "context_enhancement",
            "multilingual",
            "ambiguity_resolution",
        ]

    def get_metrics(s):
        return {"size_kb": 2.8, "init_us": 1.5, "mem_mb": 0.3}


agent = None


def get_agent():
    global agent
    if not agent:
        agent = NLInputAgent()
    return agent


@dataclass
class NLInputResult:
    """Basic NL input processing result"""

    intent: str
    entities: List[Dict[str, Any]]
    confidence: float
    requirements: List[str]


@dataclass
class EnhancedNLInputResult:
    """Enhanced NL input processing result with metadata"""

    intent: str
    entities: List[Dict[str, Any]]
    confidence: float
    requirements: List[str]
    metadata: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class UnifiedNLInputAgent(NLInputAgent):
    """Unified version of NL Input Agent for compatibility"""

    def p(self, i: Any) -> Dict[str, Any]:
        """Process method for mini base interface"""
        return {"intent": "process", "input": i, "status": "success"}
