"""
Agno Framework Runtime Executor
동적으로 생성된 에이전트들을 실행하는 런타임 엔진
"""

import asyncio
from typing import Dict, Any, List, Optional
import time
import json


class AgnoRuntimeExecutor:
    """동적 생성 에이전트 실행 엔진"""

    def __init__(self):
        self.active_agents = {}
        self.execution_history = []
        self.performance_metrics = {
            "total_executions": 0,
            "average_execution_time_ms": 0,
            "success_rate": 1.0,
        }

    async def execute_agent_operation(
        self, agent: Any, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        에이전트의 특정 작업 실행
        """
        start_time = time.perf_counter()

        try:
            # 에이전트가 execute 메소드를 가지고 있는지 확인
            if hasattr(agent, "execute"):
                result = await agent.execute(operation, params)
            # 직접 메소드 호출
            elif hasattr(agent, operation):
                method = getattr(agent, operation)
                if asyncio.iscoroutinefunction(method):
                    result = await method(**params)
                else:
                    result = method(**params)
            else:
                raise AttributeError(f"Agent has no operation: {operation}")

            # 성능 메트릭 업데이트
            execution_time = (time.perf_counter() - start_time) * 1000
            self._update_metrics(execution_time, success=True)

            # 실행 이력 저장
            self.execution_history.append(
                {
                    "agent_name": agent.name if hasattr(agent, "name") else "unknown",
                    "operation": operation,
                    "params": params,
                    "result": result,
                    "execution_time_ms": execution_time,
                    "timestamp": time.time(),
                    "success": True,
                }
            )

            return {
                "success": True,
                "result": result,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            self._update_metrics(execution_time, success=False)

            self.execution_history.append(
                {
                    "agent_name": agent.name if hasattr(agent, "name") else "unknown",
                    "operation": operation,
                    "params": params,
                    "error": str(e),
                    "execution_time_ms": execution_time,
                    "timestamp": time.time(),
                    "success": False,
                }
            )

            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time,
            }

    async def execute_agent_pipeline(
        self, agents: List[Any], operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        여러 에이전트를 순차적으로 실행하는 파이프라인
        """
        pipeline_start = time.perf_counter()
        results = []
        current_data = {}

        for i, (agent, operation_config) in enumerate(zip(agents, operations)):
            operation = operation_config.get("operation")
            params = operation_config.get("params", {})

            # 이전 결과를 현재 파라미터에 병합
            if operation_config.get("use_previous_result", True):
                params.update(current_data)

            # 에이전트 실행
            result = await self.execute_agent_operation(agent, operation, params)
            results.append(result)

            # 성공한 경우 결과를 다음 단계로 전달
            if result["success"]:
                current_data = result.get("result", {})
            else:
                # 실패 시 파이프라인 중단
                break

        pipeline_time = (time.perf_counter() - pipeline_start) * 1000

        return {
            "pipeline_execution_time_ms": pipeline_time,
            "steps": results,
            "final_result": current_data,
            "success": all(r["success"] for r in results),
        }

    async def execute_parallel_agents(
        self, agent_operations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        여러 에이전트를 병렬로 실행
        """
        tasks = []

        for config in agent_operations:
            agent = config["agent"]
            operation = config["operation"]
            params = config.get("params", {})

            task = self.execute_agent_operation(agent, operation, params)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 예외를 결과로 변환
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({"success": False, "error": str(result)})
            else:
                processed_results.append(result)

        return processed_results

    def _update_metrics(self, execution_time: float, success: bool):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_executions"] += 1

        # 평균 실행 시간 업데이트
        total = self.performance_metrics["total_executions"]
        current_avg = self.performance_metrics["average_execution_time_ms"]
        new_avg = ((current_avg * (total - 1)) + execution_time) / total
        self.performance_metrics["average_execution_time_ms"] = new_avg

        # 성공률 업데이트
        if not success:
            self.performance_metrics["success_rate"] *= 0.99

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """실행 이력 조회"""
        return self.execution_history[-limit:]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        return self.performance_metrics

    def register_agent(self, name: str, agent: Any):
        """에이전트 등록"""
        self.active_agents[name] = agent

    def get_agent(self, name: str) -> Optional[Any]:
        """등록된 에이전트 조회"""
        return self.active_agents.get(name)


class TodoAppRuntime:
    """Todo 앱 전용 런타임"""

    def __init__(self, agents: Dict[str, Any]):
        self.executor = AgnoRuntimeExecutor()
        self.agents = agents

        # 에이전트 등록
        for name, agent in agents.items():
            self.executor.register_agent(name, agent)

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 작업 생성"""
        crud_agent = self.agents.get("TodoCRUDAgent")
        if not crud_agent:
            return {"error": "CRUD agent not found"}

        # 우선순위 자동 할당 (Priority Agent 사용)
        priority_agent = self.agents.get("TaskPriorityAgent")
        if priority_agent:
            priority_result = await self.executor.execute_agent_operation(
                priority_agent,
                "execute",
                {"method_name": "autoAssignPriority", "params": {"task": task_data}},
            )
            if priority_result["success"]:
                task_data = priority_result["result"]

        # CRUD Agent로 생성
        result = await self.executor.execute_agent_operation(
            crud_agent, "create", {"data": task_data}
        )

        # 저장소에 저장
        storage_agent = self.agents.get("TaskPersistenceAgent")
        if storage_agent and result["success"]:
            await self.executor.execute_agent_operation(
                storage_agent,
                "execute",
                {
                    "operation": "save",
                    "params": {
                        "key": f"task_{result['result']['id']}",
                        "data": result["result"],
                    },
                },
            )

        return result

    async def get_filtered_tasks(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """필터링된 작업 목록 조회"""
        crud_agent = self.agents.get("TodoCRUDAgent")
        filter_agent = self.agents.get("TaskFilterAgent")

        if not crud_agent:
            return {"error": "CRUD agent not found"}

        # 모든 작업 조회
        all_tasks_result = await self.executor.execute_agent_operation(
            crud_agent, "list", {"filter": {}}
        )

        if not all_tasks_result["success"]:
            return all_tasks_result

        # 필터 적용
        if filter_agent and filters:
            filtered_result = await self.executor.execute_agent_operation(
                filter_agent,
                "execute",
                {
                    "operation": "filter",
                    "data": all_tasks_result["result"],
                    "params": filters,
                },
            )
            return filtered_result

        return all_tasks_result

    async def get_task_statistics(self) -> Dict[str, Any]:
        """작업 통계 조회"""
        crud_agent = self.agents.get("TodoCRUDAgent")
        stats_agent = self.agents.get("TaskStatisticsAgent")

        if not crud_agent:
            return {"error": "CRUD agent not found"}

        # 모든 작업 조회
        all_tasks_result = await self.executor.execute_agent_operation(
            crud_agent, "list", {"filter": {}}
        )

        if not all_tasks_result["success"]:
            return all_tasks_result

        # 통계 생성
        if stats_agent:
            stats_result = await self.executor.execute_agent_operation(
                stats_agent,
                "execute",
                {
                    "operation": "metrics",
                    "params": {"data": all_tasks_result["result"]},
                },
            )
            return stats_result

        return {"error": "Statistics agent not found"}

    async def run_complete_workflow(self, user_input: str) -> Dict[str, Any]:
        """완전한 Todo 앱 워크플로우 실행"""
        workflow_results = {"user_input": user_input, "steps": [], "final_result": None}

        # 1. 작업 생성 테스트
        if "create" in user_input.lower() or "add" in user_input.lower():
            create_result = await self.create_task(
                {
                    "title": "Sample task from user input",
                    "description": user_input,
                    "completed": False,
                }
            )
            workflow_results["steps"].append(
                {"step": "create_task", "result": create_result}
            )

        # 2. 작업 목록 조회
        list_result = await self.get_filtered_tasks({})
        workflow_results["steps"].append({"step": "list_tasks", "result": list_result})

        # 3. 통계 생성
        stats_result = await self.get_task_statistics()
        workflow_results["steps"].append(
            {"step": "generate_statistics", "result": stats_result}
        )

        # 4. 성능 메트릭
        metrics = self.executor.get_performance_metrics()
        workflow_results["performance_metrics"] = metrics

        workflow_results["final_result"] = {
            "tasks_count": len(list_result.get("result", []))
            if list_result.get("success")
            else 0,
            "statistics": stats_result.get("result")
            if stats_result.get("success")
            else {},
            "success": all(
                step["result"].get("success", False)
                for step in workflow_results["steps"]
            ),
        }

        return workflow_results


# 글로벌 인스턴스
runtime_executor = AgnoRuntimeExecutor()


async def test_runtime():
    """런타임 실행기 테스트"""
    from src.agno.agent_generator import create_agent_from_blueprint

    # 테스트용 에이전트 생성
    crud_blueprint = {
        "name": "TodoCRUDAgent",
        "type": "data_manager",
        "config": {
            "entity": "Task",
            "fields": {"id": "string", "title": "string", "completed": "boolean"},
            "validation_rules": {"title": {"required": True}},
        },
    }

    crud_agent = await create_agent_from_blueprint(crud_blueprint)

    # 에이전트 실행
    result = await runtime_executor.execute_agent_operation(
        crud_agent, "create", {"data": {"title": "Test task", "completed": False}}
    )

    print(f"Execution result: {result}")
    print(f"Performance metrics: {runtime_executor.get_performance_metrics()}")


if __name__ == "__main__":
    asyncio.run(test_runtime())
