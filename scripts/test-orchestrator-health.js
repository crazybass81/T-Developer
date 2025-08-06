#!/usr/bin/env node

const { OrchestratorHealthCheck } = require('../backend/src/monitoring/orchestrator-health-check');
const { MetricsCollector } = require('../backend/src/monitoring/metrics-collector');

// Mock orchestrator for testing
const mockOrchestrator = {
  agent_registry: {
    listAgents: () => [
      { name: 'nl-input-agent', status: 'active' },
      { name: 'ui-selection-agent', status: 'active' },
      { name: 'parser-agent', status: 'idle' }
    ],
    getAgent: async (name) => ({ name, ping: () => 'pong' })
  },
  task_queue: { size: 5 },
  completed_count: 42,
  failed_count: 3
};

async function testHealthCheck() {
  console.log('🔍 Testing Orchestrator Health Check System...\n');

  try {
    // Test 1: Health Check Creation
    console.log('1. Creating health checker...');
    const healthChecker = new OrchestratorHealthCheck(mockOrchestrator);
    console.log('✅ Health checker created successfully');

    // Test 2: Metrics Collection
    console.log('\n2. Collecting metrics...');
    const metrics = await healthChecker.collectMetrics();
    console.log('✅ Metrics collected:', {
      active_agents: metrics.active_agents,
      queued_tasks: metrics.queued_tasks,
      completed_tasks: metrics.completed_tasks,
      memory_usage: `${metrics.memory_usage}MB`,
      uptime: `${metrics.uptime}s`
    });

    // Test 3: Agent Health Check
    console.log('\n3. Checking agent health...');
    const agentHealth = await healthChecker.checkAgentHealth();
    console.log('✅ Agent health checked:', agentHealth.map(a => ({
      name: a.name,
      status: a.status,
      response_time: a.response_time ? `${a.response_time}ms` : 'N/A'
    })));

    // Test 4: Overall Health Check
    console.log('\n4. Performing overall health check...');
    const overallHealth = await healthChecker.checkHealth();
    console.log('✅ Overall health:', {
      status: overallHealth.status,
      agent_count: overallHealth.agents.length,
      healthy_agents: overallHealth.agents.filter(a => a.status === 'healthy').length
    });

    // Test 5: Response Time Recording
    console.log('\n5. Testing response time recording...');
    healthChecker.recordResponseTime(150);
    healthChecker.recordResponseTime(200);
    healthChecker.recordResponseTime(180);
    
    const updatedMetrics = await healthChecker.collectMetrics();
    console.log('✅ Response time recorded, avg:', `${updatedMetrics.avg_response_time}ms`);

    // Test 6: Metrics Collector
    console.log('\n6. Testing metrics collector...');
    const metricsCollector = new MetricsCollector();
    
    // Simulate some activity
    metricsCollector.recordRequest();
    metricsCollector.recordRequest();
    metricsCollector.recordError();
    
    // Get Prometheus metrics
    const prometheusMetrics = metricsCollector.exportPrometheusMetrics();
    console.log('✅ Prometheus metrics generated:', prometheusMetrics ? 'Yes' : 'No');

    console.log('\n🎉 All health check tests passed!');
    
    return true;

  } catch (error) {
    console.error('❌ Health check test failed:', error.message);
    return false;
  }
}

// Run tests
if (require.main === module) {
  testHealthCheck()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('Test execution failed:', error);
      process.exit(1);
    });
}

module.exports = { testHealthCheck };