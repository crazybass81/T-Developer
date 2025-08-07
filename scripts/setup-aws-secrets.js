#!/usr/bin/env node

/**
 * AWS Secrets Manager Setup Script
 * 
 * This script sets up AWS Secrets Manager for the T-Developer MVP project.
 * It creates and manages secrets for different environments (dev, staging, prod).
 */

const { 
  SecretsManagerClient, 
  CreateSecretCommand,
  UpdateSecretCommand,
  GetSecretValueCommand,
  ListSecretsCommand,
  DescribeSecretCommand
} = require('@aws-sdk/client-secrets-manager');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Configure AWS client
const client = new SecretsManagerClient({ 
  region: process.env.AWS_REGION || 'us-east-1' 
});

// Secret configurations for different environments
const SECRET_CONFIGS = {
  development: {
    name: 't-developer/dev',
    description: 'Development environment secrets for T-Developer MVP'
  },
  staging: {
    name: 't-developer/staging',
    description: 'Staging environment secrets for T-Developer MVP'
  },
  production: {
    name: 't-developer/prod',
    description: 'Production environment secrets for T-Developer MVP'
  }
};

// Default secret template
const SECRET_TEMPLATE = {
  // Database
  DB_HOST: '',
  DB_PORT: '5432',
  DB_NAME: 't_developer',
  DB_USER: '',
  DB_PASSWORD: '',
  
  // Redis
  REDIS_HOST: '',
  REDIS_PORT: '6379',
  REDIS_PASSWORD: '',
  
  // AWS Services
  AWS_ACCESS_KEY_ID: '',
  AWS_SECRET_ACCESS_KEY: '',
  AWS_REGION: 'us-east-1',
  
  // Bedrock
  BEDROCK_AGENT_ID: '',
  BEDROCK_AGENT_ALIAS_ID: '',
  BEDROCK_MODEL_ID: 'anthropic.claude-v2',
  
  // JWT
  JWT_SECRET: '',
  JWT_EXPIRES_IN: '7d',
  
  // OAuth (Optional)
  GOOGLE_CLIENT_ID: '',
  GOOGLE_CLIENT_SECRET: '',
  GITHUB_CLIENT_ID: '',
  GITHUB_CLIENT_SECRET: '',
  
  // Monitoring
  DATADOG_API_KEY: '',
  SENTRY_DSN: '',
  
  // Email
  SMTP_HOST: '',
  SMTP_PORT: '587',
  SMTP_USER: '',
  SMTP_PASSWORD: '',
  
  // API Keys
  OPENAI_API_KEY: '',
  STRIPE_API_KEY: '',
  SENDGRID_API_KEY: ''
};

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function secretExists(secretName) {
  try {
    await client.send(new DescribeSecretCommand({ SecretId: secretName }));
    return true;
  } catch (error) {
    if (error.name === 'ResourceNotFoundException') {
      return false;
    }
    throw error;
  }
}

