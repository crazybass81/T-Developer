#!/usr/bin/env node

// TypeScript 파일을 직접 require하기 위한 설정
require('ts-node/register');

const { LoadBalancer } = require('../backend/src/routing/load-balancer.ts');

async function testLoadBalancer() {
  console.log('🔄 로드 밸런서 테스트 시작...\n');

  try {
    // 1. 로드 밸런서 생성
    const loadBalancer = new LoadBalancer('resource-based');
    console.log('✅ 로드 밸런서 생성 완료');

    // 2. 테스트 에이전트 등록
    const testAgents = [
      { agentId: 'agent-1', currentTasks: 2, cpuUsage: 0.3, memoryUsage: 0.4, avgResponseTime: 150, capacity: 10 },
      { agentId: 'agent-2', currentTasks: 5, cpuUsage: 0.7, memoryUsage: 0.6, avgResponseTime: 300, capacity: 10 },
      { agentId: 'agent-3', currentTasks: 1, cpuUsage: 0.2, memoryUsage: 0.3, avgResponseTime: 100, capacity: 8 }
    ];

    testAgents.forEach(agent => {
      loadBalancer.updateAgentLoad(agent.agentId, agent);
    });
    console.log('✅ 테스트 에이전트 3개 등록 완료');

    // 3. 사용 가능한 에이전트 조회
    const availableAgents = await loadBalancer.getAvailableAgents();
    console.log(`✅ 사용 가능한 에이전트: ${availableAgents.length}개`);
    console.log(`   - ${availableAgents.join(', ')}`);

    // 4. 메트릭 확인
    const metrics = loadBalancer.getMetrics();
    console.log('\n📈 로드 밸런서 메트릭:');
    console.log(`   - 총 에이전트: ${metrics.totalAgents}개`);
    console.log(`   - 총 태스크: ${metrics.totalTasks}개`);
    console.log(`   - 평균 CPU 사용률: ${(metrics.avgCpuUsage * 100).toFixed(1)}%`);

    // 5. 다른 전략 테스트
    console.log('\n🔄 다른 로드 밸런싱 전략 테스트:');
    
    const strategies = ['least-connections', 'weighted-round-robin', 'resource-based'];
    
    for (const strategy of strategies) {
      const lb = new LoadBalancer(strategy);
      testAgents.forEach(agent => lb.updateAgentLoad(agent.agentId, agent));
      
      const agents = await lb.getAvailableAgents();
      console.log(`   - ${strategy}: ${agents[0]} (첫 번째 선택)`);
    }

    console.log('\n✅ 로드 밸런서 테스트 완료!');

  } catch (error) {
    console.error('❌ 로드 밸런서 테스트 실패:', error.message);
    process.exit(1);
  }
}

// 스크립트 직접 실행 시
if (require.main === module) {
  testLoadBalancer();
}

module.exports = { testLoadBalancer };