"""
Agno Framework Integration
고성능 에이전트 프레임워크 통합
"""

import os
import time
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor

# Agno Framework 컴포넌트
from agno.agent import Agent, AgentConfig
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory, VectorMemory
from agno.tools import Tool, ToolResult
from agno.performance import PerformanceMonitor
from agno.cache import AgentCache

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics

logger = Logger()
tracer = Tracer()
metrics = Metrics()

# AWS 클라이언트
bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')


@dataclass
class AgnoConfig:
    """Agno Framework 설정"""
    instantiation_time_target: float = 0.000003  # 3μs
    memory_footprint_target: int = 6500  # 6.5KB
    enable_caching: bool = True
    enable_vector_memory: bool = True
    enable_performance_monitoring: bool = True
    max_concurrent_agents: int = 100
    cache_ttl: int = 3600


class AgnoToolAdapter(Tool):
    """기존 함수를 Agno Tool로 변환하는 어댑터"""
    
    def __init__(self, name: str, description: str, func: Callable):
        super().__init__(name=name, description=description)
        self.func = func
    
    async def run(self, *args, **kwargs) -> ToolResult:
        """도구 실행"""
        try:
            result = await self.func(*args, **kwargs)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class HighPerformanceAgent(Agent):
    """고성능 Agno 에이전트"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.performance_monitor = PerformanceMonitor()
        self.cache = AgentCache(ttl=3600)
        self.instantiation_time = None
        self.memory_footprint = None
        
        # 성능 측정
        self._measure_performance()
    
    def _measure_performance(self):
        """성능 측정"""
        import sys
        import psutil
        import gc
        
        # 인스턴스화 시간 측정
        start_time = time.perf_counter()
        _ = Agent(self.config)
        self.instantiation_time = time.perf_counter() - start_time
        
        # 메모리 사용량 측정
        gc.collect()
        process = psutil.Process()
        self.memory_footprint = process.memory_info().rss
        
        logger.info(f"Agent instantiation time: {self.instantiation_time*1000000:.2f}μs")
        logger.info(f"Agent memory footprint: {self.memory_footprint/1024:.2f}KB")
    
    async def execute_with_cache(self, prompt: str) -> Any:
        """캐시를 사용한 실행"""
        # 캐시 키 생성
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        
        # 캐시 확인
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Cache hit")
            return cached_result
        
        # 실행
        result = await self.arun(prompt)
        
        # 캐시 저장
        self.cache.set(cache_key, result)
        
        return result


class AgnoIntegrationManager:
    """Agno Framework 통합 관리자"""
    
    def __init__(self, agno_config: Optional[AgnoConfig] = None):
        self.config = agno_config or AgnoConfig()
        self.agents = {}
        self.tools = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._init_shared_resources()
    
    def _init_shared_resources(self):
        """공유 리소스 초기화"""
        # 공유 메모리
        self.shared_memory = VectorMemory(
            dimension=1536,
            index_type="HNSW",
            metric="cosine"
        )
        
        # 공유 캐시
        self.shared_cache = AgentCache(
            ttl=self.config.cache_ttl,
            max_size=1000
        )
        
        # 성능 모니터
        self.performance_monitor = PerformanceMonitor()
    
    def create_optimized_agent(
        self,
        name: str,
        role: str,
        instructions: List[str],
        tools: Optional[List[Tool]] = None
    ) -> HighPerformanceAgent:
        """최적화된 에이전트 생성"""
        
        config = AgentConfig(
            name=name,
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role=role,
            instructions=instructions,
            memory=self.shared_memory if self.config.enable_vector_memory else None,
            tools=tools or [],
            temperature=0.2,
            max_retries=3,
            enable_streaming=True
        )
        
        agent = HighPerformanceAgent(config)
        
        # 성능 목표 확인
        if agent.instantiation_time > self.config.instantiation_time_target:
            logger.warning(
                f"Agent {name} instantiation time ({agent.instantiation_time*1000000:.2f}μs) "
                f"exceeds target ({self.config.instantiation_time_target*1000000:.2f}μs)"
            )
        
        if agent.memory_footprint > self.config.memory_footprint_target:
            logger.warning(
                f"Agent {name} memory footprint ({agent.memory_footprint/1024:.2f}KB) "
                f"exceeds target ({self.config.memory_footprint_target/1024:.2f}KB)"
            )
        
        self.agents[name] = agent
        return agent
    
    def register_tool(self, name: str, description: str, func: Callable) -> Tool:
        """도구 등록"""
        tool = AgnoToolAdapter(name, description, func)
        self.tools[name] = tool
        return tool
    
    async def execute_agent_pipeline(
        self,
        agents: List[str],
        initial_input: Any,
        parallel: bool = False
    ) -> Any:
        """에이전트 파이프라인 실행"""
        
        if parallel:
            return await self._execute_parallel(agents, initial_input)
        else:
            return await self._execute_sequential(agents, initial_input)
    
    async def _execute_sequential(
        self,
        agents: List[str],
        initial_input: Any
    ) -> Any:
        """순차 실행"""
        result = initial_input
        
        for agent_name in agents:
            agent = self.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            with self.performance_monitor.measure(agent_name):
                if self.config.enable_caching:
                    result = await agent.execute_with_cache(str(result))
                else:
                    result = await agent.arun(str(result))
        
        return result
    
    async def _execute_parallel(
        self,
        agents: List[str],
        initial_input: Any
    ) -> List[Any]:
        """병렬 실행"""
        tasks = []
        
        for agent_name in agents:
            agent = self.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            task = asyncio.create_task(
                self._execute_with_monitoring(agent, agent_name, initial_input)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def _execute_with_monitoring(
        self,
        agent: HighPerformanceAgent,
        agent_name: str,
        input_data: Any
    ) -> Any:
        """모니터링과 함께 실행"""
        with self.performance_monitor.measure(agent_name):
            if self.config.enable_caching:
                return await agent.execute_with_cache(str(input_data))
            else:
                return await agent.arun(str(input_data))
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        metrics = self.performance_monitor.get_metrics()
        
        # 에이전트별 메트릭
        agent_metrics = {}
        for name, agent in self.agents.items():
            agent_metrics[name] = {
                'instantiation_time_us': agent.instantiation_time * 1000000,
                'memory_footprint_kb': agent.memory_footprint / 1024,
                'cache_hit_rate': self.shared_cache.get_hit_rate()
            }
        
        return {
            'global_metrics': metrics,
            'agent_metrics': agent_metrics,
            'cache_stats': self.shared_cache.get_stats()
        }


class AgnoSquadIntegration:
    """T-Developer Squad와 Agno Framework 통합"""
    
    def __init__(self):
        self.manager = AgnoIntegrationManager()
        self._setup_agents()
        self._setup_tools()
    
    def _setup_agents(self):
        """T-Developer 에이전트를 Agno로 설정"""
        
        # NL Input Agent
        self.manager.create_optimized_agent(
            name="NL-Input-Processor",
            role="Senior requirements analyst",
            instructions=[
                "Extract project requirements from natural language",
                "Identify technical and business constraints",
                "Generate clarification questions when needed"
            ]
        )
        
        # UI Selection Agent
        self.manager.create_optimized_agent(
            name="UI-Framework-Selector",
            role="Frontend architecture expert",
            instructions=[
                "Select optimal UI framework based on requirements",
                "Consider performance and scalability",
                "Evaluate team expertise and learning curve"
            ]
        )
        
        # Parser Agent
        self.manager.create_optimized_agent(
            name="Requirements-Parser",
            role="System architect and analyst",
            instructions=[
                "Parse and structure requirements",
                "Create user stories and use cases",
                "Define data models and API specifications"
            ]
        )
        
        # Component Decision Agent
        self.manager.create_optimized_agent(
            name="Component-Decision-Maker",
            role="Software architect",
            instructions=[
                "Select optimal components and libraries",
                "Evaluate alternatives using MCDM",
                "Consider compatibility and performance"
            ]
        )
        
        # Match Rate Agent
        self.manager.create_optimized_agent(
            name="Match-Rate-Calculator",
            role="Component matching expert",
            instructions=[
                "Calculate matching rates between requirements and components",
                "Identify reusable templates",
                "Optimize component selection"
            ]
        )
        
        # Search Agent
        self.manager.create_optimized_agent(
            name="Component-Search-Expert",
            role="Component discovery specialist",
            instructions=[
                "Search components from multiple sources",
                "Apply intelligent filtering and ranking",
                "Analyze quality and compatibility"
            ]
        )
        
        # Generation Agent
        self.manager.create_optimized_agent(
            name="Code-Generation-Expert",
            role="Senior software engineer",
            instructions=[
                "Generate production-ready code",
                "Apply best practices and patterns",
                "Create tests and documentation"
            ]
        )
        
        # Assembly Agent
        self.manager.create_optimized_agent(
            name="Project-Assembly-Expert",
            role="DevOps and build engineer",
            instructions=[
                "Assemble project components",
                "Configure build systems",
                "Create deployment packages"
            ]
        )
        
        # Download Agent
        self.manager.create_optimized_agent(
            name="Download-Delivery-Expert",
            role="Package and delivery specialist",
            instructions=[
                "Create optimized download packages",
                "Generate secure download links",
                "Prepare deployment instructions"
            ]
        )
    
    def _setup_tools(self):
        """공통 도구 설정"""
        
        # 코드 생성 도구
        async def generate_code(spec: Dict[str, Any]) -> str:
            """코드 생성"""
            # 실제 코드 생성 로직
            return f"// Generated code for {spec.get('name', 'component')}"
        
        self.manager.register_tool(
            name="code_generator",
            description="Generate code from specifications",
            func=generate_code
        )
        
        # 검색 도구
        async def search_components(query: str) -> List[Dict]:
            """컴포넌트 검색"""
            # 실제 검색 로직
            return [{"name": "component1", "score": 0.9}]
        
        self.manager.register_tool(
            name="component_searcher",
            description="Search for components",
            func=search_components
        )
        
        # 패키지 생성 도구
        async def create_package(files: List[str]) -> str:
            """패키지 생성"""
            # 실제 패키지 생성 로직
            return "package_id_123"
        
        self.manager.register_tool(
            name="package_creator",
            description="Create download packages",
            func=create_package
        )
    
    async def execute_optimized_pipeline(
        self,
        user_input: str
    ) -> Dict[str, Any]:
        """최적화된 파이프라인 실행"""
        
        start_time = time.perf_counter()
        
        # 순차 실행 (의존성이 있는 단계)
        agents_sequence = [
            "NL-Input-Processor",
            "UI-Framework-Selector",
            "Requirements-Parser"
        ]
        
        parsing_result = await self.manager.execute_agent_pipeline(
            agents_sequence,
            user_input,
            parallel=False
        )
        
        # 병렬 실행 (독립적인 단계)
        parallel_agents = [
            "Component-Decision-Maker",
            "Match-Rate-Calculator",
            "Component-Search-Expert"
        ]
        
        parallel_results = await self.manager.execute_agent_pipeline(
            parallel_agents,
            parsing_result,
            parallel=True
        )
        
        # 최종 단계
        final_agents = [
            "Code-Generation-Expert",
            "Project-Assembly-Expert",
            "Download-Delivery-Expert"
        ]
        
        final_result = await self.manager.execute_agent_pipeline(
            final_agents,
            parallel_results,
            parallel=False
        )
        
        execution_time = time.perf_counter() - start_time
        
        # 성능 메트릭
        performance_metrics = self.manager.get_performance_metrics()
        
        return {
            'result': final_result,
            'execution_time': execution_time,
            'performance_metrics': performance_metrics
        }


# 글로벌 인스턴스
agno_squad = AgnoSquadIntegration()


async def benchmark_agno_performance():
    """Agno 성능 벤치마크"""
    
    print("=== Agno Framework Performance Benchmark ===\n")
    
    # 단일 에이전트 인스턴스화 시간
    start = time.perf_counter()
    agent = agno_squad.manager.create_optimized_agent(
        name="benchmark-agent",
        role="test",
        instructions=["test"]
    )
    instantiation_time = time.perf_counter() - start
    
    print(f"Agent Instantiation Time: {instantiation_time*1000000:.2f}μs")
    print(f"Target: 3μs")
    print(f"Status: {'✅ PASS' if instantiation_time <= 0.000003 else '❌ FAIL'}\n")
    
    # 메모리 사용량
    import psutil
    process = psutil.Process()
    memory_kb = process.memory_info().rss / 1024
    
    print(f"Memory Footprint: {memory_kb:.2f}KB")
    print(f"Target: 6.5KB per agent")
    print(f"Status: {'✅ PASS' if memory_kb <= 6500 else '❌ FAIL'}\n")
    
    # 동시 실행 테스트
    print("Concurrent Execution Test:")
    concurrent_tasks = []
    for i in range(10):
        task = agent.arun(f"Test prompt {i}")
        concurrent_tasks.append(task)
    
    start = time.perf_counter()
    await asyncio.gather(*concurrent_tasks)
    concurrent_time = time.perf_counter() - start
    
    print(f"10 concurrent executions: {concurrent_time:.3f}s")
    print(f"Average per execution: {concurrent_time/10:.3f}s\n")
    
    # 캐시 효율성
    print("Cache Performance:")
    cache_test_prompt = "Test cache prompt"
    
    # 첫 실행 (캐시 미스)
    start = time.perf_counter()
    await agent.execute_with_cache(cache_test_prompt)
    miss_time = time.perf_counter() - start
    
    # 두 번째 실행 (캐시 히트)
    start = time.perf_counter()
    await agent.execute_with_cache(cache_test_prompt)
    hit_time = time.perf_counter() - start
    
    print(f"Cache miss time: {miss_time:.3f}s")
    print(f"Cache hit time: {hit_time:.3f}s")
    print(f"Speed improvement: {miss_time/hit_time:.1f}x\n")
    
    # 전체 파이프라인 테스트
    print("Full Pipeline Performance:")
    test_input = "Create a simple e-commerce website with React"
    
    start = time.perf_counter()
    result = await agno_squad.execute_optimized_pipeline(test_input)
    pipeline_time = result['execution_time']
    
    print(f"Total pipeline execution: {pipeline_time:.3f}s")
    print(f"Performance metrics: {json.dumps(result['performance_metrics'], indent=2)}")


if __name__ == "__main__":
    # 벤치마크 실행
    asyncio.run(benchmark_agno_performance())