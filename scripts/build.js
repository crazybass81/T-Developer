#!/usr/bin/env node

const webpack = require('webpack');
const { LambdaOptimizer } = require('../backend/src/performance/bundle-optimizer');

async function buildBackend() {
  console.log('🔨 Building backend...');
  
  const config = require('../webpack.config.js');
  
  return new Promise((resolve, reject) => {
    webpack(config, (err, stats) => {
      if (err || stats?.hasErrors()) {
        console.error('❌ Backend build failed:', err || stats?.toString());
        reject(err || new Error('Build failed'));
        return;
      }
      
      console.log('✅ Backend build completed');
      resolve();
    });
  });
}

async function buildLambdas() {
  console.log('🔨 Building Lambda functions...');
  
  const optimizer = new LambdaOptimizer();
  await optimizer.buildAllFunctions();
  
  console.log('✅ Lambda functions built');
}

async function main() {
  try {
    await buildBackend();
    await buildLambdas();
    console.log('🎉 All builds completed successfully!');
  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}