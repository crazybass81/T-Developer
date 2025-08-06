#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

async function testCodeGenerator() {
  console.log('🧪 Testing Code Generator Setup...\n');

  const checks = [
    {
      name: 'Generator script exists',
      test: () => fs.access('scripts/code-generator/generator.ts')
    },
    {
      name: 'Agent template exists',
      test: () => fs.access('scripts/code-generator/templates/agent.hbs')
    },
    {
      name: 'Agent test template exists',
      test: () => fs.access('scripts/code-generator/templates/agent-test.hbs')
    },
    {
      name: 'Agent doc template exists',
      test: () => fs.access('scripts/code-generator/templates/agent-doc.hbs')
    },
    {
      name: 'Required dependencies installed',
      test: async () => {
        const packageJson = JSON.parse(await fs.readFile('backend/package.json', 'utf8'));
        const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
        
        const required = ['commander', 'inquirer', 'handlebars', 'chalk'];
        const missing = required.filter(dep => !deps[dep]);
        
        if (missing.length > 0) {
          throw new Error(`Missing dependencies: ${missing.join(', ')}`);
        }
      }
    }
  ];

  let passed = 0;
  let failed = 0;

  for (const check of checks) {
    try {
      await check.test();
      console.log(`✅ ${check.name}`);
      passed++;
    } catch (error) {
      console.log(`❌ ${check.name}: ${error.message}`);
      failed++;
    }
  }

  console.log(`\n📊 Test Results: ${passed} passed, ${failed} failed`);

  if (failed === 0) {
    console.log('\n🎉 Code generator setup is complete!');
    console.log('\nUsage:');
    console.log('  npx ts-node scripts/code-generator/generator.ts agent my-agent');
    console.log('\nNext steps:');
    console.log('  1. Install missing dependencies if any');
    console.log('  2. Test the generator with a sample agent');
    console.log('  3. Add more templates as needed');
  } else {
    console.log('\n❌ Some checks failed. Please fix the issues above.');
    process.exit(1);
  }
}

testCodeGenerator().catch(console.error);