from typing import Any, Dict, List

from .dag_validator import DAGValidator, GraphMetrics
from .parser import WorkflowDefinition


class WorkflowOptimizer:
    def __init__(self):
        self.validator = DAGValidator()
        self.cache = {}
        self.rules = {
            "parallelization": {"weight": 0.8, "threshold": 0.5},
            "complexity_reduction": {"weight": 0.7, "threshold": 0.6},
        }

    def optimize_workflow(self, wf: WorkflowDefinition) -> Dict[str, Any]:
        key = f"{wf.id}_{wf.version}"
        if key in self.cache:
            return self.cache[key]
        result = {
            "original_workflow": wf.id,
            "optimization_score": 50.0,
            "suggested_improvements": [],
            "structure_optimizations": [],
            "performance_optimizations": [],
        }
        try:
            validation = self.validator.validate_dag(wf)
            if not validation["is_valid_dag"]:
                result["suggested_improvements"].append(
                    {"type": "critical", "issue": "Invalid DAG", "solution": "Fix cycles"}
                )
                return result
            metrics = GraphMetrics(**validation["graph_metrics"])
            result["structure_optimizations"] = self._analyze_parallel(wf, metrics)
            result["optimization_score"] = self._calc_score(wf, metrics)
        except Exception as e:
            result["suggested_improvements"].append({"type": "error", "issue": str(e)})
        self.cache[key] = result
        return result

    def _analyze_parallel(self, wf: WorkflowDefinition, metrics: GraphMetrics) -> List[Dict]:
        opts = []
        if metrics.parallelization_factor < self.rules["parallelization"]["threshold"]:
            candidates = self._find_candidates(wf)
            if candidates:
                opts.append(
                    {
                        "type": "parallelization",
                        "title": "Increase Parallel Execution",
                        "candidates": candidates[:3],
                        "priority": "high",
                    }
                )
        return opts

    def _find_candidates(self, wf: WorkflowDefinition) -> List[Dict]:
        candidates = []
        graph = self.validator._build_graph(wf)
        for step in wf.steps[:5]:
            deps = graph.get(step.id, [])
            parallel_with = [
                other.id for other in wf.steps if other.id != step.id and other.id not in deps
            ][:2]
            if parallel_with:
                candidates.append({"step_id": step.id, "can_parallel_with": parallel_with})
        return candidates

    def _calc_score(self, wf: WorkflowDefinition, metrics: GraphMetrics) -> float:
        score = 50.0
        if metrics.parallelization_factor > 0.7:
            score += 20
        if metrics.topological_complexity < 0.3:
            score += 15
        return min(100, max(0, score))

    def generate_optimized(
        self, wf: WorkflowDefinition, opts: List[str] = None
    ) -> WorkflowDefinition:
        opt_steps = [s for s in wf.steps]
        if opts and "retry_policy" in opts:
            for step in opt_steps:
                if not step.retry_policy:
                    step.retry_policy = {"max_attempts": 3, "backoff_factor": 2}
        return WorkflowDefinition(
            id=f"{wf.id}_optimized",
            name=f"{wf.name} (Optimized)",
            version="1.1.0",
            steps=opt_steps,
            dependencies=wf.dependencies,
            metadata={**wf.metadata, "optimized": True},
        )
