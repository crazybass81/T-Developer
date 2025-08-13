"""Match Rate Agent - Compact < 6.5KB"""
from src.agents.unified.base.mini_base_agent import B


class MatchRateAgent(B):
    def __init__(s):
        super().__init__("match_rate")
        s.cfg = {"threshold": 0.7, "analyze_all": True}

    async def execute(s, r):
        try:
            i = r.get("items", [])
            q = r.get("query", {})
            if not i:
                return {"status": "error", "error": "No items"}
            m = await s._calc_matches(i, q)
            s = await s._score_items(m)
            rec = await s._recommend(s)
            return {"status": "success", "matches": m, "scores": s, "recommendations": rec}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _calc_matches(s, i, q):
        m = s.l("similarity_calculator")
        return await m.calculate(i, q, s.cfg["threshold"])

    async def _score_items(s, m):
        m = s.l("quality_assessor")
        return await m.assess(m)

    async def _recommend(s, sc):
        m = s.l("recommendation_engine")
        return await m.recommend(sc, s.cfg)

    def get_capabilities(s):
        return [
            "similarity_calculation",
            "quality_assessment",
            "recommendation",
            "semantic_matching",
            "risk_analysis",
            "cost_efficiency",
        ]

    def get_metrics(s):
        return {"size_kb": 1.7, "init_us": 0.9, "mem_mb": 0.15}
