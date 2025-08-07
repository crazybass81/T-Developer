/**
 * AWS Secrets Manager Integration
 * 
 * This module provides integration with AWS Secrets Manager
 * for secure configuration management.
 */

import {
  SecretsManagerClient,
  GetSecretValueCommand,
  GetSecretValueCommandOutput
} from '@aws-sdk/client-secrets-manager';

export class AWSSecretsManager {
  private client: SecretsManagerClient;
  private cache: Map<string, { value: any; timestamp: number }> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  constructor(region: string = process.env.AWS_REGION || 'us-east-1') {
    this.client = new SecretsManagerClient({ region });
  }

  /**
   * Get secret value from AWS Secrets Manager
   */
  async getSecret(secretName: string): Promise<Record<string, any>> {
    // Check cache first
    const cached = this.cache.get(secretName);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      console.log(`📦 Using cached secret: ${secretName}`);
      return cached.value;
    }

    try {
      console.log(`🔐 Fetching secret: ${secretName}`);
      
      const command = new GetSecretValueCommand({
        SecretId: secretName,
        VersionStage: 'AWSCURRENT'
      });

      const response: GetSecretValueCommandOutput = await this.client.send(command);
      
      let secretValue: Record<string, any>;
      
      if (response.SecretString) {
        secretValue = JSON.parse(response.SecretString);
      } else if (response.SecretBinary) {
        const buff = Buffer.from(response.SecretBinary);
        secretValue = JSON.parse(buff.toString('utf-8'));
      } else {
        throw new Error('Secret value is empty');
      }

      // Cache the secret
      this.cache.set(secretName, {
        value: secretValue,
        timestamp: Date.now()
      });

      console.log(`✅ Successfully retrieved secret: ${secretName}`);
      return secretValue;
    } catch (error: any) {
      console.error(`❌ Error retrieving secret ${secretName}:`, error.message);
      
      // Fallback to environment variables if Secrets Manager fails
      if (error.name === 'ResourceNotFoundException') {
        console.log('⚠️ Secret not found, falling back to environment variables');
        return this.getEnvFallback();
      }
      
      throw error;
    }
  }

  /**
   * Get specific secret value
   */
  async getSecretValue(secretName: string, key: string): Promise<string | undefined> {
    const secrets = await this.getSecret(secretName);
    return secrets[key];
  }

  /**
   * Load secrets into process.env
   */
  async loadSecretsToEnv(secretName: string): Promise<void> {
    try {
      const secrets = await this.getSecret(secretName);
      
      Object.entries(secrets).forEach(([key, value]) => {
        if (value && !process.env[key]) {
          process.env[key] = String(value);
        }
      });

      console.log('✅ Secrets loaded into environment variables');
    } catch (error) {
      console.error('❌ Failed to load secrets to environment:', error);
      throw error;
    }
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
    console.log('🧹 Secret cache cleared');
  }

  /**
   * Fallback to environment variables
   */
  private getEnvFallback(): Record<string, any> {
    return {
      DB_HOST: process.env.DB_HOST || 'localhost',
      DB_PORT: process.env.DB_PORT || '5432',
      DB_NAME: process.env.DB_NAME || 't_developer',
      DB_USER: process.env.DB_USER || 'postgres',
      DB_PASSWORD: process.env.DB_PASSWORD || '',
      REDIS_HOST: process.env.REDIS_HOST || 'localhost',
      REDIS_PORT: process.env.REDIS_PORT || '6379',
      REDIS_PASSWORD: process.env.REDIS_PASSWORD || '',
      JWT_SECRET: process.env.JWT_SECRET || 'dev-secret-key',
      AWS_REGION: process.env.AWS_REGION || 'us-east-1',
      BEDROCK_AGENT_ID: process.env.BEDROCK_AGENT_ID || '',
      BEDROCK_AGENT_ALIAS_ID: process.env.BEDROCK_AGENT_ALIAS_ID || ''
    };
  }
}

/**
 * Configuration manager that uses AWS Secrets Manager
 */
export class ConfigManager {
  private static instance: ConfigManager;
  private secretsManager: AWSSecretsManager;
  private environment: string;
  private config: Record<string, any> = {};

