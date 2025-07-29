import { 
  SecretsManagerClient, 
  GetSecretValueCommand,
  CreateSecretCommand,
  UpdateSecretCommand 
} from '@aws-sdk/client-secrets-manager';

export class SecretsManager {
  private client: SecretsManagerClient;
  private cache: Map<string, { value: any; expiry: number }> = new Map();
  private cacheTTL = 300000; // 5분
  
  constructor() {
    this.client = new SecretsManagerClient({
      region: process.env.AWS_REGION || 'us-east-1'
    });
  }
  
  async getSecret(secretName: string): Promise<any> {
    // 캐시 확인
    const cached = this.cache.get(secretName);
    if (cached && cached.expiry > Date.now()) {
      return cached.value;
    }
    
    try {
      const command = new GetSecretValueCommand({ SecretId: secretName });
      const response = await this.client.send(command);
      
      let secretValue: any;
      if (response.SecretString) {
        secretValue = JSON.parse(response.SecretString);
      } else if (response.SecretBinary) {
        const buff = Buffer.from(response.SecretBinary);
        secretValue = buff.toString('utf-8');
      }
      
      // 캐시에 저장
      this.cache.set(secretName, {
        value: secretValue,
        expiry: Date.now() + this.cacheTTL
      });
      
      return secretValue;
    } catch (error) {
      console.error(`Failed to retrieve secret ${secretName}:`, error);
      throw error;
    }
  }
  
  async createOrUpdateSecret(secretName: string, secretValue: any): Promise<void> {
    const secretString = typeof secretValue === 'string' 
      ? secretValue 
      : JSON.stringify(secretValue);
    
    try {
      // 먼저 업데이트 시도
      const updateCommand = new UpdateSecretCommand({
        SecretId: secretName,
        SecretString: secretString
      });
      await this.client.send(updateCommand);
      console.log(`✅ Secret updated: ${secretName}`);
    } catch (error: any) {
      if (error.name === 'ResourceNotFoundException') {
        // 없으면 생성
        const createCommand = new CreateSecretCommand({
          Name: secretName,
          SecretString: secretString,
          Description: `T-Developer secret: ${secretName}`
        });
        await this.client.send(createCommand);
        console.log(`✅ Secret created: ${secretName}`);
      } else {
        throw error;
      }
    }
    
    // 캐시 무효화
    this.cache.delete(secretName);
  }
  
  // 환경별 시크릿 로드
  async loadEnvironmentSecrets(): Promise<void> {
    const environment = process.env.NODE_ENV || 'development';
    const secretName = `t-developer/${environment}/config`;
    
    try {
      const secrets = await this.getSecret(secretName);
      
      // 환경 변수로 설정
      Object.entries(secrets).forEach(([key, value]) => {
        if (!process.env[key]) {
          process.env[key] = value as string;
        }
      });
      
      console.log(`✅ Loaded secrets for ${environment} environment`);
    } catch (error) {
      console.warn(`⚠️  No secrets found for ${environment}, using local .env`);
    }
  }
}

// 초기화 스크립트
export async function initializeSecrets(): Promise<void> {
  const manager = new SecretsManager();
  
  if (process.env.NODE_ENV === 'production') {
    await manager.loadEnvironmentSecrets();
  }
}