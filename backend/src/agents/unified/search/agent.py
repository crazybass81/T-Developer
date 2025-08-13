"""Search Agent - Compact < 6.5KB"""
from src.agents.unified.base.mini_base_agent import B


class SearchAgent(B):
    def __init__(s):
        super().__init__("search")
        s.cfg = {"limit": 100, "cache": True, "rank": True}

    async def execute(s, r):
        try:
            q = r.get("query", "")
            if not q:
                return {"status": "error", "error": "No query"}
            res = await s._search(q, r.get("filters", {}))
            if s.cfg["rank"]:
                res = await s._rank(res, q)
            return {
                "status": "success",
                "results": res[: s.cfg["limit"]],
                "total": len(res),
                "query": q,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _search(s, q, f):
        m = s.l("search_engine")
        return await m.search(q, f, s.cfg["cache"])

    async def _rank(s, r, q):
        m = s.l("result_ranker")
        return await m.rank(r, q)

    def get_capabilities(s):
        return [
            "text_search",
            "semantic_search",
            "faceted_search",
            "filtering",
            "ranking",
            "caching",
            "autocomplete",
        ]

    def get_metrics(s):
        return {"size_kb": 1.5, "init_us": 0.8, "mem_mb": 0.15}
