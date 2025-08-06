import axios from 'axios';

interface AgnoMetrics {
  instantiation_time_us: number;
  memory_per_agent_kb: number;
  active_agents: number;
  total_agents: number;
  error_count: number;
  success_rate: number;
}

interface PrometheusMetrics {
  instantiation_time: any;
  memory_usage: any;
  active_agents: any;
  error_rate: any;
}

class AgnoMonitoringIntegration {
  private agnoApiKey: string;
  private projectId: string;
  private environment: string;
  private metricsBuffer: AgnoMetrics[] = [];
  private flushInterval: NodeJS.Timer;

  constructor() {
    this.agnoApiKey = process.env.AGNO_API_KEY || '';
    this.projectId = process.env.AGNO_PROJECT_ID || 't-developer';
    this.environment = process.env.NODE_ENV || 'development';
    
    // Start periodic flush
    this.flushInterval = setInterval(() => {
      this.flushMetrics();
    }, 30000); // 30 seconds
  }

  setupPrometheusMetrics(): PrometheusMetrics {
    // Mock Prometheus metrics for now
    return {
      instantiation_time: {
        observe: (value: number) => {
          console.log(`Prometheus: instantiation_time observed: ${value}s`);
        }
      },
      memory_usage: {
        set: (value: number) => {
          console.log(`Prometheus: memory_usage set: ${value} bytes`);
        }
      },
      active_agents: {
        set: (value: number) => {
          console.log(`Prometheus: active_agents set: ${value}`);
        }
      },
      error_rate: {
        inc: (labels: any) => {
          console.log(`Prometheus: error_rate incremented:`, labels);
        }
      }
    };
  }

  async collectMetrics(agentPool: any): Promise<AgnoMetrics> {
    const stats = agentPool.getStats();
    const start = performance.now();
    
    // Simulate agent creation for timing
    const mockAgent = { id: 'test', created: Date.now() };
    const instantiation_time = performance.now() - start;

    const metrics: AgnoMetrics = {
      instantiation_time_us: instantiation_time * 1000, // Convert to microseconds
      memory_per_agent_kb: 6.5, // Mock value
      active_agents: stats.inUse,
      total_agents: stats.total,
      error_count: 0,
      success_rate: 1.0
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

  async sendToAgnoDashboard(metrics: AgnoMetrics): Promise<void> {
    if (!this.agnoApiKey) {
      console.log('📊 Agno API key not configured, skipping dashboard upload');
      return;
    }

    try {
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

      // Mock API call to agno.com
      console.log('📤 Sending metrics to Agno dashboard:', {
        project: this.projectId,
        environment: this.environment,
        metrics: {
          instantiation_time: `${metrics.instantiation_time_us}μs`,
          memory_per_agent: `${metrics.memory_per_agent_kb}KB`,
          active_agents: metrics.active_agents,
          success_rate: `${(metrics.success_rate * 100).toFixed(1)}%`
        }
      });

      // In real implementation, would make HTTP request:
      // await axios.post('https://agno.com/api/metrics', payload, {
      //   headers: { 'Authorization': `Bearer ${this.agnoApiKey}` }
      // });

    } catch (error) {
      console.error('❌ Failed to send metrics to Agno dashboard:', error);
    }
  }

  private async flushMetrics(): Promise<void> {
    if (this.metricsBuffer.length === 0) return;

    const batchMetrics = this.metricsBuffer.splice(0);
    
    // Calculate aggregated metrics
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

  async recordAgentEvent(eventType: string, agentId: string, metadata?: any): Promise<void> {
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

  destroy(): void {
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
    }
    
    // Flush remaining metrics
    this.flushMetrics();
  }
}

export { AgnoMonitoringIntegration, AgnoMetrics };