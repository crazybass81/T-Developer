"""Component Decision Agent - Compact < 6.5KB"""
from src.agents.unified.base.mini_base_agent import B


class ComponentDecisionAgent(B):
    def __init__(s):
        super().__init__("component_decision")
        s.cfg = {"analyze": True, "optimize": True, "max_cost": 1000}

    async def execute(s, r):
        try:
            req = r.get("requirements", {})
            if not req:
                return {"status": "error", "error": "No requirements"}
            arch = await s._select_arch(req)
            comp = await s._analyze_comp(req, arch)
            stack = await s._build_stack(comp)
            return {
                "status": "success",
                "architecture": arch,
                "components": comp,
                "stack": stack,
                "cost": s._est_cost(comp),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _select_arch(s, r):
        m = s.l("architecture_selector")
        return await m.select(r, s.cfg)

    async def _analyze_comp(s, r, a):
        m = s.l("component_analyzer")
        return await m.analyze(r, a)

    async def _build_stack(s, c):
        m = s.l("technology_stack_builder")
        return await m.build(c, s.cfg["optimize"])

    def _est_cost(s, c):
        base = len(c) * 10
        return min(s.cfg["max_cost"], base * 1.2)

    def get_capabilities(s):
        return [
            "architecture_selection",
            "component_analysis",
            "stack_building",
            "cost_optimization",
            "db_design",
            "api_architecture",
            "security_planning",
        ]

    def get_metrics(s):
        return {"size_kb": 2.3, "init_us": 1.3, "mem_mb": 0.25}
