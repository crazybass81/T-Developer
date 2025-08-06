#!/usr/bin/env node

require('ts-node/register');

const { ParallelExecutor } = require('../backend/src/workflow/parallel-executor.ts');

async function testParallelExecutor() {
  console.log('⚡ 병렬 실행 엔진 테스트 시작...\n');

  try {
    // 1. 기본 병렬 실행 테스트
    console.log('📋 테스트 1: 기본 병렬 실행');
    
    const executor = new ParallelExecutor(5);

    const simpleTasks = [
      { id: 'task-1', type: 'process', payload: { data: 'A' } },
      { id: 'task-2', type: 'process', payload: { data: 'B' } },
      { id: 'task-3', type: 'process', payload: { data: 'C' } }
    ];

    const startTime = Date.now();
    const results = await executor.executeParallel(simpleTasks);
    const totalTime = Date.now() - startTime;

    console.log(`✅ 3개 태스크 병렬 실행 완료 (${totalTime}ms)`);
    console.log(`✅ 성공: ${results.filter(r => r.status === 'completed').length}개`);
    console.log(`✅ 실패: ${results.filter(r => r.status === 'failed').length}개`);
    
    const stats = executor.getExecutionStats();
    console.log(`✅ 성공률: ${(stats.successRate * 100).toFixed(1)}%`);
    console.log(`✅ 평균 실행 시간: ${stats.averageExecutionTime}ms\n`);

    // 2. 의존성이 있는 태스크 테스트
    console.log('📋 테스트 2: 의존성 기반 실행');
    
    const executor2 = new ParallelExecutor(10);

    const dependentTasks = [
      { id: 'init', type: 'initialize', payload: { step: 1 } },
      { id: 'process-a', type: 'process', payload: { step: 2 }, dependencies: ['init'] },
      { id: 'process-b', type: 'process', payload: { step: 2 }, dependencies: ['init'] },
      { id: 'combine', type: 'combine', payload: { step: 3 }, dependencies: ['process-a', 'process-b'] },
      { id: 'finalize', type: 'finalize', payload: { step: 4 }, dependencies: ['combine'] }
    ];

    const depStartTime = Date.now();
    const depResults = await executor2.executeParallel(dependentTasks);
    const depTotalTime = Date.now() - depStartTime;

    console.log(`✅ 의존성 태스크 실행 완료 (${depTotalTime}ms)`);
    
    // 실행 순서 확인
    const sortedResults = depResults.sort((a, b) => a.startTime - b.startTime);
    console.log('✅ 실행 순서:');
    sortedResults.forEach((result, index) => {
      console.log(`   ${index + 1}. ${result.taskId} (${result.executionTime}ms)`);
    });

    const depStats = executor2.getExecutionStats();
    console.log(`✅ 성공률: ${(depStats.successRate * 100).toFixed(1)}%\n`);

    // 3. 대량 태스크 병렬 처리 테스트
    console.log('📋 테스트 3: 대량 태스크 병렬 처리');
    
    const executor3 = new ParallelExecutor(20);

    // 50개의 독립적인 태스크 생성
    const largeTasks = Array.from({ length: 50 }, (_, i) => ({
      id: `bulk-task-${i}`,
      type: 'bulk-process',
      payload: { index: i, data: `Data-${i}` }
    }));

    const bulkStartTime = Date.now();
    const bulkResults = await executor3.executeParallel(largeTasks);
    const bulkTotalTime = Date.now() - bulkStartTime;

    console.log(`✅ 50개 태스크 병렬 실행 완료 (${bulkTotalTime}ms)`);
    
    const bulkStats = executor3.getExecutionStats();
    console.log(`✅ 성공: ${bulkStats.completed}개, 실패: ${bulkStats.failed}개`);
    console.log(`✅ 성공률: ${(bulkStats.successRate * 100).toFixed(1)}%`);
    console.log(`✅ 평균 실행 시간: ${bulkStats.averageExecutionTime}ms`);
    console.log(`✅ 최대 동시 실행: ${bulkStats.maxWorkers}개\n`);

    // 4. 타임아웃 처리 테스트
    console.log('📋 테스트 4: 타임아웃 처리');
    
    const executor4 = new ParallelExecutor(5);

    const timeoutTasks = [
      { id: 'normal-task', type: 'normal', payload: {}, timeout: 2000 },
      { id: 'slow-task', type: 'slow', payload: {}, timeout: 500 }, // 짧은 타임아웃
      { id: 'fast-task', type: 'fast', payload: {}, timeout: 3000 }
    ];

    const timeoutResults = await executor4.executeParallel(timeoutTasks);
    
    console.log('✅ 타임아웃 테스트 결과:');
    timeoutResults.forEach(result => {
      console.log(`   ${result.taskId}: ${result.status} (${result.executionTime}ms)`);
      if (result.error) {
        console.log(`     오류: ${result.error}`);
      }
    });

    const timeoutStats = executor4.getExecutionStats();
    console.log(`✅ 타임아웃: ${timeoutStats.timeout}개\n`);

    // 5. 복잡한 의존성 그래프 테스트
    console.log('📋 테스트 5: 복잡한 의존성 그래프');
    
    const executor5 = new ParallelExecutor(15);

    const complexTasks = [
      // 레벨 0 (시작점)
      { id: 'start-1', type: 'start', payload: {} },
      { id: 'start-2', type: 'start', payload: {} },
      
      // 레벨 1
      { id: 'level1-a', type: 'process', payload: {}, dependencies: ['start-1'] },
      { id: 'level1-b', type: 'process', payload: {}, dependencies: ['start-1'] },
      { id: 'level1-c', type: 'process', payload: {}, dependencies: ['start-2'] },
      
      // 레벨 2
      { id: 'level2-a', type: 'process', payload: {}, dependencies: ['level1-a', 'level1-b'] },
      { id: 'level2-b', type: 'process', payload: {}, dependencies: ['level1-b', 'level1-c'] },
      
      // 레벨 3 (종료점)
      { id: 'final', type: 'finalize', payload: {}, dependencies: ['level2-a', 'level2-b'] }
    ];

    const complexStartTime = Date.now();
    const complexResults = await executor5.executeParallel(complexTasks);
    const complexTotalTime = Date.now() - complexStartTime;

    console.log(`✅ 복잡한 의존성 그래프 실행 완료 (${complexTotalTime}ms)`);
    
    // 레벨별 실행 분석
    const levelAnalysis = new Map();
    const sortedComplexResults = complexResults.sort((a, b) => a.startTime - b.startTime);
    
    sortedComplexResults.forEach((result, index) => {
      const level = Math.floor(index / 3); // 대략적인 레벨 계산
      if (!levelAnalysis.has(level)) {
        levelAnalysis.set(level, []);
      }
      levelAnalysis.get(level).push(result.taskId);
    });

    console.log('✅ 레벨별 실행:');
    for (const [level, tasks] of levelAnalysis) {
      console.log(`   레벨 ${level}: ${tasks.join(', ')}`);
    }

    const complexStats = executor5.getExecutionStats();
    console.log(`✅ 성공률: ${(complexStats.successRate * 100).toFixed(1)}%\n`);

    // 6. 에러 처리 및 복구 테스트
    console.log('📋 테스트 6: 에러 처리');
    
    const executor6 = new ParallelExecutor(5);

    // 일부러 실패하는 태스크 포함
    const errorTasks = [
      { id: 'good-1', type: 'reliable', payload: {} },
      { id: 'bad-1', type: 'unreliable', payload: {} }, // 실패 가능성 높음
      { id: 'good-2', type: 'reliable', payload: {} },
      { id: 'dependent-on-bad', type: 'process', payload: {}, dependencies: ['bad-1'] },
      { id: 'independent', type: 'process', payload: {} }
    ];

    const errorResults = await executor6.executeParallel(errorTasks);
    
    console.log('✅ 에러 처리 테스트 결과:');
    errorResults.forEach(result => {
      const status = result.status === 'completed' ? '✅' : '❌';
      console.log(`   ${status} ${result.taskId}: ${result.status}`);
      if (result.error) {
        console.log(`     오류: ${result.error}`);
      }
    });

    const errorStats = executor6.getExecutionStats();
    console.log(`✅ 전체 성공률: ${(errorStats.successRate * 100).toFixed(1)}%`);

    // 7. 성능 벤치마크
    console.log('\n📋 테스트 7: 성능 벤치마크');
    
    const benchmarkSizes = [10, 50, 100];
    
    for (const size of benchmarkSizes) {
      const benchmarkExecutor = new ParallelExecutor(Math.min(size, 50));
      
      const benchmarkTasks = Array.from({ length: size }, (_, i) => ({
        id: `bench-${i}`,
        type: 'benchmark',
        payload: { index: i }
      }));

      const benchStart = Date.now();
      const benchResults = await benchmarkExecutor.executeParallel(benchmarkTasks);
      const benchTime = Date.now() - benchStart;

      const benchStats = benchmarkExecutor.getExecutionStats();
      
      console.log(`✅ ${size}개 태스크: ${benchTime}ms (성공률: ${(benchStats.successRate * 100).toFixed(1)}%)`);
    }

    console.log('\n✅ 병렬 실행 엔진 테스트 완료!');

  } catch (error) {
    console.error('❌ 병렬 실행 엔진 테스트 실패:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// 스크립트 직접 실행 시
if (require.main === module) {
  testParallelExecutor();
}

module.exports = { testParallelExecutor };