async function createOrUpdateSecret(environment) {
  const config = SECRET_CONFIGS[environment];
  if (!config) {
    throw new Error(`Invalid environment: ${environment}`);
  }

  console.log(`\\n📝 Setting up secrets for ${environment} environment...`);
  
  // Check if secret exists
  const exists = await secretExists(config.name);
  
  // Load existing .env file if it exists
  const envFile = path.join(__dirname, `../.env.${environment}`);
  let currentSecrets = { ...SECRET_TEMPLATE };
  
  if (fs.existsSync(envFile)) {
    console.log(`📂 Found existing .env.${environment} file, loading values...`);
    const envContent = fs.readFileSync(envFile, 'utf8');
    envContent.split('\\n').forEach(line => {
      const [key, value] = line.split('=');
      if (key && value) {
        currentSecrets[key.trim()] = value.trim().replace(/^["']|["']$/g, '');
      }
    });
  }

  // Prompt for critical secrets
  console.log('\\n🔐 Enter critical secrets (press Enter to keep current value):');
  
  const criticalKeys = [
    'DB_USER', 'DB_PASSWORD', 
    'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
    'BEDROCK_AGENT_ID', 'BEDROCK_AGENT_ALIAS_ID',
    'JWT_SECRET'
  ];

  for (const key of criticalKeys) {
    const currentValue = currentSecrets[key] ? '(configured)' : '(not set)';
    const input = await question(`${key} ${currentValue}: `);
    if (input.trim()) {
      currentSecrets[key] = input.trim();
    }
  }

  // Generate JWT secret if not set
  if (!currentSecrets.JWT_SECRET) {
    currentSecrets.JWT_SECRET = require('crypto').randomBytes(64).toString('hex');
    console.log('✨ Generated random JWT_SECRET');
  }

  const secretString = JSON.stringify(currentSecrets, null, 2);

  try {
    if (exists) {
      // Update existing secret
      await client.send(new UpdateSecretCommand({
        SecretId: config.name,
        SecretString: secretString
      }));
      console.log(`✅ Updated secret: ${config.name}`);
    } else {
      // Create new secret
      await client.send(new CreateSecretCommand({
        Name: config.name,
        Description: config.description,
        SecretString: secretString,
        Tags: [
          { Key: 'Project', Value: 'T-Developer' },
          { Key: 'Environment', Value: environment },
          { Key: 'ManagedBy', Value: 'setup-script' }
        ]
      }));
      console.log(`✅ Created secret: ${config.name}`);
    }

    // Save to local .env file for development
    if (environment === 'development') {
      const envContent = Object.entries(currentSecrets)
        .map(([key, value]) => `${key}="${value}"`)
        .join('\\n');
      
      fs.writeFileSync(path.join(__dirname, '../.env'), envContent);
      console.log('📄 Saved to .env file for local development');
    }

  } catch (error) {
    console.error(`❌ Error managing secret: ${error.message}`);
    throw error;
  }
}

async function retrieveSecret(environment) {
  const config = SECRET_CONFIGS[environment];
  if (!config) {
    throw new Error(`Invalid environment: ${environment}`);
  }

  try {
    const response = await client.send(new GetSecretValueCommand({
      SecretId: config.name
    }));

    const secrets = JSON.parse(response.SecretString);
    console.log(`\\n🔑 Retrieved secrets for ${environment}:`);
    console.log('================================');
    
    Object.keys(secrets).forEach(key => {
      const value = secrets[key];
      const displayValue = key.includes('PASSWORD') || key.includes('SECRET') || key.includes('KEY')
        ? '***' 
        : value || '(not set)';
      console.log(`${key}: ${displayValue}`);
    });

    return secrets;
  } catch (error) {
    console.error(`❌ Error retrieving secret: ${error.message}`);
    throw error;
  }
}

async function listSecrets() {
  try {
    const response = await client.send(new ListSecretsCommand({
      Filters: [
        {
          Key: 'tag-key',
          Values: ['Project']
        }
      ]
    }));

    console.log('\\n📋 Configured Secrets:');
    console.log('======================');
    
    if (response.SecretList && response.SecretList.length > 0) {
      response.SecretList.forEach(secret => {
        console.log(`- ${secret.Name}: ${secret.Description || 'No description'}`);
        if (secret.Tags) {
          const env = secret.Tags.find(t => t.Key === 'Environment');
          if (env) console.log(`  Environment: ${env.Value}`);
        }
      });
    } else {
      console.log('No secrets found for this project');
    }
  } catch (error) {
    console.error(`❌ Error listing secrets: ${error.message}`);
    throw error;
  }
}

async function main() {
  console.log('🚀 AWS Secrets Manager Setup for T-Developer MVP');
  console.log('================================================\\n');

  const args = process.argv.slice(2);
  const command = args[0];
  const environment = args[1];

  try {
    switch (command) {
      case 'create':
      case 'update':
        if (!environment) {
          console.error('❌ Please specify an environment: development, staging, or production');
          process.exit(1);
        }
        await createOrUpdateSecret(environment);
        break;

      case 'get':
      case 'retrieve':
        if (!environment) {
          console.error('❌ Please specify an environment: development, staging, or production');
          process.exit(1);
        }
        await retrieveSecret(environment);
        break;

      case 'list':
        await listSecrets();
        break;

      case 'setup-all':
        for (const env of ['development', 'staging', 'production']) {
          await createOrUpdateSecret(env);
        }
        break;

      default:
        console.log('Usage:');
        console.log('  node setup-aws-secrets.js create <environment>   - Create or update secrets');
        console.log('  node setup-aws-secrets.js get <environment>      - Retrieve secrets');
        console.log('  node setup-aws-secrets.js list                   - List all secrets');
        console.log('  node setup-aws-secrets.js setup-all              - Setup all environments');
        console.log('\\nEnvironments: development, staging, production');
    }
  } catch (error) {
    console.error('\\n❌ Operation failed:', error.message);
    process.exit(1);
  } finally {
    rl.close();
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = { retrieveSecret, SECRET_CONFIGS };