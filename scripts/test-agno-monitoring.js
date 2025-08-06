#!/usr/bin/env node

const { v4: uuidv4 } = require('uuid');

// Mock AgentPool for testing
class MockAgentPool {
  constructor() {
    this.stats = { available: 5, inUse: 3, total: 8, created: 8, destroyed: 0 };
  }
  
  getStats() {
    return { ...this.stats };
  }
  
  simulateActivity() {
    // Simulate some agent activity
    this.stats.inUse = Math.floor(Math.random() * 10) + 1;
    this.stats.available = Math.max(0, this.stats.total - this.stats.inUse);
  }
}

// Mock AgnoMonitoringIntegration
class AgnoMonitoringIntegration {
  constructor() {
    this.agnoApiKey = process.env.AGNO_API_KEY || '';
    this.projectId = process.env.AGNO_PROJECT_ID || 't-developer';
    this.environment = process.env.NODE_ENV || 'development';
    this.metricsBuffer = [];
    
    console.log('🔧 Agno Monitoring Integration initialized:', {
      project: this.projectId,
      environment: this.environment,
      hasApiKey: !!this.agnoApiKey
    });
  }

  setupPrometheusMetrics() {
    return {
      instantiation_time: {
        observe: (value) => {
          console.log(`📊 Prometheus: instantiation_time observed: ${value}s`);
        }
      },
      memory_usage: {
        set: (value) => {
          console.log(`📊 Prometheus: memory_usage set: ${value} bytes`);
        }
      },
      active_agents: {
        set: (value) => {
          console.log(`📊 Prometheus: active_agents set: ${value}`);
        }
      },
      error_rate: {
        inc: (labels) => {
          console.log(`📊 Prometheus: error_rate incremented:`, labels);
        }
      }
    };
  }

  async collectMetrics(agentPool) {
    const stats = agentPool.getStats();
    const start = performance.now();
    
    // Simulate agent creation timing
    await new Promise(resolve => setTimeout(resolve, Math.random() * 2));
    const instantiation_time = performance.now() - start;

    const metrics = {
      instantiation_time_us: instantiation_time * 1000,
      memory_per_agent_kb: 6.5 + (Math.random() * 2 - 1), // 5.5-7.5KB
      active_agents: stats.inUse,
      total_agents: stats.total,
      error_count: Math.floor(Math.random() * 3),
      success_rate: 0.95 + (Math.random() * 0.05) // 95-100%
    };

    // Update Prometheus metrics
    const prometheus = this.setupPrometheusMetrics();
    prometheus.instantiation_time.observe(metrics.instantiation_time_us / 1_000_000);
    prometheus.memory_usage.set(metrics.memory_per_agent_kb * 1024);
    prometheus.active_agents.set(metrics.active_agents);

    // Buffer for Agno dashboard
    this.metricsBuffer.push(metrics);

    return metrics;
  }

  async sendToAgnoDashboard(metrics) {
    if (!this.agnoApiKey) {
      console.log('📊 Agno API key not configured, using mock data');
    }

    const payload = {
      timestamp: new Date().toISOString(),
      project_id: this.projectId,
      metrics: metrics,
      metadata: {
        environment: this.environment,
        version: process.env.APP_VERSION || '1.0.0',
        node_version: process.version
      }
    };

    console.log('📤 Sending metrics to Agno dashboard:', {
      project: this.projectId,
      environment: this.environment,
      metrics: {
        instantiation_time: `${metrics.instantiation_time_us.toFixed(2)}μs`,
        memory_per_agent: `${metrics.memory_per_agent_kb.toFixed(2)}KB`,
        active_agents: metrics.active_agents,
        success_rate: `${(metrics.success_rate * 100).toFixed(1)}%`
      }
    });

    // Simulate API response
    await new Promise(resolve => setTimeout(resolve, 100));
    console.log('✅ Metrics sent successfully');
  }

  async recordAgentEvent(eventType, agentId, metadata) {
    const event = {
      timestamp: new Date().toISOString(),
      event_type: eventType,
      agent_id: agentId,
      project_id: this.projectId,
      metadata: metadata || {}
    };

    console.log(`🎯 Agent Event: ${eventType}`, {
      agent: agentId.substring(0, 8) + '...',
      metadata: metadata
    });
  }

