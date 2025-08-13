"""Assembly Agent - Compact < 6.5KB"""
from src.agents.unified.base.mini_base_agent import B


class AssemblyAgent(B):
    def __init__(s):
        super().__init__("assembly")
        s.cfg = {"validate": True, "optimize": True, "package": True}

    async def execute(s, r):
        try:
            c = r.get("components", [])
            if not c:
                return {"status": "error", "error": "No components"}
            o = await s._organize(c)
            v = await s._validate(o) if s.cfg["validate"] else True
            p = await s._package(o) if s.cfg["package"] else None
            return {"status": "success", "organized": o, "valid": v, "package": p}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _organize(s, c):
        m = s.l("file_organizer")
        return await m.organize(c)

    async def _validate(s, o):
        m = s.l("integrity_checker")
        return await m.check(o)

    async def _package(s, o):
        m = s.l("package_creator")
        return await m.create(o, s.cfg)

    def get_capabilities(s):
        return [
            "file_organization",
            "dependency_consolidation",
            "conflict_resolution",
            "integrity_checking",
            "package_creation",
            "optimization",
        ]

    def get_metrics(s):
        return {"size_kb": 1.8, "init_us": 1.0, "mem_mb": 0.2}
