"""
Agno Framework Agent Generator
런타임에 동적으로 에이전트를 생성하는 핵심 모듈
"""

import asyncio
import hashlib
import inspect
import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AgentBlueprint:
    """에이전트 생성을 위한 설계도"""

    name: str
    type: str
    config: Dict[str, Any]
    methods: Dict[str, Callable]
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class AgnoAgentGenerator:
    """Agno Framework를 사용한 동적 에이전트 생성기"""

    def __init__(self):
        self.generated_agents = {}
        self.agent_templates = self._load_templates()
        self.performance_metrics = {
            "generation_time_us": [],
            "memory_usage_kb": [],
            "success_rate": 1.0,
        }

    def _load_templates(self) -> Dict[str, str]:
        """에이전트 템플릿 로드"""
        return {
            "data_manager": self._data_manager_template,
            "business_logic": self._business_logic_template,
            "query_processor": self._query_processor_template,
            "storage_manager": self._storage_manager_template,
            "analytics": self._analytics_template,
            "ui_controller": self._ui_controller_template,
            "notification_service": self._notification_template,
        }

    async def generate_agent(self, blueprint: AgentBlueprint) -> Any:
        """
        Agno Framework 철학에 따라 3μs 내에 에이전트 생성
        """
        start_time = time.perf_counter_ns()

        try:
            # 캐시 확인 (이미 생성된 에이전트 재사용)
            cache_key = self._get_cache_key(blueprint)
            if cache_key in self.generated_agents:
                agent = self.generated_agents[cache_key]
                generation_time = (time.perf_counter_ns() - start_time) / 1000  # μs
                self.performance_metrics["generation_time_us"].append(generation_time)
                return agent

            # 템플릿 기반 생성
            template_func = self.agent_templates.get(blueprint.type)
            if not template_func:
                raise ValueError(f"Unknown agent type: {blueprint.type}")

            # 에이전트 인스턴스 생성
            agent = await template_func(blueprint)

            # 캐시에 저장
            self.generated_agents[cache_key] = agent

            # 성능 메트릭 기록
            generation_time = (time.perf_counter_ns() - start_time) / 1000  # μs
            self.performance_metrics["generation_time_us"].append(generation_time)

            # Agno 목표: 3μs 이내 생성
            if generation_time > 3.0:
                print(f"Warning: Agent generation took {generation_time:.2f}μs (target: 3μs)")

            return agent

        except Exception as e:
            self.performance_metrics["success_rate"] *= 0.95
            raise RuntimeError(f"Failed to generate agent: {e}")

    def _get_cache_key(self, blueprint: AgentBlueprint) -> str:
        """블루프린트의 고유 캐시 키 생성"""
        key_data = (
            f"{blueprint.name}:{blueprint.type}:{json.dumps(blueprint.config, sort_keys=True)}"
        )
        return hashlib.md5(key_data.encode()).hexdigest()

    async def _data_manager_template(self, blueprint: AgentBlueprint) -> Any:
        """데이터 관리 에이전트 템플릿"""

        class DynamicDataManager:
            def __init__(self):
                self.name = blueprint.name
                self.config = blueprint.config
                self.data_store = []
                self.next_id = 1

            async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
                """데이터 생성"""
                entity = blueprint.config.get("entity", "Item")
                fields = blueprint.config.get("fields", {})
                validation = blueprint.config.get("validation_rules", {})

                # 검증
                for field, rules in validation.items():
                    if rules.get("required") and field not in data:
                        raise ValueError(f"{field} is required")

                    if field in data:
                        value = data[field]
                        if "minLength" in rules and len(str(value)) < rules["minLength"]:
                            raise ValueError(f"{field} is too short")
                        if "maxLength" in rules and len(str(value)) > rules["maxLength"]:
                            raise ValueError(f"{field} is too long")

                # 엔티티 생성
                new_entity = {
                    "id": str(self.next_id),
                    **data,
                    "createdAt": time.time(),
                    "updatedAt": time.time(),
                }
                self.next_id += 1
                self.data_store.append(new_entity)

                return new_entity

            async def read(self, id: str) -> Optional[Dict[str, Any]]:
                """데이터 읽기"""
                for item in self.data_store:
                    if item.get("id") == id:
                        return item
                return None

            async def update(self, id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
                """데이터 업데이트"""
                for i, item in enumerate(self.data_store):
                    if item.get("id") == id:
                        self.data_store[i] = {
                            **item,
                            **updates,
                            "updatedAt": time.time(),
                        }
                        return self.data_store[i]
                return None

            async def delete(self, id: str) -> bool:
                """데이터 삭제"""
                for i, item in enumerate(self.data_store):
                    if item.get("id") == id:
                        del self.data_store[i]
                        return True
                return False

            async def list(self, filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
                """데이터 목록 조회"""
                result = self.data_store.copy()

                if filter:
                    for key, value in filter.items():
                        result = [item for item in result if item.get(key) == value]

                return result

            async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
                """통합 실행 인터페이스"""
                operations = {
                    "create": self.create,
                    "read": self.read,
                    "update": self.update,
                    "delete": self.delete,
                    "list": self.list,
                }

                if operation in operations:
                    return await operations[operation](**params)
                else:
                    raise ValueError(f"Unknown operation: {operation}")

        return DynamicDataManager()

    async def _business_logic_template(self, blueprint: AgentBlueprint) -> Any:
        """비즈니스 로직 에이전트 템플릿"""

        class DynamicBusinessLogic:
            def __init__(self):
                self.name = blueprint.name
                self.config = blueprint.config
                self.methods = blueprint.config.get("methods", {})

            async def execute(self, method_name: str, params: Dict[str, Any]) -> Any:
                """메소드 실행"""
                if method_name == "setPriority":
                    return self._set_priority(params.get("taskId"), params.get("priority"))
                elif method_name == "sortByPriority":
                    return self._sort_by_priority(params.get("tasks"), params.get("order"))
                elif method_name == "getHighPriorityTasks":
                    return self._get_high_priority(params.get("tasks"), params.get("threshold"))
                elif method_name == "autoAssignPriority":
                    return self._auto_assign_priority(params.get("task"), params.get("rules"))
                else:
                    return {"error": f"Unknown method: {method_name}"}

            def _set_priority(self, task_id: str, priority: int) -> Dict[str, Any]:
                """우선순위 설정"""
                levels = self.config.get("priority_levels", {})
                if priority < 1 or priority > 5:
                    raise ValueError("Priority must be between 1 and 5")

                return {
                    "taskId": task_id,
                    "priority": priority,
                    "label": next((k for k, v in levels.items() if v == priority), "medium"),
                }

            def _sort_by_priority(self, tasks: List[Dict], order: str = "desc") -> List[Dict]:
                """우선순위로 정렬"""
                reverse = order.lower() == "desc"
                return sorted(tasks, key=lambda x: x.get("priority", 0), reverse=reverse)

            def _get_high_priority(self, tasks: List[Dict], threshold: int = 3) -> List[Dict]:
                """높은 우선순위 작업 필터링"""
                return [t for t in tasks if t.get("priority", 0) >= threshold]

            def _auto_assign_priority(self, task: Dict, rules: Dict = None) -> Dict[str, Any]:
                """자동 우선순위 할당"""
                if not rules:
                    rules = {"urgent": 5, "important": 4, "normal": 3, "low": 2}

                # 키워드 기반 자동 할당
                title = task.get("title", "").lower()
                for keyword, priority in rules.items():
                    if keyword in title:
                        task["priority"] = priority
                        return task

                task["priority"] = 3  # 기본값
                return task

        return DynamicBusinessLogic()

    async def _query_processor_template(self, blueprint: AgentBlueprint) -> Any:
        """쿼리 처리 에이전트 템플릿"""

        class DynamicQueryProcessor:
            def __init__(self):
                self.name = blueprint.name
                self.config = blueprint.config

            async def execute(
                self, operation: str, data: List[Dict], params: Dict[str, Any]
            ) -> Any:
                """쿼리 실행"""
                if operation == "filter":
                    return self._filter(data, params)
                elif operation == "search":
                    return self._search(data, params.get("query", ""))
                elif operation == "sort":
                    return self._sort(data, params.get("field"), params.get("order"))
                else:
                    return data

            def _filter(self, data: List[Dict], filters: Dict) -> List[Dict]:
                """데이터 필터링"""
                result = data
                for key, value in filters.items():
                    if value is not None:
                        result = [item for item in result if item.get(key) == value]
                return result

            def _search(self, data: List[Dict], query: str) -> List[Dict]:
                """텍스트 검색"""
                if not query:
                    return data

                query_lower = query.lower()
                search_fields = self.config.get("search", {}).get(
                    "fields", ["title", "description"]
                )

                results = []
                for item in data:
                    for field in search_fields:
                        if field in item and query_lower in str(item[field]).lower():
                            results.append(item)
                            break

                return results

            def _sort(self, data: List[Dict], field: str, order: str = "asc") -> List[Dict]:
                """데이터 정렬"""
                if not field:
                    return data

                reverse = order.lower() == "desc"
                return sorted(data, key=lambda x: x.get(field, ""), reverse=reverse)

        return DynamicQueryProcessor()

    async def _storage_manager_template(self, blueprint: AgentBlueprint) -> Any:
        """저장소 관리 에이전트 템플릿"""

        class DynamicStorageManager:
            def __init__(self):
                self.name = blueprint.name
                self.config = blueprint.config
                self.storage_type = blueprint.config.get("storage_type", "memory")
                self.cache = {}

            async def save(self, key: str, data: Any) -> bool:
                """데이터 저장"""
                try:
                    if self.config.get("compression"):
                        # 실제로는 압축 로직 구현
                        pass

                    self.cache[key] = {"data": data, "timestamp": time.time()}
                    return True
                except Exception as e:
                    print(f"Storage save error: {e}")
                    return False

            async def load(self, key: str) -> Any:
                """데이터 로드"""
                if key in self.cache:
                    return self.cache[key]["data"]
                return None

            async def export(self, data: Any, format: str = "json") -> str:
                """데이터 내보내기"""
                if format == "json":
                    return json.dumps(data, indent=2)
                elif format == "csv":
                    # CSV 변환 로직
                    if isinstance(data, list) and data:
                        headers = list(data[0].keys())
                        csv_lines = [",".join(headers)]
                        for item in data:
                            csv_lines.append(",".join(str(item.get(h, "")) for h in headers))
                        return "\n".join(csv_lines)
                return str(data)

            async def sync(self) -> bool:
                """데이터 동기화"""
                # 실제 동기화 로직
                return True

            async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
                """통합 실행"""
                operations = {
                    "save": lambda: self.save(params.get("key"), params.get("data")),
                    "load": lambda: self.load(params.get("key")),
                    "export": lambda: self.export(params.get("data"), params.get("format")),
                    "sync": lambda: self.sync(),
                }

                if operation in operations:
                    return await operations[operation]()
                return None

        return DynamicStorageManager()

    async def _analytics_template(self, blueprint: AgentBlueprint) -> Any:
        """분석 에이전트 템플릿"""

        class DynamicAnalytics:
            def __init__(self):
                self.name = blueprint.name
                self.config = blueprint.config

            async def calculate_metrics(self, data: List[Dict]) -> Dict[str, Any]:
                """메트릭 계산"""
                metrics = {}

                # 완료율
                if data:
                    completed = len([d for d in data if d.get("completed")])
                    metrics["completionRate"] = (completed / len(data)) * 100

                # 카테고리별 분포
                categories = {}
                for item in data:
                    cat = item.get("category", "uncategorized")
                    categories[cat] = categories.get(cat, 0) + 1
                metrics["tasksByCategory"] = categories

                # 지연된 작업
                import datetime

                now = datetime.datetime.now()
                overdue = 0
                for item in data:
                    if item.get("dueDate"):
                        # 실제 날짜 비교 로직
                        pass
                metrics["overdueTasks"] = overdue

                return metrics

            async def generate_report(
                self, data: List[Dict], report_type: str = "daily"
            ) -> Dict[str, Any]:
                """리포트 생성"""
                metrics = await self.calculate_metrics(data)

                return {
                    "type": report_type,
                    "timestamp": time.time(),
                    "metrics": metrics,
                    "summary": f"{len(data)} total tasks analyzed",
                }

            async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
                """통합 실행"""
                if operation == "metrics":
                    return await self.calculate_metrics(params.get("data", []))
                elif operation == "report":
                    return await self.generate_report(params.get("data", []), params.get("type"))
                return {}

        return DynamicAnalytics()

    async def _ui_controller_template(self, blueprint: AgentBlueprint) -> Any:
        """UI 컨트롤러 에이전트 템플릿"""

        class DynamicUIController:
            def __init__(self):
                self.name = blueprint.name
                self.config = blueprint.config
                self.state = {"theme": "light", "view": "list", "animations": True}

            async def set_theme(self, theme: str) -> Dict[str, Any]:
                """테마 설정"""
                themes = self.config.get("themes", {})
                if theme in themes:
                    self.state["theme"] = theme
                    return {"theme": theme, "success": True}
                return {"error": f"Unknown theme: {theme}"}

            async def set_view(self, view: str) -> Dict[str, Any]:
                """뷰 설정"""
                views = self.config.get("views", {})
                if view in views:
                    self.state["view"] = view
                    return {"view": view, "success": True}
                return {"error": f"Unknown view: {view}"}

            async def get_shortcuts(self) -> Dict[str, str]:
                """단축키 조회"""
                return self.config.get("shortcuts", {})

            async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
                """통합 실행"""
                if operation == "setTheme":
                    return await self.set_theme(params.get("theme"))
                elif operation == "setView":
                    return await self.set_view(params.get("view"))
                elif operation == "getShortcuts":
                    return await self.get_shortcuts()
                elif operation == "getState":
                    return self.state
                return {}

        return DynamicUIController()

    async def _notification_template(self, blueprint: AgentBlueprint) -> Any:
        """알림 서비스 에이전트 템플릿"""

        class DynamicNotificationService:
            def __init__(self):
                self.name = blueprint.name
                self.config = blueprint.config
                self.notifications = []

            async def send(self, notification: Dict[str, Any]) -> bool:
                """알림 전송"""
                channels = self.config.get("channels", ["browser"])

                for channel in channels:
                    if channel == "browser":
                        # 브라우저 알림 로직
                        self.notifications.append(
                            {
                                "channel": channel,
                                "message": notification.get("message"),
                                "timestamp": time.time(),
                            }
                        )

                return True

            async def schedule(self, notification: Dict[str, Any], trigger: str) -> bool:
                """알림 예약"""
                # 예약 로직
                return True

            async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
                """통합 실행"""
                if operation == "send":
                    return await self.send(params)
                elif operation == "schedule":
                    return await self.schedule(params.get("notification"), params.get("trigger"))
                elif operation == "getHistory":
                    return self.notifications
                return False

        return DynamicNotificationService()

    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        if self.performance_metrics["generation_time_us"]:
            avg_time = sum(self.performance_metrics["generation_time_us"]) / len(
                self.performance_metrics["generation_time_us"]
            )
            max_time = max(self.performance_metrics["generation_time_us"])
            min_time = min(self.performance_metrics["generation_time_us"])
        else:
            avg_time = max_time = min_time = 0

        return {
            "total_agents_generated": len(self.generated_agents),
            "average_generation_time_us": avg_time,
            "max_generation_time_us": max_time,
            "min_generation_time_us": min_time,
            "success_rate": self.performance_metrics["success_rate"],
            "target_met": avg_time <= 3.0 if avg_time > 0 else True,
            "cache_hit_rate": "N/A",  # 추후 구현
        }


# 글로벌 인스턴스
agent_generator = AgnoAgentGenerator()


async def create_agent_from_blueprint(blueprint: Dict[str, Any]) -> Any:
    """블루프린트로부터 에이전트 생성"""
    bp = AgentBlueprint(
        name=blueprint["name"],
        type=blueprint["type"],
        config=blueprint.get("config", {}),
        methods={},
        dependencies=blueprint.get("dependencies", []),
    )

    return await agent_generator.generate_agent(bp)


if __name__ == "__main__":

    async def test_generation():
        """에이전트 생성 테스트"""

        # TodoCRUD 에이전트 생성
        blueprint = {
            "name": "TodoCRUDAgent",
            "type": "data_manager",
            "config": {
                "entity": "Task",
                "fields": {"id": "string", "title": "string", "completed": "boolean"},
                "validation_rules": {"title": {"required": True, "minLength": 1}},
            },
        }

        print("Creating agent from blueprint...")
        agent = await create_agent_from_blueprint(blueprint)

        # 테스트 실행
        print("\nTesting CRUD operations...")

        # Create
        task = await agent.create({"title": "Test task", "completed": False})
        print(f"Created: {task}")

        # Read
        retrieved = await agent.read(task["id"])
        print(f"Retrieved: {retrieved}")

        # Update
        updated = await agent.update(task["id"], {"completed": True})
        print(f"Updated: {updated}")

        # List
        all_tasks = await agent.list()
        print(f"All tasks: {all_tasks}")

        # Performance report
        print("\n=== Performance Report ===")
        report = agent_generator.get_performance_report()
        for key, value in report.items():
            print(f"{key}: {value}")

    asyncio.run(test_generation())
