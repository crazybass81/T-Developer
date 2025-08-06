#!/usr/bin/env node

require('ts-node/register');

const { StateSynchronizer } = require('../backend/src/workflow/state-synchronizer.ts');

async function testStateSynchronizer() {
  console.log('🔄 상태 동기화 메커니즘 테스트 시작...\n');

  let synchronizer;

  try {
    // Redis 연결 설정
    synchronizer = new StateSynchronizer({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      lazyConnect: true
    });

    // 1. 기본 상태 동기화 테스트
    console.log('📋 테스트 1: 기본 상태 동기화');
    
    const workflowId = `test-workflow-${Date.now()}`;
    
    // 초기 상태 설정
    await synchronizer.syncState(workflowId, {
      workflowId,
      status: 'running',
      context: { projectId: 'proj-123', userId: 'user-456' },
      tasks: {
        'task-1': {
          taskId: 'task-1',
          status: 'pending'
        }
      }
    });

    const initialState = await synchronizer.getState(workflowId);
    console.log('✅ 초기 상태 설정 완료');
    console.log(`   상태: ${initialState?.status}`);
    console.log(`   버전: ${initialState?.version}`);
    console.log(`   태스크 수: ${Object.keys(initialState?.tasks || {}).length}`);

    // 2. 태스크 상태 업데이트 테스트
    console.log('\n📋 테스트 2: 태스크 상태 업데이트');
    
    await synchronizer.updateTaskState(workflowId, 'task-1', {
      taskId: 'task-1',
      status: 'running',
      startTime: new Date().toISOString()
    });

    await synchronizer.updateTaskState(workflowId, 'task-2', {
      taskId: 'task-2',
      status: 'pending'
    });

    const updatedState = await synchronizer.getState(workflowId);
    console.log('✅ 태스크 상태 업데이트 완료');
    console.log(`   task-1 상태: ${updatedState?.tasks['task-1']?.status}`);
    console.log(`   task-2 상태: ${updatedState?.tasks['task-2']?.status}`);
    console.log(`   버전: ${updatedState?.version}`);

    // 3. 컨텍스트 업데이트 테스트
    console.log('\n📋 테스트 3: 컨텍스트 업데이트');
    
    await synchronizer.updateContext(workflowId, {
      executionStartTime: new Date().toISOString(),
      metadata: {
        source: 'test',
        priority: 'high'
      }
    });

    const contextUpdatedState = await synchronizer.getState(workflowId);
    console.log('✅ 컨텍스트 업데이트 완료');
    console.log(`   실행 시작 시간: ${contextUpdatedState?.context.executionStartTime}`);
    console.log(`   메타데이터: ${JSON.stringify(contextUpdatedState?.context.metadata)}`);
    console.log(`   버전: ${contextUpdatedState?.version}`);

    // 4. 동시 업데이트 테스트 (경합 조건)
    console.log('\n📋 테스트 4: 동시 업데이트 (경합 조건)');
    
    const concurrentWorkflowId = `concurrent-test-${Date.now()}`;
    
    // 초기 상태 설정
    await synchronizer.syncState(concurrentWorkflowId, {
      workflowId: concurrentWorkflowId,
      status: 'running',
      context: { counter: 0 },
      tasks: {}
    });

    // 동시에 여러 업데이트 실행
    const updatePromises = [];
    for (let i = 0; i < 10; i++) {
      updatePromises.push(
        synchronizer.updateContext(concurrentWorkflowId, {
          [`update_${i}`]: `value_${i}`,
          timestamp: new Date().toISOString()
        })
      );
    }

    await Promise.all(updatePromises);

    const concurrentState = await synchronizer.getState(concurrentWorkflowId);
    console.log('✅ 동시 업데이트 완료');
    console.log(`   컨텍스트 키 수: ${Object.keys(concurrentState?.context || {}).length}`);
    console.log(`   최종 버전: ${concurrentState?.version}`);

    // 5. 상태 변경 이벤트 구독 테스트
    console.log('\n📋 테스트 5: 상태 변경 이벤트 구독');
    
    const eventWorkflowId = `event-test-${Date.now()}`;
    let eventReceived = false;

    // 이벤트 리스너 설정
    synchronizer.on('stateChange', (stateChange) => {
      if (stateChange.workflowId === eventWorkflowId) {
        console.log(`✅ 상태 변경 이벤트 수신: ${stateChange.workflowId}`);
        console.log(`   변경 시간: ${stateChange.timestamp}`);
        console.log(`   변경 내용: ${JSON.stringify(stateChange.changes)}`);
        eventReceived = true;
      }
    });

    // 워크플로우 구독
    synchronizer.subscribeToWorkflow(eventWorkflowId);

    // 상태 변경
    await synchronizer.syncState(eventWorkflowId, {
      workflowId: eventWorkflowId,
      status: 'running',
      context: { eventTest: true }
    });

    // 이벤트 수신 대기
    await new Promise(resolve => setTimeout(resolve, 100));

    if (eventReceived) {
      console.log('✅ 이벤트 구독 테스트 성공');
    } else {
      console.log('⚠️ 이벤트가 수신되지 않음');
    }

    // 6. 워크플로우 상태 업데이트 테스트
    console.log('\n📋 테스트 6: 워크플로우 상태 업데이트');
    
    await synchronizer.updateWorkflowStatus(workflowId, 'completed');
    
    const completedState = await synchronizer.getState(workflowId);
    console.log('✅ 워크플로우 상태 업데이트 완료');
    console.log(`   최종 상태: ${completedState?.status}`);
    console.log(`   최종 버전: ${completedState?.version}`);

    // 7. 상태 통계 테스트
    console.log('\n📋 테스트 7: 상태 통계');
    
    const stats = await synchronizer.getStateStats();
    console.log('✅ 상태 통계 조회 완료');
    console.log(`   총 워크플로우 수: ${stats.totalWorkflows}`);
    console.log(`   상태별 개수: ${JSON.stringify(stats.statusCounts)}`);
    console.log(`   평균 태스크 수: ${stats.averageTaskCount.toFixed(1)}`);

    // 8. 활성 워크플로우 목록 테스트
    console.log('\n📋 테스트 8: 활성 워크플로우 목록');
    
    const activeWorkflows = await synchronizer.getActiveWorkflows();
    console.log('✅ 활성 워크플로우 목록 조회 완료');
    console.log(`   활성 워크플로우 수: ${activeWorkflows.length}`);
    console.log(`   워크플로우 ID 예시: ${activeWorkflows.slice(0, 3).join(', ')}`);

    // 9. 상태 병합 테스트
    console.log('\n📋 테스트 9: 복잡한 상태 병합');
    
    const mergeTestId = `merge-test-${Date.now()}`;
    
    // 초기 상태
    await synchronizer.syncState(mergeTestId, {
      workflowId: mergeTestId,
      status: 'running',
      context: {
        config: {
          timeout: 300,
          retries: 3
        },
        metadata: {
          version: '1.0'
        }
      },
      tasks: {
        'task-a': { taskId: 'task-a', status: 'pending' }
      }
    });

    // 부분 업데이트
    await synchronizer.syncState(mergeTestId, {
      context: {
        config: {
          retries: 5  // timeout은 유지되어야 함
        },
        metadata: {
          author: 'test-user'  // version은 유지되어야 함
        },
        newField: 'new-value'
      },
      tasks: {
        'task-b': { taskId: 'task-b', status: 'running' }
      }
    });

    const mergedState = await synchronizer.getState(mergeTestId);
    console.log('✅ 복잡한 상태 병합 완료');
    console.log(`   config.timeout: ${mergedState?.context.config.timeout} (유지됨)`);
    console.log(`   config.retries: ${mergedState?.context.config.retries} (업데이트됨)`);
    console.log(`   metadata.version: ${mergedState?.context.metadata.version} (유지됨)`);
    console.log(`   metadata.author: ${mergedState?.context.metadata.author} (추가됨)`);
    console.log(`   newField: ${mergedState?.context.newField} (추가됨)`);
    console.log(`   태스크 수: ${Object.keys(mergedState?.tasks || {}).length}`);

    // 10. 성능 테스트
    console.log('\n📋 테스트 10: 성능 테스트');
    
    const perfTestIds = [];
    const startTime = Date.now();

    // 100개 워크플로우 동시 생성
    const createPromises = [];
    for (let i = 0; i < 100; i++) {
      const perfId = `perf-test-${Date.now()}-${i}`;
      perfTestIds.push(perfId);
      
      createPromises.push(
        synchronizer.syncState(perfId, {
          workflowId: perfId,
          status: 'running',
          context: { index: i },
          tasks: {
            [`task-${i}`]: { taskId: `task-${i}`, status: 'pending' }
          }
        })
      );
    }

    await Promise.all(createPromises);
    const createTime = Date.now() - startTime;

    console.log(`✅ 100개 워크플로우 생성 완료 (${createTime}ms)`);
    console.log(`   평균 생성 시간: ${(createTime / 100).toFixed(1)}ms`);

    // 정리
    console.log('\n📋 테스트 정리');
    
    const cleanupPromises = [workflowId, concurrentWorkflowId, eventWorkflowId, mergeTestId, ...perfTestIds]
      .map(id => synchronizer.deleteState(id));
    
    await Promise.all(cleanupPromises);
    console.log('✅ 테스트 데이터 정리 완료');

    console.log('\n✅ 상태 동기화 메커니즘 테스트 완료!');

  } catch (error) {
    console.error('❌ 상태 동기화 테스트 실패:', error.message);
    console.error(error.stack);
    process.exit(1);
  } finally {
    if (synchronizer) {
      await synchronizer.cleanup();
    }
  }
}

// 스크립트 직접 실행 시
if (require.main === module) {
  testStateSynchronizer();
}

module.exports = { testStateSynchronizer };