#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

console.log('🔧 Setting up T-Developer environment...');

// Check if .env already exists
const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  console.log('ℹ️  .env file already exists, skipping creation');
  process.exit(0);
}

// Copy .env.example to .env
const envExamplePath = path.join(__dirname, '..', '.env.example');
if (!fs.existsSync(envExamplePath)) {
  console.error('❌ .env.example file not found');
  process.exit(1);
}

const envContent = fs.readFileSync(envExamplePath, 'utf8');

// Generate secure values
const jwtSecret = crypto.randomBytes(32).toString('hex');
const encryptionKey = crypto.randomBytes(32).toString('hex');

// Replace placeholder values
const updatedContent = envContent
  .replace('your-super-secret-jwt-key', jwtSecret)
  .replace('your-32-character-encryption-key', encryptionKey);

// Write .env file
fs.writeFileSync(envPath, updatedContent);

console.log('✅ Environment file created successfully!');
console.log('📋 Next steps:');
console.log('1. Update AWS credentials in .env file');
console.log('2. Add your AI model API keys (OpenAI, Anthropic)');
console.log('3. Configure Bedrock AgentCore settings');
console.log('4. Run: npm run setup:db');

console.log('\n🔐 Generated secure keys:');
console.log('- JWT Secret: ✓');
console.log('- Encryption Key: ✓');

console.log('\n⚠️  Remember to:');
console.log('- Never commit .env to version control');
console.log('- Keep your API keys secure');
console.log('- Use different keys for production');