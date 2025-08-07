/**
 * Hybrid Configuration Manager
 * Uses both AWS Secrets Manager and Parameter Store
 */

import {
  SecretsManagerClient,
  GetSecretValueCommand
} from '@aws-sdk/client-secrets-manager';

import {
  SSMClient,
  GetParametersByPathCommand
} from '@aws-sdk/client-ssm';

export class HybridConfigManager {
  private secretsClient: SecretsManagerClient;
  private ssmClient: SSMClient;
  private cache: Map<string, any> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private environment: string;

  constructor(region: string = process.env.AWS_REGION || 'us-east-1') {
    this.secretsClient = new SecretsManagerClient({ region });
    this.ssmClient = new SSMClient({ region });
    this.environment = process.env.NODE_ENV || 'development';
  }

  /**
   * Load all configuration from both sources
   */
  async initialize(): Promise<void> {
    try {
      console.log('🔐 Loading configuration...');
      
      // 1. Load general config from Parameter Store
      await this.loadParameterStoreConfig();
      
      // 2. Load secrets from Secrets Manager
      await this.loadSecrets();
      
      console.log('✅ Configuration loaded successfully');
    } catch (error) {
      console.error('❌ Failed to load configuration:', error);
      throw error;
    }
  }

  /**
   * Load configuration from Parameter Store
   */
  private async loadParameterStoreConfig(): Promise<void> {
    const path = `/t-developer/${this.environment}`;
    
    try {
      console.log(`📦 Loading parameters from: ${path}`);
      
      let nextToken: string | undefined;
      let totalParams = 0;
      
      do {
        const command = new GetParametersByPathCommand({
          Path: path,
          Recursive: true,
          WithDecryption: true,
          MaxResults: 10,
          NextToken: nextToken
        });
        
        const response = await this.ssmClient.send(command);
        
        if (response.Parameters) {
          response.Parameters.forEach(param => {
            if (param.Name && param.Value) {
              // Extract key from path (e.g., /t-developer/development/DB_HOST -> DB_HOST)
              const parts = param.Name.split('/');
              const key = parts[parts.length - 1];
              process.env[key] = param.Value;
              this.cache.set(key, param.Value);
            }
          });
          totalParams += response.Parameters.length;
        }
        
        nextToken = response.NextToken;
      } while (nextToken);
      
      console.log(`✅ Loaded ${totalParams} parameters from Parameter Store`);
    } catch (error: any) {
      if (error.name === 'ParameterNotFound') {
        console.log('⚠️ No parameters found in Parameter Store');
      } else {
        throw error;
      }
    }
  }

  /**
   * Load secrets from Secrets Manager
   */
  private async loadSecrets(): Promise<void> {
    const secretName = `t-developer/${this.environment}/secrets`;
    
    try {
      console.log(`🔐 Loading secrets from: ${secretName}`);
      
      const command = new GetSecretValueCommand({
        SecretId: secretName,
        VersionStage: 'AWSCURRENT'
      });
      
      const response = await this.secretsClient.send(command);
      
      if (response.SecretString) {
        const secrets = JSON.parse(response.SecretString);
        
        Object.entries(secrets).forEach(([key, value]) => {
          if (value) {
            process.env[key] = String(value);
            this.cache.set(key, value);
          }
        });
        
        console.log(`✅ Loaded ${Object.keys(secrets).length} secrets from Secrets Manager`);
      }
    } catch (error: any) {
      if (error.name === 'ResourceNotFoundException') {
        console.log('⚠️ Secrets not found in Secrets Manager');
      } else {
        throw error;
      }
    }
  }

  /**
   * Get configuration value
   */
  get(key: string): string | undefined {
    // Check cache first
    if (this.cache.has(key)) {
      return this.cache.get(key);
    }
    
    // Fallback to environment variable
    return process.env[key];
  }

  /**
   * Get all configuration
   */
  getAll(): Record<string, any> {
    const config: Record<string, any> = {};
    
    // Add all cached values
    this.cache.forEach((value, key) => {
      config[key] = value;
    });
    
    return config;
  }

  /**
   * Build structured configuration object
   */
  getStructuredConfig(): Record<string, any> {
    return {
      app: {
        name: this.get('APP_NAME') || 'T-Developer MVP',
        environment: this.environment,
        port: parseInt(this.get('PORT') || '8000'),
        apiPrefix: this.get('API_PREFIX') || '/api/v1'
      },
      database: {
        host: this.get('DB_HOST'),
        port: parseInt(this.get('DB_PORT') || '5432'),
        name: this.get('DB_NAME'),
        user: this.get('DB_USER'),
        password: this.get('DB_PASSWORD'), // From Secrets Manager
        ssl: this.environment === 'production'
      },
      redis: {
        host: this.get('REDIS_HOST'),
        port: parseInt(this.get('REDIS_PORT') || '6379'),
        password: this.get('REDIS_PASSWORD') // From Secrets Manager
      },
      auth: {
        jwtSecret: this.get('JWT_SECRET'), // From Secrets Manager
        jwtExpiresIn: this.get('JWT_EXPIRES_IN') || '7d',
        bcryptRounds: parseInt(this.get('BCRYPT_ROUNDS') || '10')
      },
      aws: {
        region: this.get('AWS_REGION') || 'us-east-1',
        bedrock: {
          agentId: this.get('BEDROCK_AGENT_ID'),
          agentAliasId: this.get('BEDROCK_AGENT_ALIAS_ID'),
          modelId: this.get('BEDROCK_MODEL_ID') || 'anthropic.claude-v2'
        }
      },
      features: {
        enableCache: this.get('ENABLE_CACHE') === 'true',
        enableMetrics: this.get('ENABLE_METRICS') === 'true',
        enableTracing: this.get('ENABLE_TRACING') === 'true'
      }
    };
  }

  /**
   * Refresh configuration
   */
  async refresh(): Promise<void> {
    this.cache.clear();
    await this.initialize();
    console.log('🔄 Configuration refreshed');
  }
}

// Export singleton instance
export const configManager = new HybridConfigManager();