  private constructor() {
    this.secretsManager = new AWSSecretsManager();
    this.environment = process.env.NODE_ENV || 'development';
  }

  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  /**
   * Initialize configuration from AWS Secrets Manager
   */
  async initialize(): Promise<void> {
    const secretName = `t-developer/${this.environment === 'production' ? 'prod' : this.environment}`;
    
    try {
      // Load secrets from AWS Secrets Manager
      await this.secretsManager.loadSecretsToEnv(secretName);
      
      // Build configuration object
      this.config = {
        app: {
          name: 'T-Developer MVP',
          environment: this.environment,
          port: parseInt(process.env.PORT || '8000'),
          apiPrefix: '/api/v1'
        },
        database: {
          host: process.env.DB_HOST,
          port: parseInt(process.env.DB_PORT || '5432'),
          name: process.env.DB_NAME,
          user: process.env.DB_USER,
          password: process.env.DB_PASSWORD,
          ssl: this.environment === 'production'
        },
        redis: {
          host: process.env.REDIS_HOST,
          port: parseInt(process.env.REDIS_PORT || '6379'),
          password: process.env.REDIS_PASSWORD
        },
        auth: {
          jwtSecret: process.env.JWT_SECRET,
          jwtExpiresIn: process.env.JWT_EXPIRES_IN || '7d',
          bcryptRounds: 10
        },
        aws: {
          region: process.env.AWS_REGION || 'us-east-1',
          accessKeyId: process.env.AWS_ACCESS_KEY_ID,
          secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
          bedrock: {
            agentId: process.env.BEDROCK_AGENT_ID,
            agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID,
            modelId: process.env.BEDROCK_MODEL_ID || 'anthropic.claude-v2'
          }
        },
        oauth: {
          google: {
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET
          },
          github: {
            clientId: process.env.GITHUB_CLIENT_ID,
            clientSecret: process.env.GITHUB_CLIENT_SECRET
          }
        },
        monitoring: {
          datadogApiKey: process.env.DATADOG_API_KEY,
          sentryDsn: process.env.SENTRY_DSN
        },
        email: {
          smtp: {
            host: process.env.SMTP_HOST,
            port: parseInt(process.env.SMTP_PORT || '587'),
            user: process.env.SMTP_USER,
            password: process.env.SMTP_PASSWORD
          },
          sendgridApiKey: process.env.SENDGRID_API_KEY
        },
        features: {
          enableCache: process.env.ENABLE_CACHE === 'true',
          enableMetrics: process.env.ENABLE_METRICS === 'true',
          enableTracing: process.env.ENABLE_TRACING === 'true'
        }
      };

      console.log(`✅ Configuration initialized for ${this.environment} environment`);
    } catch (error) {
      console.error('❌ Failed to initialize configuration:', error);
      
      // Use fallback configuration
      this.config = this.getFallbackConfig();
      console.log('⚠️ Using fallback configuration');
    }
  }

  /**
   * Get configuration value
   */
  get<T = any>(path: string): T {
    const keys = path.split('.');
    let value: any = this.config;
    
    for (const key of keys) {
      value = value?.[key];
      if (value === undefined) break;
    }
    
    return value as T;
  }

  /**
   * Get entire configuration
   */
  getAll(): Record<string, any> {
    return { ...this.config };
  }

  /**
   * Refresh configuration from Secrets Manager
   */
  async refresh(): Promise<void> {
    this.secretsManager.clearCache();
    await this.initialize();
    console.log('🔄 Configuration refreshed');
  }

  /**
   * Get fallback configuration
   */
  private getFallbackConfig(): Record<string, any> {
    return {
      app: {
        name: 'T-Developer MVP',
        environment: this.environment,
        port: 8000,
        apiPrefix: '/api/v1'
      },
      database: {
        host: 'localhost',
        port: 5432,
        name: 't_developer',
        user: 'postgres',
        password: 'postgres',
        ssl: false
      },
      redis: {
        host: 'localhost',
        port: 6379,
        password: ''
      },
      auth: {
        jwtSecret: 'dev-secret-key',
        jwtExpiresIn: '7d',
        bcryptRounds: 10
      },
      aws: {
        region: 'us-east-1',
        bedrock: {
          modelId: 'anthropic.claude-v2'
        }
      },
      features: {
        enableCache: true,
        enableMetrics: false,
        enableTracing: false
      }
    };
  }
}

// Export singleton instance
export const configManager = ConfigManager.getInstance();