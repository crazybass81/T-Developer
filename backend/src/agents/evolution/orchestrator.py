"""Evolution Orchestrator - Connects and coordinates all evolution agents"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.agents.evolution.evaluator_agent import EvaluatorAgent
from src.agents.evolution.planner_agent import PlannerAgent
from src.agents.evolution.refactor_agent import RefactorAgent
from src.agents.evolution.research_agent import ResearchAgent
from src.agents.registry import get_global_registry


class EvolutionOrchestrator:
    """
    진화 오케스트레이터 - 4개 에이전트를 연결하여 진화 사이클 실행

    Evolution Cycle:
    1. Research: 정보 수집 및 분석
    2. Plan: 4시간 단위 작업 계획 수립
    3. Refactor: 실제 코드 개선 실행
    4. Evaluate: 개선 결과 평가
    5. Loop: 목표 달성까지 반복
    """

    def __init__(self, target_path: str = None) -> Any:
        """
        Args:
            target_path: 진화 대상 경로 (기본값: T-DeveloperMVP 자체)
        """
        self.target_path = target_path or "/home/ec2-user/T-DeveloperMVP"
        self.evolution_dir = Path("/tmp/t_developer_evolution")
        self.evolution_dir.mkdir(exist_ok=True)
        self.research_agent = ResearchAgent()
        self.planner_agent = PlannerAgent()
        self.refactor_agent = RefactorAgent()
        self.evaluator_agent = EvaluatorAgent()
        self._register_agents()
        self.evolution_state = {
            "version": "1.0.0",
            "cycles_completed": 0,
            "total_improvements": 0,
            "success_rate": 0.0,
            "current_goal": None,
            "history": [],
        }
        self.max_cycles = 10
        self.target_success_rate = 0.7
        self.min_improvement_threshold = 5

    def _register_agents(self) -> Any:
        """에이전트를 Registry에 등록"""
        registry = get_global_registry()
        registry.register_agent("research_evolution", self.research_agent, "evolution")
        registry.register_agent("planner_evolution", self.planner_agent, "evolution")
        registry.register_agent("refactor_evolution", self.refactor_agent, "evolution")
        registry.register_agent("evaluator_evolution", self.evaluator_agent, "evolution")
        registry.register_composite_agent(
            "evolution_orchestrator",
            [
                "research_evolution",
                "planner_evolution",
                "refactor_evolution",
                "evaluator_evolution",
            ],
        )

    async def evolve(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        진화 사이클 실행

        Args:
            goal: {
                "description": "진화 목표",
                "constraints": ["제약사항"],
                "success_criteria": {"metric": value},
                "max_cycles": 5,
                "use_ai": True/False
            }

        Returns:
            진화 결과 딕셔너리
        """
        print("\n" + "=" * 60)
        print("🧬 T-Developer Self-Evolution Starting...")
        print("=" * 60)
        self.evolution_state["current_goal"] = goal
        goal_description = goal.get("description", "Improve T-Developer")
        constraints = goal.get("constraints", [])
        success_criteria = goal.get("success_criteria", {})
        max_cycles = goal.get("max_cycles", self.max_cycles)
        use_ai = goal.get("use_ai", False)
        evolution_result = {
            "goal": goal_description,
            "start_time": datetime.now().isoformat(),
            "cycles": [],
            "final_state": None,
            "success": False,
            "total_improvements": 0,
        }
        initial_snapshot = await self._create_snapshot("initial")
        for cycle_num in range(1, max_cycles + 1):
            print(f"\n🔄 Evolution Cycle {cycle_num}/{max_cycles}")
            print("-" * 40)
            cycle_result = await self._execute_cycle(
                cycle_num=cycle_num, goal=goal_description, constraints=constraints, use_ai=use_ai
            )
            evolution_result["cycles"].append(cycle_result)
            if cycle_result["success"]:
                evolution_result["total_improvements"] += cycle_result.get("improvements_made", 0)
                if self._check_success_criteria(cycle_result, success_criteria):
                    print(f"\n✅ Evolution Goal Achieved in Cycle {cycle_num}!")
                    evolution_result["success"] = True
                    break
            else:
                print(f"\n⚠️ Cycle {cycle_num} did not meet success criteria")
            if self._is_evolution_stagnant(evolution_result["cycles"]):
                print("\n⚠️ Evolution appears to be stagnant. Stopping.")
                break
        final_snapshot = await self._create_snapshot("final")
        evolution_result["comparison"] = await self._compare_snapshots(
            initial_snapshot, final_snapshot
        )
        evolution_result["end_time"] = datetime.now().isoformat()
        evolution_result["final_state"] = self.evolution_state
        self._save_evolution_history(evolution_result)
        print("\n" + "=" * 60)
        print("🧬 Evolution Complete!")
        print(f"Success: {evolution_result['success']}")
        print(f"Total Cycles: {len(evolution_result['cycles'])}")
        print(f"Total Improvements: {evolution_result['total_improvements']}")
        print("=" * 60)
        return evolution_result

    async def _execute_cycle(
        self, cycle_num: int, goal: str, constraints: List[str], use_ai: bool
    ) -> Dict[str, Any]:
        """단일 진화 사이클 실행"""
        cycle_result = {
            "cycle": cycle_num,
            "phases": {},
            "success": False,
            "improvements_made": 0,
            "score": 0.0,
        }
        try:
            print("\n📚 Phase 1: Research")
            research_result = await self.research_agent.execute(
                {
                    "goal": goal,
                    "target": self.target_path,
                    "focus_areas": ["code_quality", "architecture", "performance"],
                }
            )
            cycle_result["phases"]["research"] = research_result
            if "error" in research_result:
                print(f"❌ Research failed: {research_result['error']}")
                return cycle_result
            print("\n📋 Phase 2: Planning")
            plan_result = await self.planner_agent.execute(
                {
                    "goal": goal,
                    "research_insights": research_result.get("insights", []),
                    "constraints": constraints + ["Maximum 4 hours per task"],
                    "prioritization": "impact",
                }
            )
            cycle_result["phases"]["planning"] = plan_result
            if "error" in plan_result:
                print(f"❌ Planning failed: {plan_result['error']}")
                return cycle_result
            print("\n🔧 Phase 3: Refactoring")
            work_units = plan_result.get("work_units", [])
            refactor_results = []
            for i, unit in enumerate(work_units[:3], 1):
                if isinstance(unit, dict):
                    unit_name = unit.get("name", f"Task {i}")
                    unit_hours = unit.get("estimated_hours", 1)
                else:
                    unit_name = f"Task {i}"
                    unit_hours = 1
                    unit = {"name": unit_name, "estimated_hours": unit_hours}
                print(f"  Working on: {unit_name} ({unit_hours}h)")
                target_files = self._determine_target_files(unit)
                for target_file in target_files:
                    refactor_result = await self.refactor_agent.execute(
                        {
                            "target": target_file,
                            "improvement_type": self._map_task_to_improvement_type(unit),
                            "plan": unit,
                            "use_ai": use_ai,
                            "auto_commit": False,
                        }
                    )
                    refactor_results.append(refactor_result)
                    if refactor_result.get("files_modified"):
                        cycle_result["improvements_made"] += len(refactor_result["files_modified"])
            cycle_result["phases"]["refactoring"] = refactor_results
            print("\n📊 Phase 4: Evaluation")
            all_modified_files = []
            for result in refactor_results:
                all_modified_files.extend(result.get("files_modified", []))
            if all_modified_files:
                eval_result = await self.evaluator_agent.execute(
                    {
                        "before": self.target_path,
                        "after": self.target_path,
                        "criteria": ["quality", "documentation", "complexity"],
                        "target_metrics": {"docstring_coverage": 60, "quality_score": 70},
                        "run_tests": False,
                    }
                )
                cycle_result["phases"]["evaluation"] = eval_result
                cycle_result["success"] = eval_result.get("success", False)
                cycle_result["score"] = eval_result.get("score", 0.0)
                print(f"\n📈 Cycle Score: {cycle_result['score']}/100")
                print(f"   Improvements: {cycle_result['improvements_made']} files")
            else:
                print("⚠️ No files were modified in this cycle")
        except Exception as e:
            print(f"❌ Cycle failed with error: {e}")
            cycle_result["error"] = str(e)
        self.evolution_state["cycles_completed"] += 1
        self.evolution_state["total_improvements"] += cycle_result["improvements_made"]
        return cycle_result

    def _determine_target_files(self, work_unit: Dict) -> List[str]:
        """작업 단위에서 타겟 파일 결정"""
        task_name = work_unit.get("name", "").lower()
        if "research" in task_name:
            return [f"{self.target_path}/backend/src/agents/evolution/research_agent.py"]
        elif "planner" in task_name or "planning" in task_name:
            return [f"{self.target_path}/backend/src/agents/evolution/planner_agent.py"]
        elif "refactor" in task_name:
            return [f"{self.target_path}/backend/src/agents/evolution/refactor_agent.py"]
        elif "evaluat" in task_name:
            return [f"{self.target_path}/backend/src/agents/evolution/evaluator_agent.py"]
        elif "registry" in task_name:
            return [f"{self.target_path}/backend/src/agents/registry/agent_registry.py"]
        else:
            return [f"{self.target_path}/backend/src/agents/evolution/"]

    def _map_task_to_improvement_type(self, work_unit: Dict) -> List[str]:
        """작업을 개선 타입으로 매핑"""
        task_name = work_unit.get("name", "").lower()
        if "document" in task_name:
            return ["docstring"]
        elif "type" in task_name or "hint" in task_name:
            return ["type_hints"]
        elif "optim" in task_name:
            return ["optimization"]
        elif "refactor" in task_name:
            return ["refactor"]
        else:
            return ["docstring", "type_hints"]

    def _check_success_criteria(self, cycle_result: Dict, criteria: Dict) -> bool:
        """성공 기준 확인"""
        if not criteria:
            return cycle_result.get("score", 0) >= 70
        eval_result = cycle_result.get("phases", {}).get("evaluation", {})
        metrics = eval_result.get("metrics", {}).get("after", {})
        for metric, target_value in criteria.items():
            actual_value = metrics.get(metric, 0)
            if actual_value < target_value:
                return False
        return True

    def _is_evolution_stagnant(self, cycles: List[Dict]) -> bool:
        """진화 정체 감지"""
        if len(cycles) < 3:
            return False
        recent_scores = [c.get("score", 0) for c in cycles[-3:]]
        if max(recent_scores) - min(recent_scores) < self.min_improvement_threshold:
            return True
        recent_successes = [c.get("success", False) for c in cycles[-3:]]
        if not any(recent_successes):
            return True
        return False

    async def _create_snapshot(self, label: str) -> Dict:
        """코드 스냅샷 생성"""
        snapshot = {"label": label, "timestamp": datetime.now().isoformat(), "metrics": {}}
        analyzer = self.evaluator_agent
        metrics = await analyzer._collect_metrics(
            self.target_path, ["quality", "documentation", "complexity"]
        )
        snapshot["metrics"] = metrics
        return snapshot

    async def _compare_snapshots(self, before: Dict, after: Dict) -> Dict:
        """스냅샷 비교"""
        comparison = {"improvement_summary": [], "regression_summary": [], "overall_change": 0}
        before_metrics = before.get("metrics", {})
        after_metrics = after.get("metrics", {})
        key_metrics = [
            ("docstring_coverage", True),
            ("quality_score", True),
            ("cyclomatic_complexity", False),
            ("todo_count", False),
        ]
        for metric, higher_is_better in key_metrics:
            before_val = before_metrics.get(metric, 0)
            after_val = after_metrics.get(metric, 0)
            if before_val != after_val:
                change = after_val - before_val
                change_pct = change / max(1, before_val) * 100 if before_val else 100
                is_improvement = (
                    change > 0 and higher_is_better or (change < 0 and (not higher_is_better))
                )
                summary = f"{metric}: {before_val:.1f} → {after_val:.1f} ({change_pct:+.1f}%)"
                if is_improvement:
                    comparison["improvement_summary"].append(summary)
                    comparison["overall_change"] += abs(change_pct)
                else:
                    comparison["regression_summary"].append(summary)
                    comparison["overall_change"] -= abs(change_pct)
        return comparison

    def _save_evolution_history(self, result: Dict) -> Any:
        """진화 히스토리 저장"""
        history_file = self.evolution_dir / "evolution_history.json"
        if history_file.exists():
            with open(history_file, "r") as f:
                history = json.load(f)
        else:
            history = []
        history.append(
            {
                "timestamp": result["start_time"],
                "goal": result["goal"],
                "success": result["success"],
                "cycles": len(result["cycles"]),
                "improvements": result["total_improvements"],
                "final_score": result["cycles"][-1]["score"] if result["cycles"] else 0,
            }
        )
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
        self.evolution_state["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "cycles": len(result["cycles"]),
                "success": result["success"],
            }
        )

    async def analyze_self(self) -> Dict[str, Any]:
        """T-Developer 자체 분석"""
        print("\n🔍 Analyzing T-Developer itself...")
        analysis = await self.research_agent.execute(
            {
                "goal": "Analyze T-Developer for self-improvement opportunities",
                "target": self.target_path,
                "focus_areas": ["architecture", "code_quality", "documentation", "testing"],
            }
        )
        summary = {
            "project": "T-Developer MVP",
            "analysis": analysis,
            "recommendations": [],
            "evolution_readiness": 0,
        }
        if analysis.get("insights"):
            for insight in analysis["insights"]:
                if "improve" in insight.lower() or "add" in insight.lower():
                    summary["recommendations"].append(insight)
        readiness_score = 0
        if os.path.exists(f"{self.target_path}/backend/src/agents/evolution"):
            readiness_score += 25
        if os.path.exists(f"{self.target_path}/backend/src/agents/registry"):
            readiness_score += 25
        if len(summary["recommendations"]) > 0:
            readiness_score += 25
        if analysis.get("projects_analyzed", 0) > 0:
            readiness_score += 25
        summary["evolution_readiness"] = readiness_score
        print(f"\n📊 Evolution Readiness: {readiness_score}%")
        print(f"📝 Recommendations Found: {len(summary['recommendations'])}")
        return summary


