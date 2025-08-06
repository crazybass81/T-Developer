#!/usr/bin/env node

const { APMService } = require('../backend/src/monitoring/apm');
const express = require('express');
const http = require('http');

console.log('🔍 Testing APM Service...\n');

// Test APM Service
const apmService = new APMService();

// Test metrics collection
console.log('1. Testing metrics collection...');
apmService.start(1000); // 1 second interval for testing

// Listen for metrics
apmService.on('metrics', (metrics) => {
  console.log('📊 Metrics collected:');
  console.log(`   CPU Usage: ${metrics.cpu.usage}%`);
  console.log(`   Memory: ${(metrics.memory.heapUsed / 1024 / 1024).toFixed(2)}MB / ${(metrics.memory.heapTotal / 1024 / 1024).toFixed(2)}MB`);
  console.log(`   Event Loop Delay: ${metrics.eventLoop.delay.toFixed(2)}ms`);
  console.log(`   Load Average: [${metrics.cpu.loadAverage.map(l => l.toFixed(2)).join(', ')}]`);
});

// Listen for alerts
apmService.on('alert', (alert) => {
  console.log(`🚨 Alert [${alert.level.toUpperCase()}]: ${alert.message}`);
});

// Test health status
setTimeout(() => {
  console.log('\n2. Testing health status...');
  const health = apmService.getHealthStatus();
  console.log(`   Healthy: ${health.healthy}`);
  if (health.issues.length > 0) {
    console.log(`   Issues: ${health.issues.join(', ')}`);
  }
}, 2000);

// Test Express endpoints
setTimeout(() => {
  console.log('\n3. Testing Express endpoints...');
  
  const app = express();
  const { apmEndpoints } = require('../backend/src/monitoring/apm');
  
  apmEndpoints(app);
  
  const server = http.createServer(app);
  server.listen(0, () => {
    const port = server.address().port;
    console.log(`   APM endpoints available on port ${port}`);
    
    // Test metrics endpoint
    http.get(`http://localhost:${port}/api/monitoring/metrics`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const metrics = JSON.parse(data);
        console.log('   ✅ /api/monitoring/metrics endpoint working');
        console.log(`      CPU: ${metrics.cpu.usage}%, Memory: ${(metrics.memory.heapUsed / 1024 / 1024).toFixed(2)}MB`);
      });
    });
    
    // Test health endpoint
    http.get(`http://localhost:${port}/api/monitoring/health`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const health = JSON.parse(data);
        console.log(`   ✅ /api/monitoring/health endpoint working (Status: ${res.statusCode})`);
        console.log(`      Healthy: ${health.healthy}`);
      });
    });
    
    // Test SSE endpoint
    const sseReq = http.get(`http://localhost:${port}/api/monitoring/stream`, (res) => {
      console.log('   ✅ /api/monitoring/stream SSE endpoint working');
      
      let eventCount = 0;
      res.on('data', (chunk) => {
        const data = chunk.toString();
        if (data.includes('data:')) {
          eventCount++;
          if (eventCount === 1) {
            console.log('      📡 Receiving real-time metrics via SSE');
          }
        }
      });
      
      // Close SSE after 3 seconds
      setTimeout(() => {
        sseReq.destroy();
        console.log(`      📊 Received ${eventCount} metric events`);
      }, 3000);
    });
    
    // Cleanup after tests
    setTimeout(() => {
      console.log('\n4. Cleaning up...');
      apmService.stop();
      server.close();
      console.log('✅ APM Service tests completed!\n');
      
      console.log('📋 APM Service Features:');
      console.log('   • Real-time CPU, memory, and event loop monitoring');
      console.log('   • Configurable thresholds with alerts');
      console.log('   • REST API endpoints for metrics and health');
      console.log('   • Server-Sent Events for real-time streaming');
      console.log('   • Health status with issue detection');
      
      process.exit(0);
    }, 5000);
  });
}, 3000);

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n🛑 Stopping APM Service...');
  apmService.stop();
  process.exit(0);
});