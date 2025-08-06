const { SecretsManagerClient, CreateSecretCommand } = require('@aws-sdk/client-secrets-manager');

async function createSecrets() {
  console.log('🔐 AWS Secrets Manager 시크릿 생성...\n');
  
  const client = new SecretsManagerClient({ region: 'us-east-1' });
  
  const secrets = [
    {
      name: 't-developer/development/config',
      value: {
        JWT_ACCESS_SECRET: 'dev-jwt-access-secret-key',
        JWT_REFRESH_SECRET: 'dev-jwt-refresh-secret-key',
        ENCRYPTION_KEY: 'dev-encryption-key-32-characters',
        OPENAI_API_KEY: 'sk-dev-openai-key',
        ANTHROPIC_API_KEY: 'sk-ant-dev-anthropic-key'
      }
    },
    {
      name: 't-developer/production/config',
      value: {
        JWT_ACCESS_SECRET: 'prod-jwt-access-secret-key',
        JWT_REFRESH_SECRET: 'prod-jwt-refresh-secret-key',
        ENCRYPTION_KEY: 'prod-encryption-key-32-characters',
        OPENAI_API_KEY: 'sk-prod-openai-key',
        ANTHROPIC_API_KEY: 'sk-ant-prod-anthropic-key'
      }
    }
  ];
  
  for (const secret of secrets) {
    try {
      const command = new CreateSecretCommand({
        Name: secret.name,
        SecretString: JSON.stringify(secret.value),
        Description: `T-Developer configuration for ${secret.name.split('/')[1]} environment`
      });
      
      await client.send(command);
      console.log(`✅ 시크릿 생성 완료: ${secret.name}`);
    } catch (error) {
      if (error.name === 'ResourceExistsException') {
        console.log(`ℹ️  시크릿이 이미 존재함: ${secret.name}`);
      } else {
        console.error(`❌ 시크릿 생성 실패: ${secret.name}`, error.message);
      }
    }
  }
  
  console.log('\n🎉 Secrets Manager 설정 완료!');
}

createSecrets().catch(console.error);