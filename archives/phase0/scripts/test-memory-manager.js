#!/usr/bin/env node

const { MemoryManager, MemoryPoolManager, WeakCache } = require('../backend/src/performance/memory-manager');

async function testMemoryManager() {
  console.log('🧠 Testing Memory Manager...\n');

  // Test 1: Memory Manager
  const memoryManager = new MemoryManager();
  
  // Test memory status
  const status = memoryManager.getMemoryStatus();
  console.log('✅ Memory Status:', {
    heapUsed: `${status.heapUsed.toFixed(2)} MB`,
    heapTotal: `${status.heapTotal.toFixed(2)} MB`,
    rss: `${status.rss.toFixed(2)} MB`,
    heapUsagePercent: `${status.heapUsagePercent.toFixed(2)}%`
  });

  // Test monitoring
  memoryManager.startMonitoring(5000);
  console.log('✅ Memory monitoring started');

  // Test event listeners
  memoryManager.on('memory:warning', (status) => {
    console.log('⚠️ Memory warning:', status.heapUsed.toFixed(2), 'MB');
  });

  memoryManager.on('memory:critical', (status) => {
    console.log('🚨 Critical memory:', status.heapUsed.toFixed(2), 'MB');
  });

  // Test 2: Memory Pool Manager
  console.log('\n📦 Testing Memory Pool Manager...');
  
  const pool = new MemoryPoolManager(
    () => ({ data: new Array(1000).fill(0) }),
    (obj) => { obj.data.fill(0); },
    10
  );

  // Acquire and release objects
  const obj1 = pool.acquire();
  const obj2 = pool.acquire();
  console.log('✅ Pool stats after acquire:', pool.getStats());

  pool.release(obj1);
  pool.release(obj2);
  console.log('✅ Pool stats after release:', pool.getStats());

  // Test 3: WeakCache
  console.log('\n💾 Testing WeakCache...');
  
  const cache = new WeakCache(5000); // 5 second TTL
  const key = { id: 'test' };
  
  cache.set(key, 'cached value');
  console.log('✅ Cache set, value:', cache.get(key));
  
  // Wait for TTL
  setTimeout(() => {
    console.log('✅ Cache after TTL:', cache.get(key) || 'expired');
  }, 6000);

  // Test 4: Heap Snapshot (if --expose-gc is available)
  if (global.gc) {
    console.log('\n📸 Creating heap snapshot...');
    try {
      const snapshotPath = await memoryManager.createHeapSnapshot();
      console.log('✅ Heap snapshot created:', snapshotPath);
    } catch (error) {
      console.log('❌ Heap snapshot failed:', error.message);
    }
  } else {
    console.log('\n⚠️ Heap snapshot requires --expose-gc flag');
  }

  // Cleanup
  setTimeout(() => {
    memoryManager.stopMonitoring();
    console.log('\n✅ Memory monitoring stopped');
    console.log('🎉 All memory manager tests completed!');
  }, 10000);
}

// Memory stress test
function createMemoryPressure() {
  const arrays = [];
  for (let i = 0; i < 100; i++) {
    arrays.push(new Array(10000).fill(Math.random()));
  }
  return arrays;
}

if (require.main === module) {
  testMemoryManager().catch(console.error);
}