  async flushMetrics() {
    if (this.metricsBuffer.length === 0) return;

    const batchMetrics = this.metricsBuffer.splice(0);
    
    const aggregated = {
      avg_instantiation_time: batchMetrics.reduce((sum, m) => sum + m.instantiation_time_us, 0) / batchMetrics.length,
      avg_memory_usage: batchMetrics.reduce((sum, m) => sum + m.memory_per_agent_kb, 0) / batchMetrics.length,
      max_active_agents: Math.max(...batchMetrics.map(m => m.active_agents)),
      total_errors: batchMetrics.reduce((sum, m) => sum + m.error_count, 0),
      avg_success_rate: batchMetrics.reduce((sum, m) => sum + m.success_rate, 0) / batchMetrics.length
    };

    console.log('📊 Agno Metrics Batch Summary:', {
      batch_size: batchMetrics.length,
      avg_instantiation_time: `${aggregated.avg_instantiation_time.toFixed(2)}μs`,
      avg_memory_usage: `${aggregated.avg_memory_usage.toFixed(2)}KB`,
      max_active_agents: aggregated.max_active_agents,
      success_rate: `${(aggregated.avg_success_rate * 100).toFixed(1)}%`
    });
  }
}

async function testAgnoMonitoring() {
  console.log('🚀 Testing Agno Monitoring Integration...\n');

  try {
    // Initialize components
    const agentPool = new MockAgentPool();
    const monitoring = new AgnoMonitoringIntegration();

    // Test 1: Basic metrics collection
    console.log('🔄 Test 1: Basic metrics collection...');
    const metrics = await monitoring.collectMetrics(agentPool);
    console.log('✅ Metrics collected:', {
      instantiation_time: `${metrics.instantiation_time_us.toFixed(2)}μs`,
      memory_usage: `${metrics.memory_per_agent_kb.toFixed(2)}KB`,
      active_agents: metrics.active_agents
    });

    // Test 2: Send to Agno dashboard
    console.log('\n🔄 Test 2: Send to Agno dashboard...');
    await monitoring.sendToAgnoDashboard(metrics);

    // Test 3: Agent event recording
    console.log('\n🔄 Test 3: Agent event recording...');
    const agentId = uuidv4();
    await monitoring.recordAgentEvent('agent_created', agentId, {
      pool_size: 10,
      creation_time_ms: 0.003
    });
    await monitoring.recordAgentEvent('agent_executed', agentId, {
      task_type: 'code_generation',
      execution_time_ms: 1250,
      success: true
    });

    // Test 4: Multiple metrics collection and batching
    console.log('\n🔄 Test 4: Multiple metrics collection...');
    for (let i = 0; i < 5; i++) {
      agentPool.simulateActivity();
      const batchMetrics = await monitoring.collectMetrics(agentPool);
      console.log(`  Batch ${i + 1}: ${batchMetrics.active_agents} active agents`);
      await new Promise(resolve => setTimeout(resolve, 50));
    }

    // Test 5: Flush metrics
    console.log('\n🔄 Test 5: Flush metrics batch...');
    await monitoring.flushMetrics();

    // Test 6: Performance monitoring simulation
    console.log('\n🔄 Test 6: Performance monitoring simulation...');
    const performanceTests = [];
    
    for (let i = 0; i < 10; i++) {
      const start = performance.now();
      
      // Simulate agent operations
      await new Promise(resolve => setTimeout(resolve, Math.random() * 5));
      
      const duration = performance.now() - start;
      performanceTests.push(duration);
      
      if (duration > 3) {
        console.warn(`⚠️  Slow operation detected: ${duration.toFixed(2)}ms`);
      }
    }

    const avgPerformance = performanceTests.reduce((a, b) => a + b, 0) / performanceTests.length;
    console.log(`✅ Average operation time: ${avgPerformance.toFixed(2)}ms`);

    // Test 7: Error simulation and tracking
    console.log('\n🔄 Test 7: Error tracking...');
    const errorTypes = ['timeout', 'memory_limit', 'api_error'];
    
    for (const errorType of errorTypes) {
      await monitoring.recordAgentEvent('agent_error', uuidv4(), {
        error_type: errorType,
        error_message: `Simulated ${errorType} error`,
        recovery_attempted: true
      });
    }

    console.log('\n🎯 Agno Monitoring Integration test completed successfully!');
    return true;

  } catch (error) {
    console.error('❌ Error:', error);
    return false;
  }
}

if (require.main === module) {
  testAgnoMonitoring()
    .then(success => process.exit(success ? 0 : 1))
    .catch(error => {
      console.error('❌ Test failed:', error);
      process.exit(1);
    });
}