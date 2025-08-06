#!/usr/bin/env node

require('ts-node/register');

const { DependencyManager } = require('../backend/src/workflow/dependency-manager.ts');

async function testDependencyManager() {
  console.log('🔗 의존성 관리 시스템 테스트 시작...\n');

  try {
    // 1. 기본 의존성 관리 테스트
    console.log('📋 테스트 1: 기본 의존성 관리');
    
    const manager = new DependencyManager();

    // 의존성 추가
    manager.addDependency({
      taskId: 'task-a',
      dependsOn: [],
      type: 'hard'
    });

    manager.addDependency({
      taskId: 'task-b',
      dependsOn: ['task-a'],
      type: 'hard'
    });

    manager.addDependency({
      taskId: 'task-c',
      dependsOn: ['task-a', 'task-b'],
      type: 'hard'
    });

    // 실행 순서 확인
    const executionOrder = manager.getExecutionOrder();
    console.log(`✅ 실행 순서: ${executionOrder.join(' → ')}`);

    // 초기 준비된 태스크 확인
    let readyTasks = manager.getReadyTasks();
    console.log(`✅ 초기 준비된 태스크: ${readyTasks.join(', ')}`);

    // task-a 완료 처리
    manager.updateTaskStatus('task-a', {
      id: 'task-a',
      status: 'completed',
      result: 'Task A 완료',
      startTime: Date.now() - 1000,
      endTime: Date.now()
    });

    readyTasks = manager.getReadyTasks();
    console.log(`✅ task-a 완료 후 준비된 태스크: ${readyTasks.join(', ')}`);

    // task-b 완료 처리
    manager.updateTaskStatus('task-b', {
      id: 'task-b',
      status: 'completed',
      result: 'Task B 완료',
      startTime: Date.now() - 500,
      endTime: Date.now()
    });

    readyTasks = manager.getReadyTasks();
    console.log(`✅ task-b 완료 후 준비된 태스크: ${readyTasks.join(', ')}\n`);

    // 2. 순환 의존성 검사 테스트
    console.log('📋 테스트 2: 순환 의존성 검사');
    
    const manager2 = new DependencyManager();

    try {
      manager2.addDependency({
        taskId: 'circular-a',
        dependsOn: ['circular-b'],
        type: 'hard'
      });

      manager2.addDependency({
        taskId: 'circular-b',
        dependsOn: ['circular-c'],
        type: 'hard'
      });

      manager2.addDependency({
        taskId: 'circular-c',
        dependsOn: ['circular-a'], // 순환 의존성!
        type: 'hard'
      });

      console.log('❌ 순환 의존성이 감지되지 않음');
    } catch (error) {
      console.log(`✅ 순환 의존성 감지: ${error.message}`);
    }
    console.log();

    // 3. Soft 의존성 테스트
    console.log('📋 테스트 3: Soft 의존성 처리');
    
    const manager3 = new DependencyManager();

    manager3.addDependency({
      taskId: 'base-task',
      dependsOn: [],
      type: 'hard'
    });

    manager3.addDependency({
      taskId: 'failing-task',
      dependsOn: ['base-task'],
      type: 'hard'
    });

    manager3.addDependency({
      taskId: 'soft-dependent',
      dependsOn: ['failing-task'],
      type: 'soft' // Soft 의존성
    });

    manager3.addDependency({
      taskId: 'hard-dependent',
      dependsOn: ['failing-task'],
      type: 'hard' // Hard 의존성
    });

    // base-task 완료
    manager3.updateTaskStatus('base-task', {
      id: 'base-task',
      status: 'completed'
    });

    // failing-task 실패
    manager3.updateTaskStatus('failing-task', {
      id: 'failing-task',
      status: 'failed',
      error: '의도적 실패'
    });

    // 실행 가능성 확인
    const canExecuteSoft = await manager3.canExecute('soft-dependent');
    const canExecuteHard = await manager3.canExecute('hard-dependent');

    console.log(`✅ Soft 의존성 태스크 실행 가능: ${canExecuteSoft}`);
    console.log(`✅ Hard 의존성 태스크 실행 가능: ${canExecuteHard}\n`);

    // 4. 복잡한 의존성 그래프 테스트
    console.log('📋 테스트 4: 복잡한 의존성 그래프');
    
    const manager4 = new DependencyManager();

    // 복잡한 의존성 구조 생성
    const complexDeps = [
      { taskId: 'init-1', dependsOn: [], type: 'hard' },
      { taskId: 'init-2', dependsOn: [], type: 'hard' },
      { taskId: 'process-1', dependsOn: ['init-1'], type: 'hard' },
      { taskId: 'process-2', dependsOn: ['init-2'], type: 'hard' },
      { taskId: 'process-3', dependsOn: ['init-1', 'init-2'], type: 'hard' },
      { taskId: 'combine-1', dependsOn: ['process-1', 'process-2'], type: 'hard' },
      { taskId: 'combine-2', dependsOn: ['process-2', 'process-3'], type: 'hard' },
      { taskId: 'finalize', dependsOn: ['combine-1', 'combine-2'], type: 'hard' }
    ];

    for (const dep of complexDeps) {
      manager4.addDependency(dep);
    }

    const complexOrder = manager4.getExecutionOrder();
    console.log(`✅ 복잡한 실행 순서: ${complexOrder.join(' → ')}`);

    // 의존성 검증
    const validation = manager4.validateDependencies();
    console.log(`✅ 의존성 검증: ${validation.isValid ? '통과' : '실패'}`);
    if (!validation.isValid) {
      console.log(`❌ 검증 오류: ${validation.errors.join(', ')}`);
    }

    // 통계 확인
    const stats = manager4.getStats();
    console.log(`✅ 통계: 총 ${stats.totalTasks}개 태스크, ${stats.totalDependencies}개 의존성`);
    console.log(`   - 대기: ${stats.statusCounts.pending}, 준비: ${stats.readyTasks}\n`);

    // 5. 의존성 추적 테스트
    console.log('📋 테스트 5: 의존성 추적');
    
    const taskId = 'combine-1';
    const dependencies = manager4.getDependencies(taskId);
    const dependents = manager4.getDependents(taskId);

    console.log(`✅ ${taskId}의 의존성: ${dependencies.join(', ')}`);
    console.log(`✅ ${taskId}에 의존하는 태스크: ${dependents.join(', ')}`);

    // 6. 조건부 의존성 테스트
    console.log('\n📋 테스트 6: 조건부 의존성');
    
    const manager5 = new DependencyManager();

    manager5.addDependency({
      taskId: 'conditional-task',
      dependsOn: ['base-task'],
      type: 'hard',
      condition: 'true' // 간단한 조건
    });

    manager5.addDependency({
      taskId: 'base-task',
      dependsOn: [],
      type: 'hard'
    });

    manager5.updateTaskStatus('base-task', {
      id: 'base-task',
      status: 'completed'
    });

    const canExecuteConditional = await manager5.canExecute('conditional-task');
    console.log(`✅ 조건부 태스크 실행 가능: ${canExecuteConditional}`);

    // 7. 성능 테스트
    console.log('\n📋 테스트 7: 성능 테스트');
    
    const manager6 = new DependencyManager();
    const startTime = Date.now();

    // 대량의 의존성 생성 (100개 태스크)
    for (let i = 0; i < 100; i++) {
      const dependsOn = i > 0 ? [`task-${i-1}`] : [];
      manager6.addDependency({
        taskId: `task-${i}`,
        dependsOn,
        type: 'hard'
      });
    }

    const executionTime = Date.now() - startTime;
    const largeOrder = manager6.getExecutionOrder();
    
    console.log(`✅ 100개 태스크 처리 시간: ${executionTime}ms`);
    console.log(`✅ 실행 순서 길이: ${largeOrder.length}`);
    console.log(`✅ 첫 5개: ${largeOrder.slice(0, 5).join(', ')}`);
    console.log(`✅ 마지막 5개: ${largeOrder.slice(-5).join(', ')}`);

    console.log('\n✅ 의존성 관리 시스템 테스트 완료!');

  } catch (error) {
    console.error('❌ 의존성 관리 시스템 테스트 실패:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// 스크립트 직접 실행 시
if (require.main === module) {
  testDependencyManager();
}

module.exports = { testDependencyManager };