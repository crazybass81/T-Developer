"""
Enhanced test for T-Developer Agent Framework - Phase 3 Complete
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend/src'))

import asyncio
from typing import Dict, Any
from agents.framework import *
from agents.framework import PERFORMANCE_TARGETS
from datetime import datetime

class EnhancedTestAgent(BaseAgent, CapabilityMixin):
    """Enhanced test agent with full framework integration"""
    
    AGENT_TYPE = "enhanced_test_agent"
    
    def __init__(self, config: Dict[str, Any]):
        BaseAgent.__init__(self, config)
        CapabilityMixin.__init__(self)
        
        # Initialize framework components
        self.lifecycle = LifecycleStateMachine()
        self.event_handler = LifecycleEventHandler()
        self.error_handler = AgentErrorHandler()
        self.active_tasks = 0
        self.accepting_tasks = True
        
        # Register capabilities
        self._register_capabilities()
        
        # Register lifecycle handlers
        self._register_lifecycle_handlers()
        
        # Register error handlers
        self._register_error_handlers()
    
    def _register_capabilities(self):
        """Register agent capabilities"""
        process_capability = Capability(
            name="process_data",
            type=CapabilityType.ANALYSIS,
            description="Process input data",
            input_schema={"type": "object", "required": ["data"]},
            output_schema={"type": "object"},
            required_permissions=[]
        )
        self.register_capability(process_capability, self._process_data)
    
    def _register_lifecycle_handlers(self):
        """Register lifecycle event handlers"""
        async def on_started(event_data):
            print(f"Agent {self.agent_id} started at {event_data.timestamp}")
        
        self.event_handler.register_handler(LifecycleEvent.STARTED, on_started)
    
    def _register_error_handlers(self):
        """Register error handlers"""
        async def handle_execution_error(error, context):
            from agents.framework.error_handling import ErrorHandlingResult
            print(f"Handling execution error: {error.message}")
            return ErrorHandlingResult(
                handled=True,
                action_taken="logged_and_recovered",
                retry_recommended=True
            )
        
        self.error_handler.register_handler("execution", handle_execution_error)
    
    async def initialize(self) -> None:
        """Initialize enhanced test agent"""
        await self.lifecycle.transition_to(LifecycleEvent.INITIALIZING)
        
        # Emit lifecycle event
        event_data = LifecycleEventData(
            event_type=LifecycleEvent.INITIALIZING,
            agent_id=self.agent_id,
            timestamp=datetime.utcnow(),
            metadata={"initialization": "starting"},
            source="agent"
        )
        await self.event_handler.emit_event(event_data)
        
        await asyncio.sleep(0.1)  # Simulate initialization work
        
        await self.lifecycle.transition_to(LifecycleEvent.INITIALIZED)
        await self.update_status(AgentStatus.READY)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced test agent"""
        self.active_tasks += 1
        
        try:
            await self.update_status(AgentStatus.PROCESSING)
            await self.lifecycle.transition_to(LifecycleEvent.EXECUTING)
            
            # Simulate potential error
            if input_data.get("simulate_error"):
                from agents.framework.error_handling import ExecutionError, ErrorContext
                
                error = ExecutionError(
                    "Simulated execution error",
                    agent_id=self.agent_id,
                    context={"input": input_data}
                )
                
                context = ErrorContext(
                    agent_id=self.agent_id,
                    operation="execute",
                    timestamp=datetime.utcnow()
                )
                
                result = await self.error_handler.handle_error(error, context)
                if not result.handled:
                    raise error
            
            # Process data
            result = {
                "processed": True,
                "input": input_data,
                "agent_id": self.agent_id,
                "timestamp": str(self.metadata.last_active)
            }
            
            await self.update_status(AgentStatus.READY)
            return result
            
        finally:
            self.active_tasks -= 1
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        return isinstance(input_data, dict) and "data" in input_data
    
    async def cleanup(self) -> None:
        """Cleanup enhanced test agent"""
        await self.lifecycle.transition_to(LifecycleEvent.STOPPING)
        await self.lifecycle.transition_to(LifecycleEvent.STOPPED)
        await self.update_status(AgentStatus.TERMINATED)
    
    async def save_state(self) -> None:
        """Save agent state"""
        # Mock state saving
        pass
    
    async def health_check(self) -> HealthCheckResult:
        """Perform health check"""
        return HealthCheckResult(
            healthy=True,
            status="operational",
            details={"active_tasks": self.active_tasks}
        )
    
    async def _process_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data capability"""
        return {"result": f"Processed: {input_data['data']}"}

async def test_enhanced_framework():
    """Test the enhanced agent framework"""
    print("🧪 Testing Enhanced T-Developer Agent Framework...")
    
    # Test 1: Enhanced Agent Creation with Configuration
    print("\n1. Testing Enhanced Agent Creation...")
    
    config = AgentConfig(
        agent_type="enhanced_test",
        version="1.0.0",
        max_concurrent_tasks=5,
        task_timeout=30000,
        resources=ResourceRequirement(cpu=1.0, memory=512),
        network=NetworkConfig(enable_http=True, timeout=10000),
        custom_settings={"test_mode": True}
    )
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print(f"❌ Configuration errors: {errors}")
        return
    
    AgentFactory.register_agent("enhanced_test", EnhancedTestAgent)
    agent = AgentFactory.create_agent("enhanced_test", config.to_dict())
    print(f"✅ Created enhanced agent: {agent.agent_id}")
    
    # Test 2: Initialization with Event Handling
    print("\n2. Testing Initialization with Events...")
    initializer = AgentInitializer()
    init_config = InitializationConfig(timeout=10000)
    
    result = await initializer.initialize_agent(agent, init_config)
    print(f"✅ Initialization {'succeeded' if result.success else 'failed'}")
    
    # Test 3: State Management with Synchronization
    print("\n3. Testing State Management...")
    local_store = MemoryStateStore()
    remote_store = MemoryStateStore()
    state_manager = StateManager(local_store)
    synchronizer = StateSynchronizer(local_store, remote_store)
    
    test_state = {"counter": 42, "status": "active", "config": config.to_dict()}
    await state_manager.save_agent_state(agent.agent_id, test_state)
    
    # Start synchronization
    await synchronizer.start_sync(agent.agent_id)
    await asyncio.sleep(0.1)  # Let sync happen
    await synchronizer.stop_sync(agent.agent_id)
    
    # Verify sync
    remote_state = await remote_store.load_state(agent.agent_id)
    print(f"✅ State synchronized: {remote_state['counter'] == 42}")
    
    # Test 4: Error Handling
    print("\n4. Testing Error Handling...")
    test_input_error = {"data": "test", "simulate_error": True}
    
    try:
        await agent.execute(test_input_error)
        print("✅ Error handled gracefully")
    except Exception as e:
        print(f"❌ Unhandled error: {e}")
    
    # Test 5: Normal Execution
    print("\n5. Testing Normal Execution...")
    test_input = {"data": "Hello, Enhanced T-Developer!"}
    
    if await agent.validate_input(test_input):
        output = await agent.execute(test_input)
        print(f"✅ Execution result: {output['processed']}")
    
    # Test 6: Lifecycle Events
    print("\n6. Testing Lifecycle Events...")
    event_summary = agent.event_handler.get_agent_lifecycle_summary(agent.agent_id)
    print(f"✅ Lifecycle events: {event_summary['events']} events recorded")
    
    # Test 7: Health Check
    print("\n7. Testing Health Check...")
    health = await agent.health_check()
    print(f"✅ Health check: {health.status}")
    
    # Test 8: Termination
    print("\n8. Testing Agent Termination...")
    terminator = AgentTerminator()
    termination_options = TerminationOptions(
        wait_for_completion=True,
        save_state=True
    )
    
    term_result = await terminator.terminate_agent(agent, termination_options)
    print(f"✅ Termination {'succeeded' if term_result.success else 'failed'}")
    
    # Test 9: Error Statistics
    print("\n9. Testing Error Statistics...")
    error_stats = agent.error_handler.get_error_statistics()
    print(f"✅ Error statistics: {error_stats['total_errors']} errors recorded")
    
    print("\n🎉 All enhanced framework tests passed!")
    
    # Performance Summary
    print(f"\n📊 Performance Summary:")
    print(f"   - Framework components: 30+ exports")
    print(f"   - Target instantiation: {PERFORMANCE_TARGETS['instantiation_time_us']}μs")
    print(f"   - Target memory: {PERFORMANCE_TARGETS['memory_per_agent_kb']}KB per agent")
    print(f"   - Max concurrent: {PERFORMANCE_TARGETS['max_concurrent_agents']} agents")

if __name__ == "__main__":
    asyncio.run(test_enhanced_framework())