#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

async function testContextManager() {
  console.log('🧠 Testing Context Manager...\n');

  const testScript = `
import asyncio
import sys
sys.path.append('${path.join(__dirname, '../backend/src')}')

from memory.context_manager import ContextManager

async def test_context_manager():
    manager = ContextManager(max_context_size=5)
    
    # Test adding context
    await manager.add_context(
        'project_type', 
        'web application',
        source='user',
        metadata={'priority': 'high'}
    )
    
    await manager.add_context(
        'requirements',
        ['authentication', 'database', 'api'],
        source='analysis'
    )
    
    print("✅ Context entries added successfully")
    
    # Test getting relevant context
    relevant = await manager.get_relevant_context('web application requirements')
    assert len(relevant) > 0, "No relevant context found"
    print(f"✅ Found {len(relevant)} relevant context entries")
    
    # Test context summary
    summary = await manager.get_context_summary()
    print(f"✅ Context summary: {summary['total_entries']} entries")
    
    print("\\n🎉 All context manager tests passed!")

if __name__ == "__main__":
    asyncio.run(test_context_manager())
`;

  return new Promise((resolve, reject) => {
    const python = spawn('python3', ['-c', testScript], {
      cwd: path.join(__dirname, '..'),
      stdio: 'inherit'
    });

    python.on('close', (code) => {
      if (code === 0) {
        console.log('\n✅ Context Manager test completed successfully!');
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
  testContextManager().catch(console.error);
}

module.exports = { testContextManager };