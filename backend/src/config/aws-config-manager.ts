import { 
  SSMClient, 
  GetParameterCommand, 
  GetParametersByPathCommand 
} from '@aws-sdk/client-ssm';
import { 
  SecretsManagerClient, 
  GetSecretValueCommand 
} from '@aws-sdk/client-secrets-manager';

interface ConfigValue {
  value: string;
  lastUpdated: Date;
}

export class AWSConfigManager {
  private ssmClient: SSMClient;
  private secretsClient: SecretsManagerClient;
  private cache: Map<string, ConfigValue> = new Map();
  private cacheTTL = 300000; // 5분

  constructor() {
    const region = process.env.AWS_REGION || 'us-east-1';
    this.ssmClient = new SSMClient({ region });
    this.secretsClient = new SecretsManagerClient({ region });
  }

  async getParameter(name: string): Promise<string> {
    const cached = this.cache.get(name);
    if (cached && Date.now() - cached.lastUpdated.getTime() < this.cacheTTL) {
      return cached.value;
    }

    try {
      const command = new GetParameterCommand({
        Name: name,
        WithDecryption: true
      });
      
      const response = await this.ssmClient.send(command);
      const value = response.Parameter?.Value || '';
      
      this.cache.set(name, {
        value,
        lastUpdated: new Date()
      });
      
      return value;
    } catch (error) {
      console.warn(`Failed to get parameter ${name}:`, error);
      return process.env[name.split('/').pop()!] || '';
    }
  }

  async getSecret(secretId: string): Promise<any> {
    const cached = this.cache.get(secretId);
    if (cached && Date.now() - cached.lastUpdated.getTime() < this.cacheTTL) {
      return JSON.parse(cached.value);
    }

    try {
      const command = new GetSecretValueCommand({ SecretId: secretId });
      const response = await this.secretsClient.send(command);
      
      const secretValue = response.SecretString || '{}';
      
      this.cache.set(secretId, {
        value: secretValue,
        lastUpdated: new Date()
      });
      
      return JSON.parse(secretValue);
    } catch (error) {
      console.warn(`Failed to get secret ${secretId}:`, error);
      return {};
    }
  }

  async loadAllConfig(): Promise<void> {
    const environment = process.env.NODE_ENV || 'development';
    
    // Parameter Store에서 설정 로드
    const parameterPath = `/t-developer/${environment}/`;
    
    try {
      const command = new GetParametersByPathCommand({
        Path: parameterPath,
        Recursive: true,
        WithDecryption: true
      });
      
      const response = await this.ssmClient.send(command);
      
      response.Parameters?.forEach(param => {
        if (param.Name && param.Value) {
          const envKey = param.Name.replace(parameterPath, '').replace(/\//g, '_').toUpperCase();
          process.env[envKey] = param.Value;
        }
      });
    } catch (error) {
      console.warn('Failed to load parameters from SSM:', error);
    }

    // Secrets Manager에서 민감한 정보 로드
    const secrets = await this.getSecret(`t-developer/${environment}/secrets`);
    Object.entries(secrets).forEach(([key, value]) => {
      process.env[key] = value as string;
    });
  }
}

export const configManager = new AWSConfigManager();