import { ConfigSystem, ConfigurationManager, FeatureFlagManager } from '../../src/config';

// Mock AWS SDK
jest.mock('@aws-sdk/client-ssm');
jest.mock('@aws-sdk/client-secrets-manager');
jest.mock('@aws-sdk/client-kms');

describe('Configuration System', () => {
  let configSystem: ConfigSystem;

  beforeEach(() => {
    configSystem = new ConfigSystem({
      region: 'us-east-1',
      applicationName: 'test-app',
      enableFeatureFlags: true,
      enableSecrets: true,
      enableAudit: true
    });
  });

  test('should initialize configuration system', async () => {
    await configSystem.initialize();
    expect(configSystem.config).toBeInstanceOf(ConfigurationManager);
  });

  test('should provide feature flags manager when enabled', () => {
    expect(configSystem.featureFlags).toBeInstanceOf(FeatureFlagManager);
  });

  test('should perform health check', async () => {
    const health = await configSystem.healthCheck();
    expect(health.status).toBe('healthy');
    expect(health.components.configuration).toBe('healthy');
  });
});

describe('Configuration Manager', () => {
  let configManager: ConfigurationManager;

  beforeEach(() => {
    configManager = new ConfigurationManager({
      region: 'us-east-1',
      applicationName: 'test-app'
    });
  });

  test('should get configuration value with default', () => {
    const value = configManager.get('nonexistent.key', 'default-value');
    expect(value).toBe('default-value');
  });

  test('should throw error for missing required config', () => {
    expect(() => {
      configManager.get('required.key');
    }).toThrow('Configuration key not found: required.key');
  });
});

describe('Feature Flag Manager', () => {
  let flagManager: FeatureFlagManager;

  beforeEach(() => {
    flagManager = new FeatureFlagManager({
      tableName: 'test-flags',
      redis: null
    });
  });

  test('should evaluate feature flag', async () => {
    await flagManager.defineFlag({
      key: 'test-flag',
      name: 'Test Flag',
      description: 'A test flag',
      enabled: true,
      defaultValue: true,
      rules: []
    });

    const result = await flagManager.evaluate('test-flag', {
      userId: 'user123'
    });

    expect(typeof result).toBe('boolean');
  });

  test('should return false for non-existent flag', async () => {
    const result = await flagManager.evaluate('non-existent', {
      userId: 'user123'
    });

    expect(result).toBe(false);
  });
});