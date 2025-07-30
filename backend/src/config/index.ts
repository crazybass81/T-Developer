import { ConfigurationManager } from './configuration-manager';
import { FeatureFlagManager } from './feature-flags';
import { SecretsManager } from './secrets-manager';
import { ConfigurationAudit } from './config-audit';

export interface ConfigSystemOptions {
  region: string;
  applicationName: string;
  enableFeatureFlags?: boolean;
  enableSecrets?: boolean;
  enableAudit?: boolean;
}

export class ConfigSystem {
  private configManager: ConfigurationManager;
  private featureFlagManager?: FeatureFlagManager;
  private secretsManager?: SecretsManager;
  private auditManager?: ConfigurationAudit;

  constructor(private options: ConfigSystemOptions) {
    this.configManager = new ConfigurationManager({
      region: options.region,
      applicationName: options.applicationName
    });

    if (options.enableFeatureFlags) {
      this.featureFlagManager = new FeatureFlagManager({
        tableName: `${options.applicationName}-feature-flags`,
        redis: null // Simplified
      });
    }

    if (options.enableSecrets) {
      this.secretsManager = new SecretsManager({
        region: options.region,
        applicationName: options.applicationName
      });
    }

    if (options.enableAudit) {
      this.auditManager = new ConfigurationAudit();
    }
  }

  async initialize(): Promise<void> {
    // Load initial configuration
    await this.configManager.loadConfiguration();
    
    console.log('Configuration system initialized');
  }

  get config(): ConfigurationManager {
    return this.configManager;
  }

  get featureFlags(): FeatureFlagManager | undefined {
    return this.featureFlagManager;
  }

  get secrets(): SecretsManager | undefined {
    return this.secretsManager;
  }

  get audit(): ConfigurationAudit | undefined {
    return this.auditManager;
  }

  async healthCheck(): Promise<{ status: string; components: any }> {
    const components: any = {
      configuration: 'healthy'
    };

    if (this.featureFlagManager) {
      components.featureFlags = 'healthy';
    }

    if (this.secretsManager) {
      components.secrets = 'healthy';
    }

    if (this.auditManager) {
      components.audit = 'healthy';
    }

    return {
      status: 'healthy',
      components
    };
  }
}

// Export all components
export { ConfigurationManager } from './configuration-manager';
export { FeatureFlagManager } from './feature-flags';
export { SecretsManager } from './secrets-manager';
export { ConfigurationAudit } from './config-audit';

// Create default instance
export const createConfigSystem = (options: ConfigSystemOptions): ConfigSystem => {
  return new ConfigSystem(options);
};