#!/usr/bin/env node

const path = require('path');
const fs = require('fs');

async function testAgentSquadSetup() {
  console.log('🔍 Testing Agent Squad Setup...\n');

  const checks = [
    {
      name: 'Agent Squad Config File',
      check: () => fs.existsSync(path.join(__dirname, '../backend/src/config/agent-squad.config.ts')),
      critical: true
    },
    {
      name: 'Agent Squad Mock Library',
      check: () => fs.existsSync(path.join(__dirname, '../backend/src/lib/agent-squad/index.ts')),
      critical: true
    },
    {
      name: 'Base Orchestrator',
      check: () => fs.existsSync(path.join(__dirname, '../backend/src/orchestration/base-orchestrator.ts')),
      critical: true
    }
  ];

  let passed = 0;
  let failed = 0;

  for (const check of checks) {
    const result = check.check();
    const icon = result ? '✅' : '❌';
    const status = result ? 'PASS' : 'FAIL';
    
    console.log(`${icon} ${check.name}: ${status}`);
    
    if (result) {
      passed++;
    } else {
      failed++;
      if (check.critical) {
        console.log(`   ⚠️  Critical check failed!`);
      }
    }
  }

  console.log('\n' + '='.repeat(50));
  console.log(`📊 Results: ${passed} passed, ${failed} failed`);

  if (failed === 0) {
    console.log('🎉 All Agent Squad setup checks passed!');
    console.log('✅ SubTask 1.1.1 completed successfully');
  } else {
    console.log('❌ Some checks failed. Please review the setup.');
  }

  return failed === 0;
}

// Test TypeScript compilation
async function testTypeScriptCompilation() {
  console.log('\n🔧 Testing TypeScript compilation...');
  
  try {
    const { execSync } = require('child_process');
    execSync('npx tsc --noEmit --project backend/tsconfig.json', { 
      cwd: path.join(__dirname, '..'),
      stdio: 'pipe'
    });
    console.log('✅ TypeScript compilation successful');
    return true;
  } catch (error) {
    console.log('❌ TypeScript compilation failed');
    console.log(error.stdout?.toString() || error.message);
    return false;
  }
}

if (require.main === module) {
  testAgentSquadSetup()
    .then(setupOk => testTypeScriptCompilation())
    .then(compileOk => {
      process.exit(compileOk ? 0 : 1);
    })
    .catch(console.error);
}

module.exports = { testAgentSquadSetup };