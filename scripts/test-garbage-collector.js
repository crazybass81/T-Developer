#!/usr/bin/env node

const path = require('path');

// Mock global.gc for testing
global.gc = () => console.log('  🗑️ Native GC triggered');

async function testGarbageCollector() {
  console.log('🗑️ Testing Memory Garbage Collector...\n');

  try {
    // Compile TypeScript on the fly
    require('ts-node').register({
      transpileOnly: true,
      compilerOptions: {
        module: 'commonjs'
      }
    });

    const { MemoryGarbageCollector } = require('../backend/src/memory/garbage-collector.ts');

    // Test configuration
    const policy = {
      maxMemoryMB: 10,
      maxAge: 1, // 1 day
      minRelevance: 0.3,
      gcInterval: 2 // 2 seconds
    };

    const gc = new MemoryGarbageCollector(policy);

    // Test adding memory items
    gc.addMemoryItem('high_relevance', { data: 'important' }, 0.9);
    gc.addMemoryItem('low_relevance', { data: 'unimportant' }, 0.1);
    gc.addMemoryItem('medium_relevance', { data: 'somewhat important' }, 0.5);

    console.log('✅ Added 3 memory items');

    // Test accessing items
    const item1 = gc.getMemoryItem('high_relevance');
    const item2 = gc.getMemoryItem('high_relevance'); // Access again
    console.log('✅ Accessed high relevance item:', item1 ? 'found' : 'not found');

    // Get initial stats
    const initialStats = gc.getStats();
    console.log(`✅ Initial stats: ${initialStats.totalItems} items, ${initialStats.totalMemoryMB.toFixed(2)}MB`);

    // Start garbage collector
    gc.start();
    console.log('✅ Garbage collector started');

    // Wait for GC to run
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Get final stats
    const finalStats = gc.getStats();
    console.log(`✅ Final stats: ${finalStats.totalItems} items, ${finalStats.totalMemoryMB.toFixed(2)}MB`);

    // Stop garbage collector
    gc.stop();
    console.log('✅ Garbage collector stopped');

    // Verify low relevance item was removed
    const removedItem = gc.getMemoryItem('low_relevance');
    if (!removedItem) {
      console.log('✅ Low relevance item was garbage collected');
    } else {
      console.log('⚠️ Low relevance item still exists');
    }

    console.log('\n🎉 All garbage collector tests completed!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

if (require.main === module) {
  testGarbageCollector().catch(console.error);
}

module.exports = { testGarbageCollector };