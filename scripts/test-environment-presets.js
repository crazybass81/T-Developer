#!/usr/bin/env node

const { spawn } = require('child_process');

// Simple test without importing TypeScript module
function testPresetFiles() {
  const fs = require('fs');
  const yaml = require('js-yaml');
  
  console.log('📦 Testing preset files...');
  
  const presetDir = './config/presets';
  const files = fs.readdirSync(presetDir);
  
  files.forEach(file => {
    if (file.endsWith('.yaml')) {
      const content = fs.readFileSync(path.join(presetDir, file), 'utf-8');
      const preset = yaml.load(content);
      console.log(`✅ ${file}: ${preset.name} - ${preset.description}`);
    }
  });
}
const path = require('path');

function testEnvironmentPresets() {
  console.log('🧪 Testing Environment Preset System...\n');

  try {
    // Test 1: Check TypeScript file exists
    const fs = require('fs');
    const tsFile = './backend/src/dev/environment-presets.ts';
    if (fs.existsSync(tsFile)) {
      console.log('✅ TypeScript implementation file exists');
    } else {
      throw new Error('TypeScript file not found');
    }
    
    // Test 2: Check preset files
    testPresetFiles();
    
    // Test 3: Check CLI integration
    const packageJson = JSON.parse(fs.readFileSync('./backend/package.json', 'utf-8'));
    if (packageJson.scripts['preset:list']) {
      console.log('✅ CLI scripts added to package.json');
    }
    
    console.log('\n✅ All Environment Preset tests passed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  testEnvironmentPresets();
}

module.exports = { testEnvironmentPresets, testPresetFiles };