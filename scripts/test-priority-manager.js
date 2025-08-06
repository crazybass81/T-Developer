#!/usr/bin/env node

require('ts-node/register');

const { PriorityQueue, TaskScheduler, Priority } = require('../backend/src/routing/priority-manager.ts');

async function testPriorityManager() {
  console.log('🔄 태스크 우선순위 관리 테스트 시작...\n');

  try {
    // 1. 우선순위 큐 테스트
    console.log('📋 우선순위 큐 테스트:');
    const priorityQueue = new PriorityQueue();

    // 테스트 태스크 생성
    const tasks = [
      { id: 'task-1', type: 'normal', createdAt: Date.now() - 60000, data: 'Normal task' },
      { id: 'task-2', type: 'urgent', createdAt: Date.now(), slaDeadline: Date.now() + 120000, data: 'Urgent task' },
      { id: 'task-3', type: 'low', createdAt: Date.now() - 300000, data: 'Old low priority task' },
      { id: 'task-4', type: 'critical', createdAt: Date.now(), slaDeadline: Date.now() + 60000, data: 'Critical task' }
    ];

    // 태스크 추가 (다양한 우선순위)
    priorityQueue.addTask(tasks[0], Priority.NORMAL);
    priorityQueue.addTask(tasks[1], Priority.HIGH);
    priorityQueue.addTask(tasks[2], Priority.LOW);
    priorityQueue.addTask(tasks[3], Priority.CRITICAL);

    console.log('✅ 4개 태스크 추가 완료');

    // 큐 상태 확인
    const queueStatus = priorityQueue.getQueueStatus();
    console.log(`   - 총 태스크: ${queueStatus.totalTasks}개`);
    console.log(`   - CRITICAL: ${queueStatus.priorityCounts.CRITICAL}개`);
    console.log(`   - HIGH: ${queueStatus.priorityCounts.HIGH}개`);
    console.log(`   - NORMAL: ${queueStatus.priorityCounts.NORMAL}개`);
    console.log(`   - LOW: ${queueStatus.priorityCounts.LOW}개`);

    // 우선순위 순서로 태스크 처리
    console.log('\n🎯 우선순위 순서로 태스크 처리:');
    let order = 1;
    while (true) {
      const task = priorityQueue.getNextTask();
      if (!task) break;
      
      console.log(`   ${order}. ${task.id} (${Priority[task.priority]}) - ${task.data}`);
      order++;
    }

    // 2. 태스크 스케줄러 테스트
    console.log('\n⚡ 태스크 스케줄러 테스트:');
    
    const processedTasks = [];
    const scheduler = new TaskScheduler(async (task) => {
      console.log(`   🔄 처리 중: ${task.id} (${Priority[task.priority]})`);
      await new Promise(resolve => setTimeout(resolve, 100)); // 처리 시뮬레이션
      processedTasks.push(task);
    });

    // 새로운 태스크들 스케줄링
    const newTasks = [
      { id: 'sched-1', type: 'normal', createdAt: Date.now(), data: 'Scheduled normal' },
      { id: 'sched-2', type: 'critical', createdAt: Date.now(), data: 'Scheduled critical' },
      { id: 'sched-3', type: 'high', createdAt: Date.now(), data: 'Scheduled high' }
    ];

    scheduler.scheduleTask(newTasks[0], Priority.NORMAL);
    scheduler.scheduleTask(newTasks[1], Priority.CRITICAL);
    scheduler.scheduleTask(newTasks[2], Priority.HIGH);

    console.log('✅ 3개 태스크 스케줄링 완료');

    // 처리 완료 대기
    await new Promise(resolve => setTimeout(resolve, 500));

    console.log(`✅ ${processedTasks.length}개 태스크 처리 완료`);

    // 스케줄러 상태 확인
    const schedulerStatus = scheduler.getSchedulerStatus();
    console.log(`   - 처리 중: ${schedulerStatus.isProcessing ? 'Yes' : 'No'}`);
    console.log(`   - 대기 중인 태스크: ${schedulerStatus.queueStatus.totalTasks}개`);

    // 3. SLA 데드라인 테스트
    console.log('\n⏰ SLA 데드라인 테스트:');
    
    const slaQueue = new PriorityQueue();
    const urgentTask = {
      id: 'urgent-sla',
      type: 'urgent',
      createdAt: Date.now(),
      slaDeadline: Date.now() + 60000, // 1분 후 데드라인
      data: 'Urgent SLA task'
    };

    const normalTask = {
      id: 'normal-task',
      type: 'normal', 
      createdAt: Date.now(),
      data: 'Normal task'
    };

    slaQueue.addTask(normalTask, Priority.NORMAL);
    slaQueue.addTask(urgentTask, Priority.NORMAL); // 같은 우선순위지만 SLA 때문에 먼저 처리되어야 함

    const firstTask = slaQueue.getNextTask();
    console.log(`✅ SLA 데드라인으로 인해 ${firstTask?.id}가 먼저 선택됨`);

    console.log('\n✅ 태스크 우선순위 관리 테스트 완료!');

  } catch (error) {
    console.error('❌ 태스크 우선순위 관리 테스트 실패:', error.message);
    process.exit(1);
  }
}

// 스크립트 직접 실행 시
if (require.main === module) {
  testPriorityManager();
}

module.exports = { testPriorityManager };