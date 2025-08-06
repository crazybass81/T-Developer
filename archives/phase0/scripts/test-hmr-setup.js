#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔥 Testing HMR Setup...\n');

// 1. Check if HMR files exist
const hmrFile = path.join(__dirname, '../backend/src/dev/hot-reload.ts');
const packageFile = path.join(__dirname, '../backend/package.json');

console.log('📁 Checking HMR files...');
if (fs.existsSync(hmrFile)) {
  console.log('✅ hot-reload.ts exists');
} else {
  console.log('❌ hot-reload.ts missing');
  process.exit(1);
}

// 2. Check dependencies
console.log('\n📦 Checking dependencies...');
const packageJson = JSON.parse(fs.readFileSync(packageFile, 'utf8'));
const requiredDeps = ['chokidar', 'ws'];

requiredDeps.forEach(dep => {
  if (packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep]) {
    console.log(`✅ ${dep} found`);
  } else {
    console.log(`❌ ${dep} missing`);
  }
});

// 3. Check HMR class structure
console.log('\n🔍 Checking HMR implementation...');
const hmrContent = fs.readFileSync(hmrFile, 'utf8');

const checks = [
  { name: 'HotModuleReplacementManager class', pattern: /class HotModuleReplacementManager/ },
  { name: 'WebSocket server setup', pattern: /WebSocket\.Server/ },
  { name: 'File watching', pattern: /chokidar\.watch/ },
  { name: 'Module cache clearing', pattern: /delete require\.cache/ },
  { name: 'HMR client script', pattern: /hmrClient.*=/ }
];

checks.forEach(check => {
  if (check.pattern.test(hmrContent)) {
    console.log(`✅ ${check.name}`);
  } else {
    console.log(`❌ ${check.name} missing`);
  }
});

console.log('\n✅ HMR setup verification complete!');
console.log('\n📋 Next steps:');
console.log('1. Install dependencies: npm install chokidar ws');
console.log('2. Add HMR to your dev server');
console.log('3. Test with file changes');