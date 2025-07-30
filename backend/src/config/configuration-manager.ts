import { SSMClient, GetParameterCommand, GetParametersByPathCommand } from '@aws-sdk/client-ssm';
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

export interface ConfigManagerOptions {
  region: string;
  applicationName: string;
  readReplicaRegion?: string;
  pollInterval?: number;
}

export interface Configuration {
  [key: string]: any;
}

export interface ConfigChange {
  key: string;
  oldValue: any;
  newValue: any;
  timestamp: Date;
}

export interface ValidationError {
  key: string;
  value: any;
  errors: string[];
}

export class ConfigurationError extends Error {
  constructor(message: string, public errors: ValidationError[]) {
    super(message);
    this.name = 'ConfigurationError';
  }
}

export class ConfigurationManager {
  private ssmClient: SSMClient;
  private secretsClient: SecretsManagerClient;
  private cache: Map<string, { value: any; expiry: number }> = new Map();
  private validators: Map<string, ConfigValidator> = new Map();
  private currentConfig: Configuration = {};

  constructor(private config: ConfigManagerOptions) {
    this.ssmClient = new SSMClient({ region: config.region });
    this.secretsClient = new SecretsManagerClient({ region: config.region });
    this.registerDefaultValidators();
  }

  private registerDefaultValidators(): void {
    this.validators.set('server.port', new ConfigValidator({
      type: 'number',
      min: 1,
      max: 65535,
      required: false
    }));
    
    this.validators.set('database.host', new ConfigValidator({
      type: 'string',
      required: false
    }));
  }

  async loadConfiguration(): Promise<Configuration> {
    const baseConfig = this.loadBaseConfig();
    const envConfig = await this.loadEnvironmentConfig();
    const parameterConfig = await this.loadParameterStoreConfig();
    const secrets = await this.loadSecrets();

    const mergedConfig = {
      ...baseConfig,
      ...envConfig,
      ...parameterConfig,
      ...secrets
    };

    await this.validateConfiguration(mergedConfig);
    this.currentConfig = mergedConfig;
    return mergedConfig;
  }

  private loadBaseConfig(): any {
    return {
      server: {
        port: 3000,
        host: '0.0.0.0'
      },
      logging: {
        level: 'info',
        format: 'json'
      }
    };
  }

  private async loadEnvironmentConfig(): Promise<any> {
    return {
      server: {
        port: process.env.PORT ? parseInt(process.env.PORT) : undefined
      },
      database: {
        host: process.env.DB_HOST,
        port: process.env.DB_PORT ? parseInt(process.env.DB_PORT) : undefined
      }
    };
  }

  private async loadParameterStoreConfig(): Promise<any> {
    const prefix = `/${this.config.applicationName}/${process.env.NODE_ENV || 'development'}`;
    
    try {
      const response = await this.ssmClient.send(new GetParametersByPathCommand({
        Path: prefix,
        Recursive: true,
        WithDecryption: true
      }));

      const config: any = {};
      for (const param of response.Parameters || []) {
        const key = param.Name!.replace(prefix + '/', '').replace(/\//g, '.');
        const value = this.parseParameterValue(param.Value!, param.Type);
        this.setNestedProperty(config, key, value);
      }

      return config;
    } catch (error) {
      console.warn('Failed to load Parameter Store config:', error);
      return {};
    }
  }

  private async loadSecrets(): Promise<any> {
    const secretIds = ['database-credentials', 'api-keys'];
    const secrets: any = {};

    for (const secretId of secretIds) {
      try {
        const secretName = `${this.config.applicationName}/${process.env.NODE_ENV || 'development'}/${secretId}`;
        const secret = await this.getSecret(secretName);
        Object.assign(secrets, secret);
      } catch (error) {
        // Secret not found is acceptable
      }
    }

    return secrets;
  }

  private async getSecret(secretName: string): Promise<any> {
    const response = await this.secretsClient.send(new GetSecretValueCommand({
      SecretId: secretName
    }));

    if (response.SecretString) {
      return JSON.parse(response.SecretString);
    }
    return {};
  }

  private parseParameterValue(value: string, type?: string): any {
    if (type === 'StringList') {
      return value.split(',');
    }
    
    // Try to parse as JSON
    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  }

  private setNestedProperty(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    let current = obj;

    for (let i = 0; i < keys.length - 1; i++) {
      if (!(keys[i] in current)) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }

    current[keys[keys.length - 1]] = value;
  }

  private getNestedProperty(obj: any, path: string): any {
    const keys = path.split('.');
    let current = obj;

    for (const key of keys) {
      if (current[key] === undefined) return undefined;
      current = current[key];
    }

    return current;
  }

  private async validateConfiguration(config: Configuration): Promise<void> {
    const errors: ValidationError[] = [];

    for (const [key, validator] of this.validators) {
      const value = this.getNestedProperty(config, key);
      
      // Skip validation if value is undefined and not required
      if (value === undefined && !validator.definition?.required) {
        continue;
      }
      
      const result = await validator.validate(value);

      if (!result.valid) {
        errors.push({
          key,
          value,
          errors: result.errors
        });
      }
    }

    if (errors.length > 0) {
      throw new ConfigurationError('Configuration validation failed', errors);
    }
  }

  get<T>(key: string, defaultValue?: T): T {
    const value = this.getNestedProperty(this.currentConfig, key);
    
    if (value === undefined) {
      if (defaultValue !== undefined) {
        return defaultValue;
      }
      throw new Error(`Configuration key not found: ${key}`);
    }

    return value as T;
  }

  async watchForChanges(callback: (changes: ConfigChange[]) => void): Promise<void> {
    setInterval(async () => {
      const changes = await this.detectChanges();
      if (changes.length > 0) {
        callback(changes);
      }
    }, this.config.pollInterval || 60000);
  }

  private async detectChanges(): Promise<ConfigChange[]> {
    // Simplified change detection
    return [];
  }
}

export class ConfigValidator {
  constructor(public definition: any) {}

  async validate(value: any): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = [];

    if (this.definition.required && (value === undefined || value === null)) {
      errors.push('Value is required');
    }

    if (value !== undefined && this.definition.type) {
      if (this.definition.type === 'number' && typeof value !== 'number') {
        errors.push('Value must be a number');
      }
      
      if (this.definition.type === 'string' && typeof value !== 'string') {
        errors.push('Value must be a string');
      }
    }

    if (typeof value === 'number') {
      if (this.definition.min !== undefined && value < this.definition.min) {
        errors.push(`Value must be at least ${this.definition.min}`);
      }
      
      if (this.definition.max !== undefined && value > this.definition.max) {
        errors.push(`Value must be at most ${this.definition.max}`);
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}