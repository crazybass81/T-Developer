#!/usr/bin/env node

require('ts-node/register');

const { RoutingMonitor } = require('../backend/src/routing/routing-metrics.ts');

async function testRoutingMetrics() {
  console.log('📊 라우팅 성능 모니터링 테스트 시작...\n');

  try {
    const monitor = new RoutingMonitor();

    // 1. 기본 메트릭 테스트
    console.log('📈 기본 메트릭 수집 테스트:');
    
    // 초기 메트릭 확인
    let metrics = monitor.getMetrics();
    console.log(`✅ 초기 상태 - 총 요청: ${metrics.totalRequests}, 에러율: ${(metrics.errorRate * 100).toFixed(2)}%`);

    // 2. 요청 기록 시뮬레이션
    console.log('\n🔄 요청 기록 시뮬레이션:');
    
    const agents = ['nl-agent', 'code-agent', 'ui-agent'];
    const requests = [];

    // 100개 요청 시뮬레이션
    for (let i = 0; i < 100; i++) {
      const agentId = agents[i % agents.length];
      const latency = Math.random() * 500 + 50; // 50-550ms
      const success = Math.random() > 0.1; // 90% 성공률
      
      monitor.recordRequest(agentId, latency, success);
      requests.push({ agentId, latency, success });
    }

    console.log(`✅ 100개 요청 기록 완료`);

    // 큐 깊이 업데이트
    monitor.updateQueueDepth(25);

    // 3. 메트릭 수집 및 분석
    console.log('\n📊 메트릭 수집 및 분석:');
    
    metrics = await monitor.collectMetrics();
    
    console.log(`   - 총 요청 수: ${metrics.totalRequests}`);
    console.log(`   - 에러율: ${(metrics.errorRate * 100).toFixed(2)}%`);
    console.log(`   - 큐 깊이: ${metrics.queueDepth}`);
    
    if (metrics.routingLatency.length > 0) {
      console.log(`   - P50 지연시간: ${metrics.routingLatency[50]?.toFixed(2)}ms`);
      console.log(`   - P95 지연시간: ${metrics.routingLatency[95]?.toFixed(2)}ms`);
      console.log(`   - P99 지연시간: ${metrics.routingLatency[99]?.toFixed(2)}ms`);
    }

    // 4. 에이전트 활용률 분석
    console.log('\n🤖 에이전트 활용률 분석:');
    
    const agentStats = monitor.getAgentStats();
    for (const [agentId, stats] of Object.entries(agentStats)) {
      console.log(`   - ${agentId}:`);
      console.log(`     * 요청 수: ${stats.requests}`);
      console.log(`     * 평균 응답시간: ${stats.avgResponseTime.toFixed(2)}ms`);
      console.log(`     * 에러율: ${(stats.errorRate * 100).toFixed(2)}%`);
    }

    for (const [agentId, utilization] of metrics.agentUtilization) {
      console.log(`   - ${agentId} 활용률: ${(utilization * 100).toFixed(2)}%`);
    }

    // 5. 이상 상황 시뮬레이션
    console.log('\n🚨 이상 상황 시뮬레이션:');
    
    // 높은 지연시간 시뮬레이션
    for (let i = 0; i < 10; i++) {
      monitor.recordRequest('slow-agent', 1500, true); // 1.5초 지연
    }

    // 높은 에러율 시뮬레이션
    for (let i = 0; i < 20; i++) {
      monitor.recordRequest('error-agent', 200, false); // 모두 실패
    }

    // 높은 큐 깊이 시뮬레이션
    monitor.updateQueueDepth(150);

    // 메트릭 재수집
    await monitor.collectMetrics();

    // 6. 알림 확인
    console.log('\n🔔 생성된 알림:');
    
    const alerts = monitor.getAlerts();
    if (alerts.length > 0) {
      alerts.forEach((alert, index) => {
        console.log(`   ${index + 1}. ${alert.type}: ${alert.message}`);
        console.log(`      데이터: ${JSON.stringify(alert.data)}`);
      });
    } else {
      console.log('   알림 없음');
    }

    // 7. 메트릭 히스토리 확인
    console.log('\n📈 메트릭 히스토리:');
    
    const history = monitor.getMetricsHistory();
    console.log(`   - 수집된 메트릭 스냅샷: ${history.length}개`);
    
    if (history.length > 0) {
      const latest = history[history.length - 1];
      const first = history[0];
      
      console.log(`   - 첫 번째 스냅샷: 요청 ${first.totalRequests}개, 에러율 ${(first.errorRate * 100).toFixed(2)}%`);
      console.log(`   - 최신 스냅샷: 요청 ${latest.totalRequests}개, 에러율 ${(latest.errorRate * 100).toFixed(2)}%`);
    }

    // 8. 성능 테스트
    console.log('\n⚡ 성능 테스트:');
    
    const startTime = Date.now();
    
    // 1000개 요청 빠르게 기록
    for (let i = 0; i < 1000; i++) {
      const agentId = agents[i % agents.length];
      const latency = Math.random() * 100 + 10;
      const success = Math.random() > 0.05;
      
      monitor.recordRequest(agentId, latency, success);
    }
    
    const recordTime = Date.now() - startTime;
    console.log(`✅ 1000개 요청 기록 시간: ${recordTime}ms`);

    const collectStart = Date.now();
    await monitor.collectMetrics();
    const collectTime = Date.now() - collectStart;
    console.log(`✅ 메트릭 수집 시간: ${collectTime}ms`);

    console.log('\n✅ 라우팅 성능 모니터링 테스트 완료!');

  } catch (error) {
    console.error('❌ 라우팅 성능 모니터링 테스트 실패:', error.message);
    process.exit(1);
  }
}

// 스크립트 직접 실행 시
if (require.main === module) {
  testRoutingMetrics();
}

module.exports = { testRoutingMetrics };