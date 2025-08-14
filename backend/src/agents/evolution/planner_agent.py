"""PlannerAgent - Hierarchical Planning System for T-Developer Evolution"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.agents.evolution.base_agent import BaseEvolutionAgent


class PlannerAgent(BaseEvolutionAgent):
    """
    계획 수립 에이전트
    방법론: 목표 → 대분류 → 중분류 → 소분류 → 4시간 이하 작업 단위
    """

    def __init__(self) -> Any:
        """Function __init__(self)"""
        super().__init__(name="PlannerAgent", version="1.0.0")
        self.max_task_hours = 4
        self.human_work_hours_per_day = 8

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        계획 수립 실행
        input_data: {
            "goal": "최종 목표",
            "current_state": "현재 상태 분석",
            "research_data": "ResearchAgent의 조사 결과",
            "constraints": "제약 조건"
        }
        """
        goal = input_data.get("goal", "")
        current_state = input_data.get("current_state", {})
        research_data = input_data.get("research_data", {})
        objectives = self._define_objectives(goal, current_state)
        phases = self._create_phases(objectives, research_data)
        milestones = self._create_milestones(phases)
        tasks = self._create_tasks(milestones)
        work_units = self._decompose_to_work_units(tasks)
        execution_plan = self._generate_execution_plan(work_units)
        result = {
            "objectives": objectives,
            "phases": phases,
            "milestones": milestones,
            "tasks": tasks,
            "work_units": work_units,
            "execution_plan": execution_plan,
            "total_estimated_hours": self._calculate_total_hours(work_units),
            "estimated_completion_date": self._estimate_completion_date(work_units),
        }
        self.log_execution(input_data, result)
        return result

    def _define_objectives(self, goal: str, current_state: Dict) -> List[Dict]:
        """목표를 구체적인 달성 목표로 변환"""
        return [
            {
                "id": "obj_1",
                "title": "Core System 구축",
                "description": f"T-Developer 핵심 시스템 구현: {goal}",
                "success_criteria": ["Agent Registry 완성", "Evolution Loop 작동"],
                "priority": 1,
            },
            {
                "id": "obj_2",
                "title": "Self-Evolution 구현",
                "description": "자기 개선 사이클 구현",
                "success_criteria": ["자동 코드 분석", "자동 개선 실행"],
                "priority": 2,
            },
        ]

    def _create_phases(self, objectives: List[Dict], research_data: Dict) -> List[Dict]:
        """대분류 단계 생성 (몇 주 단위)"""
        phases = []
        for i, obj in enumerate(objectives):
            phases.append(
                {
                    "id": f"phase_{i + 1}",
                    "objective_id": obj["id"],
                    "title": f"Phase {i + 1}: {obj['title']}",
                    "estimated_weeks": 2,
                    "dependencies": [] if i == 0 else [f"phase_{i}"],
                    "research_insights": research_data.get("relevant_projects", []),
                }
            )
        return phases

    def _create_milestones(self, phases: List[Dict]) -> List[Dict]:
        """중분류 마일스톤 생성 (며칠 단위)"""
        milestones = []
        milestone_id = 1
        for phase in phases:
            milestone_count = 3
            for i in range(milestone_count):
                milestones.append(
                    {
                        "id": f"ms_{milestone_id}",
                        "phase_id": phase["id"],
                        "title": f"{phase['title']} - Milestone {i + 1}",
                        "estimated_days": phase["estimated_weeks"] * 7 / milestone_count,
                        "deliverables": [f"Component {milestone_id}.{j}" for j in range(1, 3)],
                    }
                )
                milestone_id += 1
        return milestones

    def _create_tasks(self, milestones: List[Dict]) -> List[Dict]:
        """소분류 작업 생성 (몇 시간 단위)"""
        tasks = []
        task_id = 1
        for milestone in milestones:
            task_count = 7
            for i in range(task_count):
                estimated_hours = (
                    milestone["estimated_days"] * self.human_work_hours_per_day / task_count
                )
                tasks.append(
                    {
                        "id": f"task_{task_id}",
                        "milestone_id": milestone["id"],
                        "title": f"Task {task_id}: {milestone['title'][:20]}... 작업 {i + 1}",
                        "estimated_hours": estimated_hours,
                        "type": self._determine_task_type(i),
                        "requires_decomposition": estimated_hours > self.max_task_hours,
                    }
                )
                task_id += 1
        return tasks

    def _decompose_to_work_units(self, tasks: List[Dict]) -> List[Dict]:
        """4시간 이하 작업 단위로 분해"""
        work_units = []
        work_unit_id = 1
        for task in tasks:
            if task["requires_decomposition"]:
                num_units = int(task["estimated_hours"] / self.max_task_hours) + 1
                hours_per_unit = task["estimated_hours"] / num_units
                for i in range(num_units):
                    work_units.append(
                        {
                            "id": f"wu_{work_unit_id}",
                            "task_id": task["id"],
                            "title": f"{task['title']} - Part {i + 1}/{num_units}",
                            "estimated_hours": round(hours_per_unit, 1),
                            "type": task["type"],
                            "sequence": i + 1,
                            "executable": True,
                        }
                    )
                    work_unit_id += 1
            else:
                work_units.append(
                    {
                        "id": f"wu_{work_unit_id}",
                        "task_id": task["id"],
                        "title": task["title"],
                        "estimated_hours": round(task["estimated_hours"], 1),
                        "type": task["type"],
                        "sequence": 1,
                        "executable": True,
                    }
                )
                work_unit_id += 1
        return work_units

    def _generate_execution_plan(self, work_units: List[Dict]) -> Dict:
        """실행 가능한 일정 계획 생성"""
        daily_schedule = []
        current_day = 1
        daily_hours = 0
        day_tasks = []
        for unit in work_units:
            if daily_hours + unit["estimated_hours"] > self.human_work_hours_per_day:
                daily_schedule.append(
                    {"day": current_day, "tasks": day_tasks, "total_hours": round(daily_hours, 1)}
                )
                current_day += 1
                daily_hours = unit["estimated_hours"]
                day_tasks = [unit]
            else:
                daily_hours += unit["estimated_hours"]
                day_tasks.append(unit)
        if day_tasks:
            daily_schedule.append(
                {"day": current_day, "tasks": day_tasks, "total_hours": round(daily_hours, 1)}
            )
        return {
            "total_days": current_day,
            "daily_schedule": daily_schedule,
            "parallel_opportunities": self._identify_parallel_tasks(work_units),
        }

    def _determine_task_type(self, index: int) -> str:
        """작업 유형 결정"""
        types = [
            "research",
            "design",
            "implementation",
            "testing",
            "refactoring",
            "documentation",
            "review",
        ]
        return types[index % len(types)]

    def _calculate_total_hours(self, work_units: List[Dict]) -> float:
        """총 예상 시간 계산"""
        return sum((unit["estimated_hours"] for unit in work_units))

    def _estimate_completion_date(self, work_units: List[Dict]) -> str:
        """예상 완료일 계산"""
        total_hours = self._calculate_total_hours(work_units)
        total_days = int(total_hours / self.human_work_hours_per_day) + 1
        completion_date = datetime.now() + timedelta(days=total_days)
        return completion_date.strftime("%Y-%m-%d")

    def _identify_parallel_tasks(self, work_units: List[Dict]) -> List[List[str]]:
        """병렬 실행 가능한 작업 식별"""
        parallel_groups = []
        by_type = {}
        for unit in work_units:
            if unit["type"] not in by_type:
                by_type[unit["type"]] = []
            by_type[unit["type"]].append(unit["id"])
        for task_type, unit_ids in by_type.items():
            if len(unit_ids) > 1:
                parallel_groups.append(unit_ids[:3])
        return parallel_groups

    def get_capabilities(self) -> List[str]:
        """에이전트 능력 목록"""
        return [
            "hierarchical_planning",
            "task_decomposition",
            "time_estimation",
            "dependency_analysis",
            "parallel_task_identification",
            "milestone_tracking",
            "4h_work_unit_creation",
        ]
