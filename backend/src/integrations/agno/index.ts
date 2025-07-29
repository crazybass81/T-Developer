export { 
  AgnoMonitoringClient, 
  AgnoConfig, 
  AgnoMetric, 
  AgnoEvent, 
  AgnoTrace,
  AgnoTrace as AgnoTraceDecorator
} from './monitoring-config';

export { 
  AgnoMonitoredAgent, 
  AgnoNLInputAgent 
} from './agno-agent';

// Configuration helpers
export function createAgnoConfig(
  apiKey: string,
  projectId: string,
  environment: string = 'development',
  endpoint: string = 'https://api.agno.com'
): AgnoConfig {
  return {
    apiKey,
    endpoint,
    projectId,
    environment,
    batchSize: 50,
    flushInterval: 5000 // 5 seconds for development
  };
}

// Environment-based configuration
export function getAgnoConfigFromEnv(): AgnoConfig {
  const apiKey = process.env.AGNO_API_KEY;
  const projectId = process.env.AGNO_PROJECT_ID;
  const environment = process.env.NODE_ENV || 'development';
  const endpoint = process.env.AGNO_ENDPOINT || 'https://api.agno.com';
  
  if (!apiKey || !projectId) {
    throw new Error('Agno configuration missing. Set AGNO_API_KEY and AGNO_PROJECT_ID');
  }
  
  return createAgnoConfig(apiKey, projectId, environment, endpoint);
}

// Global monitoring instance
let globalAgnoClient: AgnoMonitoringClient | null = null;

export function initializeGlobalAgnoMonitoring(config?: AgnoConfig): AgnoMonitoringClient {
  if (!globalAgnoClient) {
    const agnoConfig = config || getAgnoConfigFromEnv();
    globalAgnoClient = new AgnoMonitoringClient(agnoConfig);
    console.log('🔍 Agno monitoring initialized');
  }
  
  return globalAgnoClient;
}

export function getGlobalAgnoClient(): AgnoMonitoringClient | null {
  return globalAgnoClient;
}