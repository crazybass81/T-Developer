#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

async function demoCodeGenerator() {
  console.log('🎯 Code Generator Demo\n');

  try {
    // Create a sample agent using the generator
    console.log('📝 Creating sample agent with predefined answers...');
    
    // Create a temporary input file for inquirer
    const inputAnswers = [
      'analysis',  // agent type
      ' ',         // space to select first capability (database-access)
      '\n',        // confirm selection
      'Sample analysis agent for demo purposes', // description
      '\n'         // confirm
    ].join('\n');

    // Write input to temp file
    await fs.writeFile('/tmp/generator-input.txt', inputAnswers);

    // Run the generator with input redirection
    console.log('🚀 Running code generator...');
    
    const command = `cd backend && echo "analysis\n \n\nSample analysis agent for demo purposes\n" | npx ts-node ../scripts/code-generator/generator.ts agent sample-demo`;
    
    try {
      execSync(command, { 
        stdio: 'inherit',
        timeout: 30000
      });
    } catch (error) {
      console.log('⚠️  Generator execution completed (may have interactive prompts)');
    }

    // Check if files were created
    const expectedFiles = [
      'backend/src/agents/sample-demo-agent.ts',
      'backend/tests/agents/sample-demo-agent.test.ts',
      'docs/agents/sample-demo-agent.md'
    ];

    console.log('\n📁 Checking generated files...');
    
    let filesCreated = 0;
    for (const file of expectedFiles) {
      try {
        await fs.access(file);
        console.log(`✅ ${file}`);
        filesCreated++;
      } catch {
        console.log(`❌ ${file} (not found)`);
      }
    }

    if (filesCreated > 0) {
      console.log(`\n🎉 Successfully generated ${filesCreated} files!`);
      
      // Show sample of generated agent code
      try {
        const agentCode = await fs.readFile('backend/src/agents/sample-demo-agent.ts', 'utf8');
        console.log('\n📄 Sample generated agent code:');
        console.log('```typescript');
        console.log(agentCode.split('\n').slice(0, 20).join('\n'));
        console.log('...');
        console.log('```');
      } catch (error) {
        console.log('Could not read generated agent file');
      }
    } else {
      console.log('\n❌ No files were generated. Check the generator setup.');
    }

    // Cleanup
    try {
      await fs.unlink('/tmp/generator-input.txt');
    } catch {}

  } catch (error) {
    console.error('❌ Demo failed:', error.message);
    process.exit(1);
  }
}

demoCodeGenerator().catch(console.error);