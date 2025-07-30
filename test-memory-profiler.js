// Test memory profiler
class MemoryProfiler {
  constructor() {
    this.snapshots = [];
    this.isRunning = false;
    this.interval = null;
  }
  
  start(intervalMs = 100) {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this.snapshots = [];
    
    this.interval = setInterval(() => {
      this.takeSnapshot();
    }, intervalMs);
    
    console.log(`📊 Memory profiling started (${intervalMs}ms intervals)`);
  }
  
  stop() {
    if (!this.isRunning) {
      throw new Error('Profiler not running');
    }
    
    this.isRunning = false;
    if (this.interval) {
      clearInterval(this.interval);
    }
    
    console.log(`📊 Memory profiling stopped (${this.snapshots.length} snapshots)`);
    return this.analyzeProfile();
  }
  
  takeSnapshot() {
    const memUsage = process.memoryUsage();
    
    this.snapshots.push({
      timestamp: Date.now(),
      heapUsed: memUsage.heapUsed,
      heapTotal: memUsage.heapTotal,
      external: memUsage.external,
      rss: memUsage.rss,
      arrayBuffers: memUsage.arrayBuffers || 0
    });
  }
  
  analyzeProfile() {
    if (this.snapshots.length === 0) {
      throw new Error('No snapshots available');
    }
    
    const duration = this.snapshots[this.snapshots.length - 1].timestamp - this.snapshots[0].timestamp;
    const heapValues = this.snapshots.map(s => s.heapUsed);
    
    return {
      duration,
      snapshots: this.snapshots.length,
      summary: {
        maxHeapUsed: Math.max(...heapValues),
        avgHeapUsed: heapValues.reduce((a, b) => a + b, 0) / heapValues.length,
        memoryGrowth: this.calculateMemoryGrowth(),
        gcEvents: this.estimateGCCount()
      }
    };
  }
  
  calculateMemoryGrowth() {
    if (this.snapshots.length < 2) return 0;
    
    const first = this.snapshots[0].heapUsed;
    const last = this.snapshots[this.snapshots.length - 1].heapUsed;
    
    return last - first;
  }
  
  estimateGCCount() {
    let gcCount = 0;
    
    for (let i = 1; i < this.snapshots.length; i++) {
      const current = this.snapshots[i];
      const prev = this.snapshots[i - 1];
      
      // Significant heap decrease indicates GC
      if (prev.heapUsed - current.heapUsed > 1024 * 1024) { // 1MB decrease
        gcCount++;
      }
    }
    
    return gcCount;
  }
}

// Memory stress test
async function memoryStressTest() {
  console.log('🧠 Starting Memory Profiler Test\n');
  
  const profiler = new MemoryProfiler();
  profiler.start(50); // 50ms intervals
  
  // Create memory pressure
  const arrays = [];
  
  console.log('💾 Creating memory pressure...');
  for (let i = 0; i < 100; i++) {
    // Create large arrays to stress memory
    arrays.push(new Array(10000).fill(Math.random()));
    
    if (i % 20 === 0) {
      console.log(`  Created ${i + 1}/100 arrays`);
      // Force some cleanup
      if (arrays.length > 50) {
        arrays.splice(0, 10);
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  
  console.log('🗑️  Cleaning up memory...');
  arrays.length = 0; // Clear arrays
  
  // Wait a bit more
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const result = profiler.stop();
  
  console.log('\n📈 Memory Profile Results:');
  console.log('========================');
  console.log(`Duration: ${result.duration}ms`);
  console.log(`Snapshots: ${result.snapshots}`);
  console.log(`Max Heap Used: ${(result.summary.maxHeapUsed / 1024 / 1024).toFixed(2)} MB`);
  console.log(`Avg Heap Used: ${(result.summary.avgHeapUsed / 1024 / 1024).toFixed(2)} MB`);
  console.log(`Memory Growth: ${(result.summary.memoryGrowth / 1024 / 1024).toFixed(2)} MB`);
  console.log(`Estimated GC Events: ${result.summary.gcEvents}`);
  
  console.log('\n✅ Memory profiler test completed!');
}

// Run the test
memoryStressTest().catch(console.error);