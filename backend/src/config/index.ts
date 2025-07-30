// Phase 1 핵심 설정
export const config = {
  // Agent Squad 설정 (직접 구현)
  agentSquad: {
    maxConcurrentAgents: 50,
    timeout: 300000,
    storage: 'dynamodb'
  },
  
  // Agno Framework 설정
  agno: {
    instantiationTargetUs: 3,
    memoryTargetKb: 6.5,
    enableOptimizations: true
  },
  
  // AWS 설정
  aws: {
    region: process.env.AWS_REGION || 'us-east-1',
    bedrock: {
      region: process.env.AWS_BEDROCK_REGION || 'us-east-1'
    }
  },
  
  // DynamoDB 설정
  dynamodb: {
    tableName: 'T-Developer-Main',
    endpoint: process.env.DYNAMODB_ENDPOINT
  },
  
  // Redis 설정
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379')
  }
};

// Agent Squad 대체 구현 사용
export { AgentSquad, SupervisorAgent } from '../orchestration/agent-squad';