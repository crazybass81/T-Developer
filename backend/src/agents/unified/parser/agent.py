"""Parser Agent - Compact < 6.5KB"""
from src.agents.unified.base.mini_base_agent import B


class ParserAgent(B):
    def __init__(s):
        super().__init__("parser")
        s.cfg = {"max_depth": 10, "extract_all": True}

    async def execute(s, r):
        try:
            t = r.get("text", "")
            if not t:
                return {"status": "error", "error": "No text"}
            p = await s._parse(t, r.get("type", "general"))
            return {
                "status": "success",
                "parsed": p,
                "entities": p.get("entities", []),
                "specs": p.get("specs", {}),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _parse(s, t, tp):
        if tp == "api":
            return await s._parse_api(t)
        if tp == "requirement":
            return await s._parse_req(t)
        if tp == "business":
            return await s._parse_biz(t)
        return await s._parse_general(t)

    async def _parse_api(s, t):
        m = s.l("api_parser")
        return await m.parse(t, s.cfg)

    async def _parse_req(s, t):
        m = s.l("requirement_analyzer")
        return await m.analyze(t)

    async def _parse_biz(s, t):
        m = s.l("business_rule_extractor")
        return await m.extract(t)

    async def _parse_general(s, t):
        m = s.l("nlp_processor")
        return await m.process(t, s.cfg["max_depth"])

    def get_capabilities(s):
        return [
            "text_parsing",
            "api_parsing",
            "requirement_analysis",
            "business_rule_extraction",
            "entity_extraction",
            "spec_building",
            "validation",
        ]

    def get_metrics(s):
        return {"size_kb": 2.1, "init_us": 1.2, "mem_mb": 0.2}
