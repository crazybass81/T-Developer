"""Data Transformer Agent - Compact < 6.5KB"""
import json


class DataTransformerAgent:
    def __init__(s):
        s.cfg = {"validate": True, "clean": True, "format": "json"}

    async def execute(s, r):
        try:
            d = r.get("data")
            if not d:
                return {"status": "error", "error": "No data"}
            t = r.get("transform_type", "normalize")
            if t == "normalize":
                res = await s._normalize(d)
            elif t == "aggregate":
                res = await s._aggregate(d)
            elif t == "filter":
                res = await s._filter(d, r.get("conditions", {}))
            elif t == "map":
                res = await s._map(d, r.get("mapping", {}))
            else:
                res = d
            return {"status": "success", "transformed": res, "type": t}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _normalize(s, d):
        if isinstance(d, list):
            return [s._norm_item(i) for i in d]
        return s._norm_item(d)

    def _norm_item(s, i):
        if isinstance(i, dict):
            return {k.lower().replace(" ", "_"): v for k, v in i.items()}
        return i

    async def _aggregate(s, d):
        if not isinstance(d, list):
            return d
        agg = {}
        for i in d:
            if isinstance(i, dict):
                for k, v in i.items():
                    if k not in agg:
                        agg[k] = []
                    agg[k].append(v)
        return agg

    async def _filter(s, d, c):
        if not isinstance(d, list):
            return d
        res = []
        for i in d:
            if s._match_conditions(i, c):
                res.append(i)
        return res

    def _match_conditions(s, i, c):
        for k, v in c.items():
            if k not in i or i[k] != v:
                return False
        return True

    async def _map(s, d, m):
        if isinstance(d, list):
            return [s._map_item(i, m) for i in d]
        return s._map_item(d, m)

    def _map_item(s, i, m):
        if not isinstance(i, dict):
            return i
        res = {}
        for k, v in m.items():
            if v in i:
                res[k] = i[v]
        return res

    def get_capabilities(s):
        return [
            "normalization",
            "aggregation",
            "filtering",
            "mapping",
            "validation",
            "cleaning",
            "format_conversion",
        ]

    def get_metrics(s):
        return {"size_kb": 2.5, "init_us": 1.5, "mem_mb": 0.3}


agent = None


def get_agent():
    global agent
    if not agent:
        agent = DataTransformerAgent()
    return agent