async def main():
    """테스트 실행"""
    orchestrator = EvolutionOrchestrator()
    print("\n" + "=" * 60)
    print("🧬 T-Developer Self-Analysis")
    print("=" * 60)
    analysis = await orchestrator.analyze_self()
    print(f"\nEvolution Readiness: {analysis['evolution_readiness']}%")
    if analysis["recommendations"]:
        print("\nTop Recommendations:")
        for i, rec in enumerate(analysis["recommendations"][:3], 1):
            print(f"  {i}. {rec}")
    if analysis["evolution_readiness"] >= 75:
        print("\n" + "=" * 60)
        print("🚀 Starting First Evolution Cycle")
        print("=" * 60)
        evolution_goal = {
            "description": "Add docstrings to all evolution agents",
            "constraints": [
                "Preserve existing functionality",
                "Follow Google docstring style",
                "Keep changes minimal",
            ],
            "success_criteria": {"docstring_coverage": 60},
            "max_cycles": 2,
            "use_ai": False,
        }
        result = await orchestrator.evolve(evolution_goal)
        print("\n📊 Evolution Results:")
        print(f"  Success: {result['success']}")
        print(f"  Cycles Run: {len(result['cycles'])}")
        print(f"  Files Improved: {result['total_improvements']}")
        if result.get("comparison"):
            comp = result["comparison"]
            if comp["improvement_summary"]:
                print("\n✅ Improvements:")
                for imp in comp["improvement_summary"]:
                    print(f"  - {imp}")
            if comp["regression_summary"]:
                print("\n⚠️ Regressions:")
                for reg in comp["regression_summary"]:
                    print(f"  - {reg}")
    else:
        print("\n⚠️ Evolution readiness too low. Please ensure all components are properly set up.")


if __name__ == "__main__":
    asyncio.run(main())
