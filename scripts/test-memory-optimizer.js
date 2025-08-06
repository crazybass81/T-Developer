#!/usr/bin/env node

const { MemoryOptimizer, MemoryEfficientStream, MemoryProfiler } = require('../backend/src/performance/memory-optimizer');

async function testMemoryOptimizer() {
  console.log('🧠 Testing Memory Optimizer...\n');
  
  // 1. 메모리 옵티마이저 테스트
  console.log('1. Memory Optimizer Test:');
  const optimizer = new MemoryOptimizer({
    warning: 50 * 1024 * 1024,    // 50MB (테스트용 낮은 값)
    critical: 100 * 1024 * 1024,  // 100MB
    gcTrigger: 75 * 1024 * 1024   // 75MB
  });
  
  // 이벤트 리스너 등록
  optimizer.on('warning', (stats) => {
    console.log(`⚠️  Memory warning: ${Math.round(stats.heapUsed / 1024 / 1024)}MB used`);
  });
  
  optimizer.on('critical', (stats) => {
    console.log(`🚨 Memory critical: ${Math.round(stats.heapUsed / 1024 / 1024)}MB used`);
  });
  
  // 초기 메모리 상태
  const initialStats = optimizer.getMemoryStats();
  console.log(`Initial memory: ${Math.round(initialStats.heapUsed / 1024 / 1024)}MB`);
  
  // 2. 객체 풀링 테스트
  console.log('\n2. Object Pooling Test:');
  optimizer.createPool('testObjects', () => ({ data: null }), 50);
  
  // 객체 생성 및 반환
  const objects = [];
  for (let i = 0; i < 10; i++) {
    const obj = optimizer.getFromPool('testObjects', () => ({ data: `test-${i}` }));
    objects.push(obj);
  }
  console.log(`✅ Created ${objects.length} objects from pool`);
  
  // 객체 반환
  objects.forEach(obj => optimizer.returnToPool('testObjects', obj));
  console.log('✅ Returned objects to pool');
  
  // 3. WeakRef 테스트
  console.log('\n3. WeakRef Test:');
  let testObj = { name: 'test', data: new Array(1000).fill('data') };
  const weakRef = optimizer.addWeakRef(testObj);
  console.log(`✅ WeakRef created: ${weakRef.deref() ? 'alive' : 'dead'}`);
  
  // 객체 해제
  testObj = null;
  
  // 강제 GC 후 WeakRef 확인
  if (global.gc) {
    global.gc();
    setTimeout(() => {
      console.log(`WeakRef after GC: ${weakRef.deref() ? 'alive' : 'dead'}`);
      const cleaned = optimizer.cleanupWeakRefs();
      console.log(`✅ Cleaned up ${cleaned} weak references`);
    }, 100);
  }
  
  // 4. 메모리 효율적인 스트림 테스트
  console.log('\n4. Memory Efficient Stream Test:');
  const stream = new MemoryEfficientStream(1000);
  const largeArray = new Array(5000).fill(0).map((_, i) => ({ id: i, data: `item-${i}` }));
  
  let processedChunks = 0;
  for await (const result of stream.processLargeData(largeArray, async (chunk) => {
    // 청크 처리 시뮬레이션
    return chunk.length;
  })) {
    processedChunks++;
  }
  console.log(`✅ Processed ${processedChunks} chunks from ${largeArray.length} items`);
  
  // 5. 메모리 프로파일러 테스트
  console.log('\n5. Memory Profiler Test:');
  const profiler = new MemoryProfiler();
  
  // 여러 스냅샷 생성
  for (let i = 0; i < 5; i++) {
    const snapshot = profiler.takeSnapshot();
    console.log(`Snapshot ${i + 1}: ${Math.round(snapshot.heapUsed / 1024 / 1024)}MB`);
    
    // 메모리 사용량 증가 시뮬레이션
    const tempArray = new Array(10000).fill('memory-test');
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  const trend = profiler.getMemoryTrend();
  console.log(`✅ Memory trend: ${trend.trend} (avg growth: ${Math.round(trend.averageGrowth / 1024)}KB)`);
  
  // 6. 메모리 모니터링 시작 (짧은 시간)
  console.log('\n6. Memory Monitoring Test:');
  optimizer.startMonitoring(1000); // 1초마다
  
  // 메모리 사용량 증가 시뮬레이션
  const memoryHogs = [];
  for (let i = 0; i < 3; i++) {
    memoryHogs.push(new Array(1000000).fill(`memory-hog-${i}`));
    await new Promise(resolve => setTimeout(resolve, 1500));
  }
  
  // 정리
  setTimeout(() => {
    optimizer.stopMonitoring();
    console.log('\n✅ Memory Optimizer tests completed!');
    
    const finalStats = optimizer.getMemoryStats();
    console.log(`Final memory: ${Math.round(finalStats.heapUsed / 1024 / 1024)}MB`);
    console.log(`Memory difference: ${Math.round((finalStats.heapUsed - initialStats.heapUsed) / 1024 / 1024)}MB`);
  }, 5000);
}

// 에러 처리
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error.message);
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  console.error('❌ Unhandled Rejection:', reason);
  process.exit(1);
});

// 테스트 실행
testMemoryOptimizer().catch(console.error);