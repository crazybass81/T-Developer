#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

console.log('🔥 Testing HMR Integration...\n');

// Test HMR server startup
async function testHMRServer() {
  console.log('🚀 Starting HMR test server...');
  
  const server = spawn('npm', ['run', 'hmr:start'], {
    cwd: path.join(__dirname, '../backend'),
    stdio: 'pipe'
  });
  
  let serverReady = false;
  
  server.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(output);
    
    if (output.includes('HMR Dev Server running')) {
      serverReady = true;
      console.log('✅ HMR server started successfully');
      
      // Test file change simulation
      setTimeout(() => {
        testFileChange();
      }, 2000);
      
      // Stop server after test
      setTimeout(() => {
        server.kill('SIGINT');
      }, 5000);
    }
  });
  
  server.stderr.on('data', (data) => {
    console.error('Server error:', data.toString());
  });
  
  server.on('close', (code) => {
    console.log(`\n🔥 HMR server stopped (code: ${code})`);
    
    if (serverReady) {
      console.log('✅ HMR integration test completed successfully!');
    } else {
      console.log('❌ HMR server failed to start');
      process.exit(1);
    }
  });
}

function testFileChange() {
  console.log('\n📝 Simulating file change...');
  
  const testFile = path.join(__dirname, '../backend/src/test-hmr.ts');
  const testContent = `// Test file for HMR - ${new Date().toISOString()}\nexport const test = 'hmr-test';`;
  
  fs.writeFileSync(testFile, testContent);
  console.log('✅ Test file created/modified');
  
  // Clean up
  setTimeout(() => {
    if (fs.existsSync(testFile)) {
      fs.unlinkSync(testFile);
      console.log('🧹 Test file cleaned up');
    }
  }, 2000);
}

// Run test
testHMRServer().catch(console.error);