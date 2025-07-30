export interface AgnoConfig {
  performance: {
    instantiationTargetUs: number;
    memoryTargetKb: number;
    enableOptimizations: boolean;
    useNativeExtensions: boolean;
  };
  monitoring: {
    enabled: boolean;
    endpoint?: string;
    apiKey?: string;
    metricsInterval: number;
    customMetrics: string[];
  };
  resources: {
    maxAgents: number;
    maxMemoryPerAgentKb: number;
    agentTimeoutSeconds: number;
  };
}

export const agnoConfig: AgnoConfig = {
  performance: {
    instantiationTargetUs: 3, // 3μs 목표
    memoryTargetKb: 6.5,      // 6.5KB 목표
    enableOptimizations: true,
    useNativeExtensions: true
  },
  
  monitoring: {
    enabled: process.env.AGNO_MONITORING === 'true',
    endpoint: process.env.AGNO_MONITORING_URL,
    apiKey: process.env.AGNO_API_KEY,
    metricsInterval: 30000, // 30초
    customMetrics: [
      'agent_instantiation_time',
      'memory_usage_per_agent',
      'total_active_agents'
    ]
  },
  
  resources: {
    maxAgents: parseInt(process.env.MAX_AGENTS || '1000'),
    maxMemoryPerAgentKb: 10,
    agentTimeoutSeconds: 300
  }
};