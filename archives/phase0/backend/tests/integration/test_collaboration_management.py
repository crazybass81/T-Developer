#!/usr/bin/env python3
"""
Test suite for T-Developer Agent Framework Collaboration & Management (Tasks 3.11-3.20)
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from agents.framework.workflow_engine import WorkflowEngine, WorkflowStep, StepType, WorkflowStatus
from agents.framework.agent_chain import AgentChainManager, ChainType, ChainStep
from agents.framework.parallel_coordinator import ParallelCoordinator, ParallelTask
from agents.framework.dependency_manager import DependencyManager, Dependency, DependencyType
from agents.framework.collaboration_patterns import PatternLibrary, CollaborationPattern, PatternType
from agents.framework.agent_registry import AgentRegistry, AgentRegistration
from agents.framework.performance_monitor import PerformanceMonitor
from agents.framework.logging_tracing import AgentLogger, DistributedTracer, AgentLoggingMixin
from agents.framework.version_manager import VersionManager, AgentVersion
from agents.framework.deployment_scaling import AgentDeploymentManager, DeploymentTarget, ScalingConfig, ScalingPolicy

class TestWorkflowEngine:
    """Test workflow engine functionality"""
    
    async def test_workflow_creation(self):
        """Test workflow creation and step definition"""
        engine = WorkflowEngine()
        
        steps = [
            WorkflowStep(
                id="step1",
                name="Initialize",
                type=StepType.SEQUENTIAL,
                agent_id="agent1",
                action="initialize",
                inputs={"data": "test"}
            ),
            WorkflowStep(
                id="step2",
                name="Process",
                type=StepType.SEQUENTIAL,
                agent_id="agent2",
                action="process",
                inputs={"data": "processed"},
                dependencies=["step1"]
            )
        ]
        
        workflow_id = await engine.create_workflow("test_workflow", steps)
        assert workflow_id is not None
        assert workflow_id in engine.workflows
        print("✅ Workflow creation")
    
    async def test_workflow_execution(self):
        """Test workflow execution with handlers"""
        engine = WorkflowEngine()
        
        # Register handlers
        async def mock_handler(inputs, context):
            return {"result": f"processed_{inputs.get('data', 'none')}"}
        
        engine.register_step_handler("test_action", mock_handler)
        
        steps = [
            WorkflowStep(
                id="step1",
                name="Test Step",
                type=StepType.SEQUENTIAL,
                agent_id="agent1",
                action="test_action",
                inputs={"data": "input"}
            )
        ]
        
        workflow_id = await engine.create_workflow("test", steps)
        results = await engine.execute_workflow(workflow_id)
        
        assert "step1" in results
        assert results["step1"]["result"] == "processed_input"
        print("✅ Workflow execution")

class TestAgentChain:
    """Test agent chain management"""
    
    async def test_sequential_chain(self):
        """Test sequential agent chain execution"""
        manager = AgentChainManager()
        
        # Register mock handlers
        async def handler1(action, inputs):
            return {"step1_result": inputs.get("data", "") + "_processed1"}
        
        async def handler2(action, inputs):
            return {"step2_result": inputs.get("step1_result", "") + "_processed2"}
        
        manager.register_agent_handler("agent1", handler1)
        manager.register_agent_handler("agent2", handler2)
        
        steps = [
            ChainStep(agent_id="agent1", action="process", inputs={}),
            ChainStep(agent_id="agent2", action="process", inputs={})
        ]
        
        chain_id = manager.create_chain("test_chain", ChainType.SEQUENTIAL, steps)
        results = await manager.execute_chain(chain_id, {"data": "initial"})
        
        assert "agent1" in results
        assert "agent2" in results
        assert "processed2" in str(results["agent2"])
        print("✅ Sequential agent chain")
    
    async def test_parallel_chain(self):
        """Test parallel agent chain execution"""
        manager = AgentChainManager()
        
        async def handler(action, inputs):
            await asyncio.sleep(0.1)  # Simulate work
            return {"result": f"processed_{inputs.get('id', 'unknown')}"}
        
        manager.register_agent_handler("agent1", handler)
        manager.register_agent_handler("agent2", handler)
        
        steps = [
            ChainStep(agent_id="agent1", action="process", inputs={"id": "1"}),
            ChainStep(agent_id="agent2", action="process", inputs={"id": "2"})
        ]
        
        chain_id = manager.create_chain("parallel_chain", ChainType.PARALLEL, steps)
        results = await manager.execute_chain(chain_id, {})
        
        assert len(results) == 2
        assert "agent1" in results and "agent2" in results
        print("✅ Parallel agent chain")

class TestParallelCoordinator:
    """Test parallel task coordination"""
    
    async def test_parallel_execution(self):
        """Test parallel task execution"""
        coordinator = ParallelCoordinator(max_workers=5)
        
        async def mock_handler(action, inputs):
            await asyncio.sleep(0.1)
            return {"processed": inputs.get("data", "none")}
        
        coordinator.register_task_handler("test_agent", mock_handler)
        
        tasks = [
            ParallelTask(
                id=f"task_{i}",
                agent_id="test_agent",
                action="process",
                inputs={"data": f"data_{i}"},
                priority=i
            )
            for i in range(3)
        ]
        
        results = await coordinator.execute_parallel_tasks(tasks)
        
        assert len(results) == 3
        assert all(r.success for r in results.values())
        print("✅ Parallel task execution")
    
    async def test_dependency_resolution(self):
        """Test task dependency resolution"""
        coordinator = ParallelCoordinator()
        
        async def handler(action, inputs):
            return {"result": f"processed_{inputs.get('data', 'none')}"}
        
        coordinator.register_task_handler("agent", handler)
        
        tasks = [
            ParallelTask(id="task1", agent_id="agent", action="process", inputs={"data": "1"}),
            ParallelTask(id="task2", agent_id="agent", action="process", inputs={"data": "2"}, dependencies={"task1"}),
            ParallelTask(id="task3", agent_id="agent", action="process", inputs={"data": "3"}, dependencies={"task2"})
        ]
        
        results = await coordinator.execute_parallel_tasks(tasks)
        
        assert len(results) == 3
        assert all(r.success for r in results.values())
        print("✅ Task dependency resolution")

class TestDependencyManager:
    """Test dependency management"""
    
    def test_dependency_graph(self):
        """Test dependency graph creation"""
        manager = DependencyManager()
        
        # Add dependencies
        manager.add_dependency(Dependency("agent1", "agent2", DependencyType.HARD))
        manager.add_dependency(Dependency("agent2", "agent3", DependencyType.SOFT))
        
        # Test dependency queries
        deps = manager.get_dependencies("agent2")
        assert "agent1" in deps
        
        dependents = manager.get_dependents("agent2")
        assert "agent3" in dependents
        
        print("✅ Dependency graph management")
    
    def test_execution_order(self):
        """Test execution order calculation"""
        manager = DependencyManager()
        
        manager.add_dependency(Dependency("A", "B", DependencyType.HARD))
        manager.add_dependency(Dependency("B", "C", DependencyType.HARD))
        manager.add_dependency(Dependency("A", "D", DependencyType.HARD))
        
        order = manager.get_execution_order(["A", "B", "C", "D"])
        
        # A should be first, C should be last
        assert order[0] == ["A"]
        assert "C" in order[-1]
        print("✅ Execution order calculation")

class TestCollaborationPatterns:
    """Test collaboration patterns"""
    
    async def test_pipeline_pattern(self):
        """Test pipeline collaboration pattern"""
        library = PatternLibrary()
        
        async def handler(action, data):
            return {"value": data.get("value", 0) + 1}
        
        library.register_agent_handler("agent1", handler)
        library.register_agent_handler("agent2", handler)
        library.register_agent_handler("agent3", handler)
        
        pattern = CollaborationPattern(
            name="test_pipeline",
            type=PatternType.PIPELINE,
            participants=["agent1", "agent2", "agent3"]
        )
        
        library.register_pattern(pattern)
        
        result = await library.execute_pattern("test_pipeline", {"value": 0})
        
        assert result["final_result"]["value"] == 3
        print("✅ Pipeline collaboration pattern")
    
    async def test_scatter_gather_pattern(self):
        """Test scatter-gather pattern"""
        library = PatternLibrary()
        
        async def handler(action, data):
            agent_id = getattr(handler, 'agent_id', 'unknown')
            return {"processed_by": agent_id, "data": data}
        
        # Create different handlers for each agent
        for i, agent_id in enumerate(["agent1", "agent2", "agent3"]):
            async def make_handler(aid):
                async def h(action, data):
                    return {"processed_by": aid, "value": data.get("value", 0) * 2}
                return h
            library.register_agent_handler(agent_id, await make_handler(agent_id))
        
        pattern = CollaborationPattern(
            name="scatter_gather",
            type=PatternType.SCATTER_GATHER,
            participants=["agent1", "agent2", "agent3"]
        )
        
        library.register_pattern(pattern)
        
        result = await library.execute_pattern("scatter_gather", {"value": 5})
        
        assert len(result) == 3
        assert all("processed_by" in r for r in result.values())
        print("✅ Scatter-gather pattern")

class TestAgentRegistry:
    """Test agent registry system"""
    
    def test_agent_registration(self):
        """Test agent registration and lookup"""
        registry = AgentRegistry()
        
        registration = AgentRegistration(
            agent_id="test_agent",
            agent_type="test_type",
            version="1.0.0",
            capabilities=["test_capability"],
            status="active",
            tags={"environment", "test"}
        )
        
        success = registry.register_agent(registration)
        assert success
        
        # Test lookup
        found = registry.get_agent_info("test_agent")
        assert found is not None
        assert found.agent_type == "test_type"
        
        print("✅ Agent registration")
    
    def test_agent_search(self):
        """Test agent search functionality"""
        registry = AgentRegistry()
        
        # Register multiple agents
        for i in range(3):
            registration = AgentRegistration(
                agent_id=f"agent_{i}",
                agent_type="worker",
                version="1.0.0",
                capabilities=["process", "analyze"],
                status="active"
            )
            registry.register_agent(registration)
        
        # Search by type
        workers = registry.find_agents_by_type("worker")
        assert len(workers) == 3
        
        # Search by capability
        processors = registry.find_agents_by_capability("process")
        assert len(processors) == 3
        
        print("✅ Agent search functionality")

class TestPerformanceMonitor:
    """Test performance monitoring"""
    
    def test_execution_tracking(self):
        """Test execution time tracking"""
        monitor = PerformanceMonitor()
        
        # Simulate execution
        monitor.start_execution("test_agent", "exec_1")
        import time
        time.sleep(0.1)
        monitor.end_execution("test_agent", "exec_1", success=True)
        
        stats = monitor.get_agent_stats("test_agent")
        assert stats is not None
        assert stats.total_executions == 1
        assert stats.successful_executions == 1
        assert stats.avg_execution_time > 0
        
        print("✅ Execution tracking")
    
    def test_performance_alerts(self):
        """Test performance alert generation"""
        monitor = PerformanceMonitor()
        
        # Simulate high error rate
        for i in range(10):
            monitor.start_execution("failing_agent", f"exec_{i}")
            monitor.end_execution("failing_agent", f"exec_{i}", success=i < 5)
        
        alerts = monitor.get_performance_alerts()
        
        # Should have high error rate alert
        error_alerts = [a for a in alerts if a["type"] == "high_error_rate"]
        assert len(error_alerts) > 0
        
        print("✅ Performance alerts")

class TestLoggingTracing:
    """Test logging and tracing"""
    
    def test_agent_logger(self):
        """Test agent logging functionality"""
        logger = AgentLogger("test_agent")
        
        logger.set_context(session_id="test_session", user_id="test_user")
        logger.info("Test message", extra_data="test")
        
        context = logger.get_context()
        assert "session_id" in context
        assert context["session_id"] == "test_session"
        
        print("✅ Agent logging")
    
    async def test_distributed_tracing(self):
        """Test distributed tracing"""
        tracer = DistributedTracer()
        
        # Test trace context manager
        with tracer.trace("test_operation", component="test") as span_id:
            tracer.add_log(span_id, "Processing started")
            await asyncio.sleep(0.01)
            tracer.add_log(span_id, "Processing completed")
        
        span = tracer.spans.get(span_id)
        assert span is not None
        assert span.status == "ok"
        assert len(span.logs) == 2
        
        print("✅ Distributed tracing")

class TestVersionManager:
    """Test version management"""
    
    def test_version_creation(self):
        """Test version creation and management"""
        manager = VersionManager()
        
        version = manager.create_version(
            agent_id="test_agent",
            version="1.0.0",
            code="def test(): pass",
            config={"param": "value"},
            changelog="Initial version"
        )
        
        assert version.agent_id == "test_agent"
        assert version.version == "1.0.0"
        assert len(version.code_hash) == 64  # SHA256 hash
        
        print("✅ Version creation")
    
    def test_version_activation(self):
        """Test version activation"""
        manager = VersionManager()
        
        # Create versions
        manager.create_version("agent", "1.0.0", "code1", {})
        manager.create_version("agent", "1.1.0", "code2", {})
        
        # Set active version
        success = manager.set_active_version("agent", "1.1.0")
        assert success
        
        active = manager.get_active_version("agent")
        assert active is not None
        assert active.version == "1.1.0"
        
        print("✅ Version activation")

class TestDeploymentScaling:
    """Test deployment and scaling"""
    
    async def test_agent_deployment(self):
        """Test agent deployment"""
        manager = AgentDeploymentManager()
        
        target = DeploymentTarget(
            target_id="local_target",
            target_type="local",
            endpoint="localhost",
            credentials={},
            config={}
        )
        
        manager.register_deployment_target(target)
        
        success = await manager.deploy_agent(
            agent_id="test_agent",
            version="1.0.0",
            target_id="local_target",
            instances=1
        )
        
        assert success
        
        status = manager.get_deployment_status("test_agent", "local_target")
        assert status is not None
        assert status["status"] == "deployed"
        
        print("✅ Agent deployment")
    
    def test_scaling_configuration(self):
        """Test auto-scaling configuration"""
        manager = AgentDeploymentManager()
        
        config = ScalingConfig(
            min_instances=1,
            max_instances=5,
            target_cpu_percent=70.0
        )
        
        manager.configure_auto_scaling(
            "test_agent",
            "local_target",
            ScalingPolicy.CPU_BASED,
            config
        )
        
        key = "test_agent:local_target"
        assert key in manager.scaling_configs
        assert manager.scaling_configs[key].max_instances == 5
        
        print("✅ Scaling configuration")

async def run_all_tests():
    """Run all collaboration and management tests"""
    print("🧪 Testing T-Developer Agent Framework Collaboration & Management")
    print("=" * 70)
    
    # Test workflow engine
    workflow_test = TestWorkflowEngine()
    await workflow_test.test_workflow_creation()
    await workflow_test.test_workflow_execution()
    
    # Test agent chains
    chain_test = TestAgentChain()
    await chain_test.test_sequential_chain()
    await chain_test.test_parallel_chain()
    
    # Test parallel coordination
    parallel_test = TestParallelCoordinator()
    await parallel_test.test_parallel_execution()
    await parallel_test.test_dependency_resolution()
    
    # Test dependency management
    dep_test = TestDependencyManager()
    dep_test.test_dependency_graph()
    dep_test.test_execution_order()
    
    # Test collaboration patterns
    pattern_test = TestCollaborationPatterns()
    await pattern_test.test_pipeline_pattern()
    await pattern_test.test_scatter_gather_pattern()
    
    # Test agent registry
    registry_test = TestAgentRegistry()
    registry_test.test_agent_registration()
    registry_test.test_agent_search()
    
    # Test performance monitoring
    perf_test = TestPerformanceMonitor()
    perf_test.test_execution_tracking()
    perf_test.test_performance_alerts()
    
    # Test logging and tracing
    log_test = TestLoggingTracing()
    log_test.test_agent_logger()
    await log_test.test_distributed_tracing()
    
    # Test version management
    version_test = TestVersionManager()
    version_test.test_version_creation()
    version_test.test_version_activation()
    
    # Test deployment and scaling
    deploy_test = TestDeploymentScaling()
    await deploy_test.test_agent_deployment()
    deploy_test.test_scaling_configuration()
    
    print("=" * 70)
    print("✅ All collaboration and management tests passed!")
    print(f"📊 Framework Status:")
    print(f"   - Workflow Engine: ✅ Ready")
    print(f"   - Agent Chains: ✅ Ready")
    print(f"   - Parallel Coordination: ✅ Ready")
    print(f"   - Dependency Management: ✅ Ready")
    print(f"   - Collaboration Patterns: ✅ Ready")
    print(f"   - Agent Registry: ✅ Ready")
    print(f"   - Performance Monitoring: ✅ Ready")
    print(f"   - Logging & Tracing: ✅ Ready")
    print(f"   - Version Management: ✅ Ready")
    print(f"   - Deployment & Scaling: ✅ Ready")

if __name__ == "__main__":
    asyncio.run(run_all_tests())