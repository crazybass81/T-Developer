import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3000'),
  nodeEnv: process.env.NODE_ENV || 'development',
  
  // AWS Configuration
  aws: {
    region: process.env.AWS_REGION || 'us-east-1',
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    bedrockRegion: process.env.AWS_BEDROCK_REGION || 'us-east-1'
  },

  // AI Models
  openai: {
    apiKey: process.env.OPENAI_API_KEY
  },
  anthropic: {
    apiKey: process.env.ANTHROPIC_API_KEY
  },

  // Bedrock AgentCore
  bedrock: {
    runtimeId: process.env.BEDROCK_AGENTCORE_RUNTIME_ID,
    gatewayUrl: process.env.BEDROCK_AGENTCORE_GATEWAY_URL
  },

  // Agent Squad (Open Source)
  agentSquad: {
    storage: process.env.AGENT_SQUAD_STORAGE || 'memory',
    timeout: parseInt(process.env.AGENT_SQUAD_TIMEOUT || '300')
  },

  // Agno Framework (Open Source)
  agno: {
    monitoringUrl: process.env.AGNO_MONITORING_URL,
    enableMonitoring: process.env.ENABLE_AGNO_MONITORING === 'true'
  },

  // Database
  dynamodb: {
    endpoint: process.env.DYNAMODB_ENDPOINT,
    region: process.env.DYNAMODB_REGION || 'us-east-1'
  },

  // Redis
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD
  },

  // Security
  jwt: {
    secret: process.env.JWT_SECRET || 'dev-secret'
  },

  // Feature Flags
  features: {
    enableCache: process.env.ENABLE_CACHE === 'true',
    enableTelemetry: process.env.ENABLE_TELEMETRY === 'true',
    maxConcurrentAgents: parseInt(process.env.MAX_CONCURRENT_AGENTS || '50')
  }
};