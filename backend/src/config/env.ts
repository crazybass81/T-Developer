import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../../../.env') });

export const env = {
  // Node Environment
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: parseInt(process.env.PORT || '3000'),
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',

  // AWS Configuration
  AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY,
  AWS_REGION: process.env.AWS_REGION || 'us-east-1',
  AWS_BEDROCK_REGION: process.env.AWS_BEDROCK_REGION || 'us-east-1',

  // AI Model API Keys
  OPENAI_API_KEY: process.env.OPENAI_API_KEY,
  ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,

  // Bedrock AgentCore
  BEDROCK_AGENTCORE_RUNTIME_ID: process.env.BEDROCK_AGENTCORE_RUNTIME_ID,
  BEDROCK_AGENTCORE_GATEWAY_URL: process.env.BEDROCK_AGENTCORE_GATEWAY_URL,

  // Agent Squad
  AGENT_SQUAD_STORAGE: process.env.AGENT_SQUAD_STORAGE || 'memory',
  AGENT_SQUAD_TIMEOUT: parseInt(process.env.AGENT_SQUAD_TIMEOUT || '300'),

  // Database
  DYNAMODB_ENDPOINT: process.env.DYNAMODB_ENDPOINT,
  DYNAMODB_REGION: process.env.DYNAMODB_REGION || 'us-east-1',

  // S3
  S3_ARTIFACTS_BUCKET: process.env.S3_ARTIFACTS_BUCKET,
  S3_REGION: process.env.S3_REGION || 'us-east-1',

  // Redis
  REDIS_HOST: process.env.REDIS_HOST || 'localhost',
  REDIS_PORT: parseInt(process.env.REDIS_PORT || '6379'),
  REDIS_PASSWORD: process.env.REDIS_PASSWORD,

  // GitHub
  GITHUB_TOKEN: process.env.GITHUB_TOKEN,
  GITHUB_OWNER: process.env.GITHUB_OWNER,
  GITHUB_REPO: process.env.GITHUB_REPO,

  // Monitoring
  AGNO_MONITORING_URL: process.env.AGNO_MONITORING_URL,
  ENABLE_MONITORING: process.env.ENABLE_MONITORING === 'true',

  // Security
  JWT_SECRET: process.env.JWT_SECRET,
  ENCRYPTION_KEY: process.env.ENCRYPTION_KEY,

  // Performance
  AGNO_MAX_WORKERS: parseInt(process.env.AGNO_MAX_WORKERS || '10'),
  MAX_CONCURRENT_AGENTS: parseInt(process.env.MAX_CONCURRENT_AGENTS || '50'),

  // Development
  USE_MOCKS: process.env.USE_MOCKS === 'true',
  MOCK_BEDROCK: process.env.MOCK_BEDROCK === 'true',
  MOCK_DYNAMODB: process.env.MOCK_DYNAMODB === 'true',
  MOCK_S3: process.env.MOCK_S3 === 'true',
  MOCK_EXTERNAL_APIS: process.env.MOCK_EXTERNAL_APIS === 'true'
};

// Validation
export function validateEnv(): void {
  const required = [
    'AWS_REGION',
    'JWT_SECRET'
  ];

  for (const key of required) {
    if (!process.env[key]) {
      throw new Error(`Missing required environment variable: ${key}`);
    }
  }
}