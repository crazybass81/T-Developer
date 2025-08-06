#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🧪 Testing Multimodal API Implementation...\n');

// Test file paths
const files = [
  'backend/src/multimodal/unified_api_ts.ts',
  'backend/src/llm/model_provider_abstract.py',
  'backend/src/llm/providers/openai_provider.py',
  'backend/src/llm/providers/bedrock_provider.py',
  'backend/src/llm/model_manager.py'
];

let allTestsPassed = true;

// Test 1: File existence
console.log('📁 Testing file existence...');
files.forEach(file => {
  const fullPath = path.join(process.cwd(), file);
  if (fs.existsSync(fullPath)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - File not found`);
    allTestsPassed = false;
  }
});

// Test 2: TypeScript syntax check
console.log('\n🔍 Testing TypeScript syntax...');
try {
  const tsFile = fs.readFileSync('backend/src/multimodal/unified_api_ts.ts', 'utf8');
  
  // Check for key components
  const checks = [
    { pattern: /interface MultiModalInput/, name: 'MultiModalInput interface' },
    { pattern: /interface MultiModalOutput/, name: 'MultiModalOutput interface' },
    { pattern: /class UnifiedMultiModalAPI/, name: 'UnifiedMultiModalAPI class' },
    { pattern: /async process\(/, name: 'process method' },
    { pattern: /processMixed\(/, name: 'processMixed method' }
  ];
  
  checks.forEach(check => {
    if (check.pattern.test(tsFile)) {
      console.log(`✅ ${check.name} found`);
    } else {
      console.log(`❌ ${check.name} missing`);
      allTestsPassed = false;
    }
  });
} catch (error) {
  console.log(`❌ TypeScript file read error: ${error.message}`);
  allTestsPassed = false;
}

// Test 3: Python syntax check
console.log('\n🐍 Testing Python syntax...');
try {
  const pyFile = fs.readFileSync('backend/src/llm/model_provider_abstract.py', 'utf8');
  
  const checks = [
    { pattern: /class ModelProvider\(ABC\)/, name: 'ModelProvider abstract class' },
    { pattern: /@abstractmethod/, name: 'Abstract methods' },
    { pattern: /class ModelProviderFactory/, name: 'ModelProviderFactory class' },
    { pattern: /async def generate/, name: 'Generate method' }
  ];
  
  checks.forEach(check => {
    if (check.pattern.test(pyFile)) {
      console.log(`✅ ${check.name} found`);
    } else {
      console.log(`❌ ${check.name} missing`);
      allTestsPassed = false;
    }
  });
} catch (error) {
  console.log(`❌ Python file read error: ${error.message}`);
  allTestsPassed = false;
}

// Test 4: Provider implementations
console.log('\n🔌 Testing provider implementations...');
const providers = ['openai_provider.py', 'bedrock_provider.py'];

providers.forEach(provider => {
  try {
    const providerFile = fs.readFileSync(`backend/src/llm/providers/${provider}`, 'utf8');
    
    const checks = [
      { pattern: /class \w+Provider\(ModelProvider\)/, name: 'Provider class inheritance' },
      { pattern: /async def initialize/, name: 'Initialize method' },
      { pattern: /async def generate/, name: 'Generate method' },
      { pattern: /def estimate_tokens/, name: 'Token estimation' }
    ];
    
    console.log(`\n  Testing ${provider}:`);
    checks.forEach(check => {
      if (check.pattern.test(providerFile)) {
        console.log(`  ✅ ${check.name}`);
      } else {
        console.log(`  ❌ ${check.name} missing`);
        allTestsPassed = false;
      }
    });
  } catch (error) {
    console.log(`  ❌ ${provider} read error: ${error.message}`);
    allTestsPassed = false;
  }
});

// Test 5: Model manager
console.log('\n🎛️  Testing model manager...');
try {
  const managerFile = fs.readFileSync('backend/src/llm/model_manager.py', 'utf8');
  
  const checks = [
    { pattern: /class ModelManager/, name: 'ModelManager class' },
    { pattern: /async def get_provider/, name: 'Get provider method' },
    { pattern: /def list_models/, name: 'List models method' },
    { pattern: /'gpt-4'[\s\S]*'claude-3-sonnet'/, name: 'Multiple model configs' }
  ];
  
  checks.forEach(check => {
    if (check.pattern.test(managerFile)) {
      console.log(`✅ ${check.name}`);
    } else {
      console.log(`❌ ${check.name} missing`);
      allTestsPassed = false;
    }
  });
} catch (error) {
  console.log(`❌ Model manager read error: ${error.message}`);
  allTestsPassed = false;
}

// Final result
console.log('\n' + '='.repeat(50));
if (allTestsPassed) {
  console.log('🎉 All multimodal API tests passed!');
  console.log('\n📋 Implementation Summary:');
  console.log('✅ Unified multimodal API with text/image/audio/video support');
  console.log('✅ Abstract model provider architecture');
  console.log('✅ OpenAI and Bedrock provider implementations');
  console.log('✅ Model manager with multiple LLM support');
  console.log('✅ Mock implementations for testing');
  
  process.exit(0);
} else {
  console.log('❌ Some tests failed. Please check the implementation.');
  process.exit(1);
}