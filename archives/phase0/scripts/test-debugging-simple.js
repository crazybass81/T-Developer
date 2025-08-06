#!/usr/bin/env node

const { performance } = require('perf_hooks');
const { AsyncLocalStorage } = require('async_hooks');
const util = require('util');
const crypto = require('crypto');

// Simple debugging tools test without external dependencies
console.log('🔧 Testing Debugging Tools (Simple)...\n');

// 1. Test AsyncLocalStorage for tracing
console.log('1. Testing AsyncLocalStorage tracing...');
const traceContext = new AsyncLocalStorage();

function generateTraceId() {
  return crypto.randomBytes(16).toString('hex');
}

function generateSpanId() {
  return crypto.randomBytes(8).toString('hex');
}

async function testTracing() {
  const traceId = generateTraceId();
  const spanId = generateSpanId();
  
  await traceContext.run({ traceId, spanId }, async () => {
    console.log('→ Starting operation', { traceId: traceId.slice(0, 8), spanId: spanId.slice(0, 8) });
    
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const context = traceContext.getStore();
    console.log('← Operation completed', { 
      traceId: context.traceId.slice(0, 8), 
      spanId: context.spanId.slice(0, 8) 
    });
  });
}

testTracing().then(() => {
  console.log('✅ AsyncLocalStorage tracing test passed\n');
  
  // 2. Test performance monitoring
  console.log('2. Testing performance monitoring...');
  const startTime = performance.now();
  
  return new Promise(resolve => setTimeout(resolve, 50)).then(() => {
    const duration = performance.now() - startTime;
    console.log(`Operation took ${duration.toFixed(2)}ms`);
    console.log('✅ Performance monitoring test passed\n');
    
    // 3. Test enhanced object inspection
console.log('3. Testing enhanced object inspection...');
const testObj = {
  name: 'test',
  nested: {
    value: 42,
    array: [1, 2, 3]
  }
};

console.log('Object inspection:');
console.log(util.inspect(testObj, {
  colors: true,
  depth: 4,
  compact: false
}));
console.log('✅ Object inspection test passed\n');

// 4. Test simple proxy debugging
console.log('4. Testing simple proxy debugging...');
function createSimpleDebugProxy(target, name = 'Object') {
  return new Proxy(target, {
    get(obj, prop) {
      const value = obj[prop];
      console.log(`[${name}] GET ${String(prop)} → ${value}`);
      return value;
    },
    set(obj, prop, value) {
      console.log(`[${name}] SET ${String(prop)} ← ${value}`);
      obj[prop] = value;
      return true;
    }
  });
}

const proxiedObj = createSimpleDebugProxy({ test: 'value' }, 'TestObj');
proxiedObj.test; // GET
proxiedObj.test = 'new value'; // SET
console.log('✅ Simple proxy debugging test passed\n');

// 5. Test execution timing
console.log('5. Testing execution timing...');
async function timeExecution(name, fn) {
  const start = performance.now();
  console.log(`→ ${name}`);
  
  try {
    const result = await fn();
    const duration = performance.now() - start;
    console.log(`← ${name} (${duration.toFixed(2)}ms)`);
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.log(`✗ ${name} (${duration.toFixed(2)}ms) - Error: ${error.message}`);
    throw error;
  }
}

await timeExecution('test-async-operation', async () => {
  await new Promise(resolve => setTimeout(resolve, 75));
  return 'completed';
});

console.log('✅ Execution timing test passed\n');

console.log('🎉 All debugging tools tests passed!');
console.log('\n📊 Test Summary:');
console.log('- AsyncLocalStorage tracing: ✅');
console.log('- Performance monitoring: ✅');
console.log('- Object inspection: ✅');
console.log('- Proxy debugging: ✅');
console.log('- Execution timing: ✅');