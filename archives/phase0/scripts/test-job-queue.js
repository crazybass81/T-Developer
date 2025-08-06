const { QueueManager, JobType } = require('../backend/src/performance/job-queue');

async function testJobQueue() {
  console.log('🔄 Testing Job Queue System...');
  
  const queueManager = new QueueManager();
  
  try {
    // 큐 초기화
    await queueManager.initialize();
    console.log('✅ Queue manager initialized');
    
    // 작업 추가
    const job = await queueManager.addJob('main', 'test-job', {
      type: JobType.AGENT_EXECUTION,
      timestamp: Date.now(),
      agentName: 'test-agent',
      input: { test: 'data' }
    });
    
    console.log(`✅ Job added with ID: ${job.id}`);
    
    // 작업 상태 확인
    const status = await queueManager.getJobStatus('main', job.id.toString());
    console.log('✅ Job status:', status);
    
    // 큐 통계
    const stats = await queueManager.getQueueStats('main');
    console.log('✅ Queue stats:', stats);
    
    console.log('✅ All job queue tests passed!');
    
  } catch (error) {
    console.error('❌ Job queue test failed:', error);
  } finally {
    await queueManager.shutdown();
  }
}

testJobQueue();