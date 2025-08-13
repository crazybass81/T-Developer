import importlib


class B:
    def __init__(s, n):
        s.n = n
        s.m = {}

    def l(s, n):
        if n not in s.m:
            s.m[n] = importlib.import_module(f"src.agents.unified.{s.n}.modules.{n}")
        return s.m[n]

    async def e(s, d):
        t = d.get("t", "default")
        m = s.l(t)
        return await m.p(d) if hasattr(m, "p") else m.process(d)
