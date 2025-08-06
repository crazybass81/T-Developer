export const agentSquadConfig = {
  orchestrator: {
    maxConcurrentAgents: 50,
    timeout: 300000, // 5분
    retryPolicy: {
      maxAttempts: 3,
      backoffMultiplier: 2
    }
  },
  monitoring: {
    enabled: true,
    metricsEndpoint: '/metrics',
    healthCheckInterval: 30000
  },
  storage: {
    type: 'dynamodb',
    region: process.env.AWS_REGION,
    tableName: 't-developer-agents'
  }
};