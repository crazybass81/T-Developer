#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

async function testHierarchicalMemory() {
  console.log('🧠 Testing Hierarchical Memory System...\n');

  const testScript = `
import asyncio
import sys
import os
sys.path.append('${path.join(__dirname, '../backend/src')}')

from memory.hierarchical_memory import HierarchicalMemorySystem

async def test_memory_system():
    memory = HierarchicalMemorySystem()
    
    # Test normal importance (working memory only)
    await memory.remember('test_key', {'data': 'test_value'}, 'normal')
    result = await memory.recall('test_key')
    assert result == {'data': 'test_value'}, "Normal memory test failed"
    print("✅ Normal importance memory test passed")
    
    # Test high importance (short-term + long-term)
    await memory.remember('important_key', {'data': 'important_value'}, 'high')
    result = await memory.recall('important_key')
    assert result == {'data': 'important_value'}, "High importance memory test failed"
    print("✅ High importance memory test passed")
    
    # Test critical importance (all layers)
    await memory.remember('critical_key', {'data': 'critical_value'}, 'critical')
    result = await memory.recall('critical_key')
    assert result == {'data': 'critical_value'}, "Critical importance memory test failed"
    print("✅ Critical importance memory test passed")
    
    print("\\n🎉 All hierarchical memory tests passed!")

if __name__ == "__main__":
    asyncio.run(test_memory_system())
`;

  return new Promise((resolve, reject) => {
    const python = spawn('python3', ['-c', testScript], {
      cwd: path.join(__dirname, '..'),
      stdio: 'inherit'
    });

    python.on('close', (code) => {
      if (code === 0) {
        console.log('\n✅ Hierarchical Memory System test completed successfully!');
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
  testHierarchicalMemory().catch(console.error);
}

module.exports = { testHierarchicalMemory };