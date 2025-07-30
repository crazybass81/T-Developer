// Task 1.8 Memory System Test
const { MemoryHierarchy } = require('../../src/agno/memory/memory-hierarchy');
const { ContextManager } = require('../../src/agno/memory/context-manager');

// Simple test runner
async function runTests() {
  console.log('🧪 Testing Task 1.8: Memory and State Management System\n');

  // Test 1: Memory Hierarchy
  console.log('📊 SubTask 1.8.1: Memory Hierarchy');
  try {
    const memory = new MemoryHierarchy();
    await memory.store('L1', 'test1', 'value1');
    await memory.store('L3', 'test2', 'value2');
    
    const val1 = await memory.get('test1');
    const val2 = await memory.get('test2');
    
    console.log('  ✅ Store/retrieve across levels:', val1 === 'value1' && val2 === 'value2');
    
    // Test promotion
    for (let i = 0; i < 5; i++) {
      await memory.get('test2');
    }
    const stats = memory.getStats();
    console.log('  ✅ Promotion system:', stats.promotions > 0);
    
  } catch (error) {
    console.log('  ❌ Memory Hierarchy failed:', error.message);
  }

  // Test 2: Context Manager
  console.log('\n💬 SubTask 1.8.2: Context Management');
  try {
    const context = new ContextManager();
    const sessionId = 'test-session';
    
    await context.addMessage(sessionId, {
      role: 'user',
      content: 'Hello world'
    });
    
    const ctx = await context.getContext(sessionId);
    console.log('  ✅ Context creation:', ctx.messages.length === 1);
    console.log('  ✅ Token counting:', ctx.tokenCount > 0);
    
  } catch (error) {
    console.log('  ❌ Context Manager failed:', error.message);
  }

  // Test 3: State Manager
  console.log('\n🔄 SubTask 1.8.3: State Management');
  try {
    const { StateManager } = require('../../src/memory/state-manager');
    const stateManager = new StateManager();
    
    const agentId = 'test-agent';
    const state = { status: 'active', data: { count: 5 } };
    
    const snapshotId = stateManager.saveState(agentId, state);
    const retrieved = stateManager.getState(agentId);
    
    console.log('  ✅ State save/retrieve:', JSON.stringify(retrieved) === JSON.stringify(state));
    console.log('  ✅ Snapshot generation:', snapshotId !== undefined);
    
  } catch (error) {
    console.log('  ❌ State Manager failed:', error.message);
  }

  // Test 4: Memory Optimization
  console.log('\n⚡ SubTask 1.8.4: Memory Optimization');
  try {
    const { MemoryOptimizer } = require('../../src/agno/memory/memory-optimization');
    const optimizer = new MemoryOptimizer();
    
    const largeText = 'Large data '.repeat(100);
    const compressed = optimizer.compress(largeText);
    
    console.log('  ✅ Data compression:', compressed.compressed === true);
    console.log('  ✅ Memory pressure detection:', typeof optimizer.getMemoryPressure() === 'number');
    
  } catch (error) {
    console.log('  ❌ Memory Optimizer failed:', error.message);
  }

  // Test 5: Analytics
  console.log('\n📈 SubTask 1.8.5: Memory Analytics');
  try {
    const { MemoryAnalytics } = require('../../src/agno/memory/memory-analytics');
    const analytics = new MemoryAnalytics();
    
    analytics.recordAccess('key1', 'L1', 'hit', 10);
    analytics.recordAccess('key2', 'L3', 'miss', 50);
    
    const report = analytics.generateReport();
    
    console.log('  ✅ Access recording:', report.summary.totalAccesses === 2);
    console.log('  ✅ Hit rate calculation:', report.summary.hitRate === 0.5);
    
  } catch (error) {
    console.log('  ❌ Memory Analytics failed:', error.message);
  }

  // Integration Test
  console.log('\n🔗 Integration Test');
  try {
    const memory = new MemoryHierarchy();
    const context = new ContextManager();
    
    // Add context and store in memory
    await context.addMessage('integration', { role: 'user', content: 'Integration test' });
    const ctx = await context.getContext('integration');
    await memory.store('L2', 'integration-context', ctx);
    
    const stored = await memory.get('integration-context');
    console.log('  ✅ Memory + Context integration:', stored.messages.length === 1);
    
  } catch (error) {
    console.log('  ❌ Integration test failed:', error.message);
  }

  console.log('\n🎉 Task 1.8 Testing Complete!');
}

runTests().catch(console.error);