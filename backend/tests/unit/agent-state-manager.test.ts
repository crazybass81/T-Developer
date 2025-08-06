import { spawn } from 'child_process';
import path from 'path';

describe('AgentStateManager', () => {
  it('should save and load agent state', async () => {
    const testScript = `
import asyncio
import sys
sys.path.append('${path.join(__dirname, '../../src')}')

from memory.agent_state_manager import AgentStateManager, AgentState
from datetime import datetime

async def test():
    manager = AgentStateManager()
    
    state = AgentState(
        agent_id='test-001',
        session_id='session-001',
        context={'task': 'test'},
        memory={'data': 'value'},
        last_activity=datetime.utcnow(),
        checkpoints=[]
    )
    
    await manager.save_state(state)
    loaded = await manager.load_state('test-001', 'session-001')
    
    assert loaded is not None
    assert loaded.agent_id == 'test-001'
    print("SUCCESS")

asyncio.run(test())
`;

    return new Promise((resolve, reject) => {
      const python = spawn('python3', ['-c', testScript], {
        stdio: 'pipe'
      });

      let output = '';
      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.on('close', (code) => {
        if (code === 0 && output.includes('SUCCESS')) {
          resolve(undefined);
        } else {
          reject(new Error(`Test failed with code ${code}`));
        }
      });
    });
  }, 10000);

  it('should create checkpoints', async () => {
    const testScript = `
import asyncio
import sys
import time
sys.path.append('${path.join(__dirname, '../../src')}')

from memory.agent_state_manager import AgentStateManager, AgentState
from datetime import datetime

async def test():
    manager = AgentStateManager()
    
    state = AgentState(
        agent_id='test-002',
        session_id='session-002',
        context={'task': 'test'},
        memory={'data': 'value'},
        last_activity=datetime.utcnow(),
        checkpoints=[]
    )
    
    await manager.save_state(state)
    time.sleep(2)  # Wait for checkpoint interval
    
    state.context['updated'] = True
    await manager.save_state(state)
    
    loaded = await manager.load_state('test-002', 'session-002')
    assert len(loaded.checkpoints) > 0
    print("SUCCESS")

asyncio.run(test())
`;

    return new Promise((resolve, reject) => {
      const python = spawn('python3', ['-c', testScript], {
        stdio: 'pipe'
      });

      let output = '';
      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.on('close', (code) => {
        if (code === 0 && output.includes('SUCCESS')) {
          resolve(undefined);
        } else {
          reject(new Error(`Test failed with code ${code}`));
        }
      });
    });
  }, 15000);
});