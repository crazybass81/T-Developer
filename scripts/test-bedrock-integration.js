#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 Testing Bedrock AgentCore Integration Setup...\n');

// 1. 파일 존재 확인
const files = [
  'backend/src/integrations/bedrock/agentcore-config.ts'
];

console.log('📁 Checking file existence:');
files.forEach(file => {
  const exists = fs.existsSync(file);
  console.log(`  ${exists ? '✅' : '❌'} ${file}`);
});

// 2. 의존성 확인
console.log('\n📦 Checking dependencies:');
const packageJsonPath = 'backend/package.json';
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
  
  const requiredDeps = [
    '@aws-sdk/client-bedrock-agent-runtime',
    'winston'
  ];
  
  requiredDeps.forEach(dep => {
    const exists = deps[dep];
    console.log(`  ${exists ? '✅' : '❌'} ${dep} ${exists ? `(${exists})` : ''}`);
  });
}

// 3. TypeScript 컴파일 확인
console.log('\n🔧 Checking TypeScript compilation:');
try {
  const { execSync } = require('child_process');
  execSync('cd backend && npx tsc --noEmit --skipLibCheck', { stdio: 'pipe' });
  console.log('  ✅ TypeScript compilation successful');
} catch (error) {
  console.log('  ❌ TypeScript compilation failed');
  console.log(`     Error: ${error.message}`);
}

// 4. 설정 파일 내용 검증
console.log('\n📋 Validating configuration structure:');
const configFile = 'backend/src/integrations/bedrock/agentcore-config.ts';
if (fs.existsSync(configFile)) {
  const content = fs.readFileSync(configFile, 'utf8');
  
  const checks = [
    { name: 'AgentCoreConfig interface', pattern: /interface AgentCoreConfig/ },
    { name: 'BedrockAgentCoreManager class', pattern: /class BedrockAgentCoreManager/ },
    { name: 'invokeAgent method', pattern: /async invokeAgent/ },
    { name: 'retrieveFromKnowledgeBase method', pattern: /async retrieveFromKnowledgeBase/ },
    { name: 'BedrockAgent abstract class', pattern: /abstract class BedrockAgent/ }
  ];
  
  checks.forEach(check => {
    const exists = check.pattern.test(content);
    console.log(`  ${exists ? '✅' : '❌'} ${check.name}`);
  });
}

console.log('\n🎯 Bedrock AgentCore Integration Setup Test Complete!');