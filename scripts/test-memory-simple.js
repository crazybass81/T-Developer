#!/usr/bin/env node

// 간단한 메모리 옵티마이저 테스트
console.log('🧠 Testing Memory Optimizer (Simple)...\n');

// 메모리 사용량 체크 함수
function getMemoryUsage() {
  const usage = process.memoryUsage();
  return {
    heapUsed: Math.round(usage.heapUsed / 1024 / 1024),
    heapTotal: Math.round(usage.heapTotal / 1024 / 1024),
    rss: Math.round(usage.rss / 1024 / 1024)
  };
}

// 초기 메모리 상태
console.log('1. Initial Memory State:');
const initialMemory = getMemoryUsage();
console.log(`   Heap Used: ${initialMemory.heapUsed}MB`);
console.log(`   Heap Total: ${initialMemory.heapTotal}MB`);
console.log(`   RSS: ${initialMemory.rss}MB`);

// 메모리 사용량 증가 시뮬레이션
console.log('\n2. Memory Usage Simulation:');
const memoryHogs = [];

for (let i = 0; i < 5; i++) {
  // 큰 배열 생성
  const bigArray = new Array(100000).fill(`data-${i}-${Math.random()}`);
  memoryHogs.push(bigArray);
  
  const currentMemory = getMemoryUsage();
  console.log(`   Step ${i + 1}: ${currentMemory.heapUsed}MB heap used`);
}

// 객체 풀링 시뮬레이션
console.log('\n3. Object Pooling Simulation:');
const objectPool = [];

// 풀에서 객체 가져오기
function getFromPool() {
  if (objectPool.length > 0) {
    return objectPool.pop();
  }
  return { data: null, timestamp: Date.now() };
}

// 풀에 객체 반환
function returnToPool(obj) {
  // 객체 초기화
  obj.data = null;
  obj.timestamp = Date.now();
  
  if (objectPool.length < 50) {
    objectPool.push(obj);
  }
}

// 객체 풀 테스트
const testObjects = [];
for (let i = 0; i < 20; i++) {
  const obj = getFromPool();
  obj.data = `test-data-${i}`;
  testObjects.push(obj);
}

console.log(`   Created ${testObjects.length} objects`);
console.log(`   Pool size before return: ${objectPool.length}`);

// 객체 반환
testObjects.forEach(obj => returnToPool(obj));
console.log(`   Pool size after return: ${objectPool.length}`);

// 메모리 정리 시뮬레이션
console.log('\n4. Memory Cleanup Simulation:');
const beforeCleanup = getMemoryUsage();
console.log(`   Before cleanup: ${beforeCleanup.heapUsed}MB`);

// 큰 객체들 해제
memoryHogs.length = 0;

// 강제 가비지 컬렉션 (--expose-gc 플래그 필요)
if (global.gc) {
  global.gc();
  console.log('   ✅ Garbage collection triggered');
} else {
  console.log('   ⚠️  Garbage collection not available (use --expose-gc flag)');
}

setTimeout(() => {
  const afterCleanup = getMemoryUsage();
  console.log(`   After cleanup: ${afterCleanup.heapUsed}MB`);
  console.log(`   Memory freed: ${beforeCleanup.heapUsed - afterCleanup.heapUsed}MB`);
  
  // 메모리 효율적인 스트림 처리 시뮬레이션
  console.log('\n5. Memory Efficient Stream Processing:');
  
  const largeDataset = new Array(10000).fill(0).map((_, i) => ({
    id: i,
    data: `item-${i}`,
    timestamp: Date.now()
  }));
  
  console.log(`   Processing ${largeDataset.length} items in chunks...`);
  
  const chunkSize = 1000;
  let processedItems = 0;
  
  for (let i = 0; i < largeDataset.length; i += chunkSize) {
    const chunk = largeDataset.slice(i, i + chunkSize);
    
    // 청크 처리 시뮬레이션
    chunk.forEach(item => {
      // 간단한 처리
      item.processed = true;
    });
    
    processedItems += chunk.length;
    
    // 메모리 체크
    if (i % (chunkSize * 3) === 0) {
      const currentMemory = getMemoryUsage();
      console.log(`   Processed ${processedItems} items, Memory: ${currentMemory.heapUsed}MB`);
    }
  }
  
  console.log(`   ✅ Completed processing ${processedItems} items`);
  
  // 최종 메모리 상태
  console.log('\n6. Final Memory State:');
  const finalMemory = getMemoryUsage();
  console.log(`   Heap Used: ${finalMemory.heapUsed}MB`);
  console.log(`   Memory Change: ${finalMemory.heapUsed - initialMemory.heapUsed}MB`);
  
  console.log('\n✅ Memory Optimizer test completed!');
  
}, 1000);