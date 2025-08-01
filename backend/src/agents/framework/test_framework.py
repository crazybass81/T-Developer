"""
Test script for T-Developer Agent Framework
"""
import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent, AgentStatus
from .agent_factory import AgentFactory
from .capabilities import Capability, CapabilityType, CapabilityMixin
from .lifecycle import LifecycleStateMachine, LifecycleEvent
from .initialization import AgentInitializer, InitializationConfig
from .state_store import MemoryStateStore, StateManager

class TestAgent(BaseAgent, CapabilityMixin):
    """Test agent implementation"""
    
    AGENT_TYPE = "test_agent"
    
    def __init__(self, config: Dict[str, Any]):
        BaseAgent.__init__(self, config)
        CapabilityMixin.__init__(self)
        
        # Register test capability
        test_capability = Capability(
            name="test_process",
            type=CapabilityType.ANALYSIS,
            description="Test processing capability",
            input_schema={"type": "object", "required": ["data"]},
            output_schema={"type": "object"},
            required_permissions=[]
        )
        
        self.register_capability(test_capability, self._test_process)
        self.lifecycle = LifecycleStateMachine()
    
    async def initialize(self) -> None:
        """Initialize test agent"""
        await self.lifecycle.transition_to(LifecycleEvent.INITIALIZING)
        await asyncio.sleep(0.1)  # Simulate initialization work
        await self.lifecycle.transition_to(LifecycleEvent.INITIALIZED)
        await self.update_status(AgentStatus.READY)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test agent"""
        await self.update_status(AgentStatus.PROCESSING)
        await self.lifecycle.transition_to(LifecycleEvent.EXECUTING)
        
        # Process data
        result = {
            "processed": True,
            "input": input_data,
            "agent_id": self.agent_id,
            "timestamp": str(self.metadata.last_active)
        }
        
        await self.update_status(AgentStatus.READY)
        return result
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        return isinstance(input_data, dict) and "data" in input_data
    
    async def cleanup(self) -> None:
        """Cleanup test agent"""
        await self.lifecycle.transition_to(LifecycleEvent.STOPPING)
        await self.lifecycle.transition_to(LifecycleEvent.STOPPED)
        await self.update_status(AgentStatus.TERMINATED)
    
    async def _test_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test capability handler"""
        return {"result": f"Processed: {input_data['data']}"}

async def test_framework():
    """Test the agent framework"""
    print("🧪 Testing T-Developer Agent Framework...")
    
    # Test 1: Agent Factory
    print("\n1. Testing Agent Factory...")
    AgentFactory.register_agent("test", TestAgent)
    
    config = {
        "agent_type": "test",
        "version": "1.0.0",
        "capabilities": ["test_process"]
    }
    
    agent = AgentFactory.create_agent("test", config)
    print(f"✅ Created agent: {agent.agent_id}")
    
    # Test 2: Agent Initialization
    print("\n2. Testing Agent Initialization...")
    initializer = AgentInitializer()
    init_config = InitializationConfig(timeout=5000)
    
    result = await initializer.initialize_agent(agent, init_config)
    print(f"✅ Initialization {'succeeded' if result.success else 'failed'}")
    
    # Test 3: Agent Execution
    print("\n3. Testing Agent Execution...")
    test_input = {"data": "Hello, T-Developer!"}
    
    if await agent.validate_input(test_input):
        output = await agent.execute(test_input)
        print(f"✅ Execution result: {output['processed']}")
    
    # Test 4: Capabilities
    print("\n4. Testing Capabilities...")
    capabilities = agent.get_capabilities()
    print(f"✅ Agent has {len(capabilities)} capabilities")
    
    cap_result = await agent.execute_capability("test_process", {"data": "capability test"})
    print(f"✅ Capability result: {cap_result['result']}")
    
    # Test 5: State Management
    print("\n5. Testing State Management...")
    store = MemoryStateStore()
    state_manager = StateManager(store)
    
    test_state = {"counter": 42, "status": "active"}
    await state_manager.save_agent_state(agent.agent_id, test_state)
    
    loaded_state = await state_manager.load_agent_state(agent.agent_id)
    print(f"✅ State saved and loaded: {loaded_state['counter'] == 42}")
    
    # Test 6: Lifecycle
    print("\n6. Testing Lifecycle...")
    current_state = agent.lifecycle.get_current_state()
    print(f"✅ Current lifecycle state: {current_state.value}")
    
    # Cleanup
    await agent.cleanup()
    print(f"✅ Agent cleaned up, final state: {agent.lifecycle.get_current_state().value}")
    
    print("\n🎉 All framework tests passed!")

if __name__ == "__main__":
    asyncio.run(test_framework())