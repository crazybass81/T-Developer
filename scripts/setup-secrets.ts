import { SecretsManager } from '../backend/src/config/secrets-manager';

async function setupSecrets() {
  const manager = new SecretsManager();
  const environment = process.env.NODE_ENV || 'development';
  
  const secrets = {
    JWT_ACCESS_SECRET: process.env.JWT_ACCESS_SECRET || 'dev-access-secret',
    JWT_REFRESH_SECRET: process.env.JWT_REFRESH_SECRET || 'dev-refresh-secret',
    OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
    ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || '',
    GITHUB_TOKEN: process.env.GITHUB_TOKEN || ''
  };

  try {
    await manager.createOrUpdateSecret(`t-developer/${environment}/config`, secrets);
    console.log(`✅ Secrets configured for ${environment} environment`);
    
    console.log('\n📋 Next steps:');
    console.log('1. Update actual secret values in AWS Secrets Manager console');
    console.log('2. Ensure IAM role has secretsmanager:GetSecretValue permission');
    console.log('3. Test secret loading in production environment');
    
  } catch (error) {
    console.error('❌ Failed to setup secrets:', error);
    console.log('\n🔧 Troubleshooting:');
    console.log('- Check AWS credentials are configured');
    console.log('- Verify IAM permissions for Secrets Manager');
    console.log('- Ensure AWS_REGION is set correctly');
  }
}

setupSecrets();