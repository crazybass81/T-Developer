import { S3Client } from '@aws-sdk/client-s3';
import { LambdaClient } from '@aws-sdk/client-lambda';
import { SecretsManagerClient } from '@aws-sdk/client-secrets-manager';
import { CloudWatchLogsClient } from '@aws-sdk/client-cloudwatch-logs';

// LocalStack 클라이언트 설정
const localStackConfig = {
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.LOCALSTACK_ENDPOINT || 'http://localhost:4566',
  credentials: {
    accessKeyId: 'test',
    secretAccessKey: 'test'
  }
};

// 개발 환경에서만 LocalStack 사용
const useLocalStack = process.env.NODE_ENV === 'development' && process.env.USE_LOCALSTACK === 'true';

export const s3Client = new S3Client(
  useLocalStack ? localStackConfig : { region: process.env.AWS_REGION }
);

export const lambdaClient = new LambdaClient(
  useLocalStack ? localStackConfig : { region: process.env.AWS_REGION }
);

export const secretsManagerClient = new SecretsManagerClient(
  useLocalStack ? localStackConfig : { region: process.env.AWS_REGION }
);

export const cloudWatchLogsClient = new CloudWatchLogsClient(
  useLocalStack ? localStackConfig : { region: process.env.AWS_REGION }
);

// LocalStack 상태 확인
export async function checkLocalStackHealth(): Promise<boolean> {
  if (!useLocalStack) return true;
  
  try {
    const response = await fetch(`${localStackConfig.endpoint}/_localstack/health`);
    const health = await response.json();
    
    const requiredServices = ['s3', 'lambda', 'secretsmanager', 'logs'];
    const availableServices = Object.keys(health.services);
    
    return requiredServices.every(service => availableServices.includes(service));
  } catch (error) {
    console.error('LocalStack health check failed:', error);
    return false;
  }
}