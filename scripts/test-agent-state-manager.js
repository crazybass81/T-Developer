#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

async function testAgentStateManager() {
  console.log('💾 Testing Agent State Manager...\n');

  const testScript = `
import asyncio
import sys
import os
from datetime import datetime
sys.path.append('${path.join(__dirname, '../backend/src')}')

from memory.agent_state_manager import AgentStateManager, AgentState

async def test_state_manager():
    manager = AgentStateManager()
    
    # Create test state
    test_state = AgentState(
        agent_id='test-agent-001',
        session_id='session-123',
        context={'current_task': 'code_generation', 'user_id': 'user-456'},
        memory={'learned_patterns': ['pattern1', 'pattern2'], 'cache': {}},
        last_activity=datetime.utcnow(),
        checkpoints=[]
    )
    
    # Test save state
    await manager.save_state(test_state)
    print("✅ State saved successfully")
    
    # Test load state
    loaded_state = await manager.load_state('test-agent-001', 'session-123')
    assert loaded_state is not None, "Failed to load state"
    assert loaded_state.agent_id == 'test-agent-001', "Agent ID mismatch"
    assert loaded_state.context['current_task'] == 'code_generation', "Context mismatch"
    print("✅ State loaded successfully")
    
    # Test checkpoint creation (simulate time passage)
    import time
    time.sleep(1)  # Small delay to ensure different timestamp
    loaded_state.context['new_data'] = 'updated'
    await manager.save_state(loaded_state)
    
    # Load again and check checkpoint
    final_state = await manager.load_state('test-agent-001', 'session-123')
    assert len(final_state.checkpoints) > 0, "No checkpoints created"
    print("✅ Checkpoint creation test passed")
    
    # Test checkpoint restoration
    if final_state.checkpoints:
        checkpoint_id = final_state.checkpoints[0].id
        restored_state = await manager.restore_from_checkpoint(
            'test-agent-001', 'session-123', checkpoint_id
        )
        assert restored_state is not None, "Failed to restore from checkpoint"
        print("✅ Checkpoint restoration test passed")
    
    print("\\n🎉 All agent state manager tests passed!")

if __name__ == "__main__":
    asyncio.run(test_state_manager())
`;

  return new Promise((resolve, reject) => {
    const python = spawn('python3', ['-c', testScript], {
      cwd: path.join(__dirname, '..'),
      stdio: 'inherit'
    });

    python.on('close', (code) => {
      if (code === 0) {
        console.log('\n✅ Agent State Manager test completed successfully!');
        resolve();
      } else {
        console.error(`\n❌ Test failed with exit code ${code}`);
        reject(new Error(`Test failed with exit code ${code}`));
      }
    });

    python.on('error', (err) => {
      console.error('❌ Failed to run Python test:', err.message);
      reject(err);
    });
  });
}

if (require.main === module) {
  testAgentStateManager().catch(console.error);
}

module.exports = { testAgentStateManager };