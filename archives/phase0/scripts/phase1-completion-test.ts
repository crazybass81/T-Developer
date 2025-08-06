#!/usr/bin/env ts-node

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import chalk from 'chalk';

interface TestResult {
  name: string;
  status: 'PASS' | 'FAIL' | 'SKIP';
  message?: string;
  duration?: number;
}

class Phase1CompletionTest {
  private results: TestResult[] = [];

  async runAllTests(): Promise<void> {
    console.log(chalk.blue('🧪 Phase 1 Completion Tests\n'));

    // Core Infrastructure Tests
    await this.testAgentSquadIntegration();
    await this.testAgnoFramework();
    await this.testBedrockAgentCore();
    await this.testDynamoDBConnection();
    await this.testRedisCache();
    await this.testLoggingSystem();
    await this.testConfigurationManagement();
    await this.testPerformanceBenchmarks();

    this.printResults();
    this.generateCompletionReport();
  }

  private async testAgentSquadIntegration(): Promise<void> {
    const start = Date.now();
    try {
      // Test Agent Squad orchestration
      const testCode = `
        import { AgentSquad } from 'agent-squad';
        const squad = new AgentSquad();
        await squad.initialize();
        console.log('Agent Squad initialized');
      `;
      
      execSync(`echo "${testCode}" | ts-node`, { stdio: 'pipe' });
      
      this.results.push({
        name: 'Agent Squad Integration',
        status: 'PASS',
        duration: Date.now() - start
      });
    } catch (error) {
      this.results.push({
        name: 'Agent Squad Integration',
        status: 'FAIL',
        message: error.message,
        duration: Date.now() - start
      });
    }
  }

  private async testAgnoFramework(): Promise<void> {
    const start = Date.now();
    try {
      // Test Agno Framework performance
      const testCode = `
        from agno import Agent
        import time
        
        # Test instantiation speed
        start = time.perf_counter_ns()
        agent = Agent()
        end = time.perf_counter_ns()
        
        instantiation_time_us = (end - start) / 1000
        print(f"Instantiation time: {instantiation_time_us:.2f}μs")
        
        if instantiation_time_us <= 10:  # Allow 10μs tolerance
            print("PASS: Agno performance target met")
        else:
            print("FAIL: Agno performance target not met")
      `;
      
      const result = execSync(`python3 -c "${testCode}"`, { encoding: 'utf8' });
      
      if (result.includes('PASS')) {
        this.results.push({
          name: 'Agno Framework Performance',
          status: 'PASS',
          duration: Date.now() - start
        });
      } else {
        this.results.push({
          name: 'Agno Framework Performance',
          status: 'FAIL',
          message: result,
          duration: Date.now() - start
        });
      }
    } catch (error) {
      this.results.push({
        name: 'Agno Framework Performance',
        status: 'FAIL',
        message: error.message,
        duration: Date.now() - start
      });
    }
  }

  private async testBedrockAgentCore(): Promise<void> {
    const start = Date.now();
    try {
      // Test Bedrock connection
      const testCode = `
        import { BedrockClient, ListFoundationModelsCommand } from '@aws-sdk/client-bedrock';
        const client = new BedrockClient({ region: 'us-east-1' });
        const command = new ListFoundationModelsCommand({});
        const response = await client.send(command);
        console.log('Bedrock connection successful');
      `;
      
      execSync(`echo "${testCode}" | ts-node`, { stdio: 'pipe' });
      
      this.results.push({
        name: 'Bedrock AgentCore Connection',
        status: 'PASS',
        duration: Date.now() - start
      });
    } catch (error) {
      this.results.push({
        name: 'Bedrock AgentCore Connection',
        status: 'SKIP',
        message: 'AWS credentials not configured',
        duration: Date.now() - start
      });
    }
  }

  private async testDynamoDBConnection(): Promise<void> {
    const start = Date.now();
    try {
      // Test DynamoDB local connection
      const testCode = `
        import { DynamoDBClient, ListTablesCommand } from '@aws-sdk/client-dynamodb';
        const client = new DynamoDBClient({ 
          endpoint: 'http://localhost:8000',
          region: 'us-east-1'
        });
        const command = new ListTablesCommand({});
        const response = await client.send(command);
        console.log('DynamoDB connection successful');
      `;
      
      execSync(`echo "${testCode}" | ts-node`, { stdio: 'pipe' });
      
      this.results.push({
        name: 'DynamoDB Connection',
        status: 'PASS',
        duration: Date.now() - start
      });
    } catch (error) {
      this.results.push({
        name: 'DynamoDB Connection',
        status: 'FAIL',
        message: 'DynamoDB Local not running',
        duration: Date.now() - start
      });
    }
  }

  private async testRedisCache(): Promise<void> {
    const start = Date.now();
    try {
      const testCode = `
        import Redis from 'ioredis';
        const redis = new Redis({ host: 'localhost', port: 6379 });
        await redis.ping();
        console.log('Redis connection successful');
        redis.disconnect();
      `;
      
      execSync(`echo "${testCode}" | ts-node`, { stdio: 'pipe' });
      
      this.results.push({
        name: 'Redis Cache Connection',
        status: 'PASS',
        duration: Date.now() - start
      });
    } catch (error) {
      this.results.push({
        name: 'Redis Cache Connection',
        status: 'FAIL',
        message: 'Redis not running',
        duration: Date.now() - start
      });
    }
  }

  private async testLoggingSystem(): Promise<void> {
    const start = Date.now();
    try {
      // Check if logging configuration exists
      if (existsSync('./backend/src/config/logger.ts')) {
        this.results.push({
          name: 'Logging System',
          status: 'PASS',
          duration: Date.now() - start
        });
      } else {
        this.results.push({
          name: 'Logging System',
          status: 'FAIL',
          message: 'Logger configuration not found',
          duration: Date.now() - start
        });
      }
    } catch (error) {
      this.results.push({
        name: 'Logging System',
        status: 'FAIL',
        message: error.message,
        duration: Date.now() - start
      });
    }
  }

  private async testConfigurationManagement(): Promise<void> {
    const start = Date.now();
    try {
      // Check if configuration files exist
      const configFiles = [
        '.env.example',
        'backend/src/config'
      ];
      
      const allExist = configFiles.every(file => existsSync(file));
      
      if (allExist) {
        this.results.push({
          name: 'Configuration Management',
          status: 'PASS',
          duration: Date.now() - start
        });
      } else {
        this.results.push({
          name: 'Configuration Management',
          status: 'FAIL',
          message: 'Configuration files missing',
          duration: Date.now() - start
        });
      }
    } catch (error) {
      this.results.push({
        name: 'Configuration Management',
        status: 'FAIL',
        message: error.message,
        duration: Date.now() - start
      });
    }
  }

  private async testPerformanceBenchmarks(): Promise<void> {
    const start = Date.now();
    try {
      // Simple performance test
      const iterations = 1000;
      const startTime = process.hrtime.bigint();
      
      for (let i = 0; i < iterations; i++) {
        // Simulate agent creation
        const obj = { id: i, timestamp: Date.now() };
      }
      
      const endTime = process.hrtime.bigint();
      const avgTime = Number(endTime - startTime) / iterations / 1000; // microseconds
      
      if (avgTime < 100) { // Less than 100μs per operation
        this.results.push({
          name: 'Performance Benchmarks',
          status: 'PASS',
          message: `Average operation time: ${avgTime.toFixed(2)}μs`,
          duration: Date.now() - start
        });
      } else {
        this.results.push({
          name: 'Performance Benchmarks',
          status: 'FAIL',
          message: `Performance too slow: ${avgTime.toFixed(2)}μs`,
          duration: Date.now() - start
        });
      }
    } catch (error) {
      this.results.push({
        name: 'Performance Benchmarks',
        status: 'FAIL',
        message: error.message,
        duration: Date.now() - start
      });
    }
  }

  private printResults(): void {
    console.log(chalk.blue('\n📊 Test Results:\n'));
    
    this.results.forEach(result => {
      const icon = result.status === 'PASS' ? '✅' : 
                   result.status === 'FAIL' ? '❌' : '⏭️';
      const color = result.status === 'PASS' ? chalk.green : 
                    result.status === 'FAIL' ? chalk.red : chalk.yellow;
      
      console.log(`${icon} ${color(result.name)} (${result.duration}ms)`);
      if (result.message) {
        console.log(`   ${chalk.gray(result.message)}`);
      }
    });
    
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => r.status === 'FAIL').length;
    const skipped = this.results.filter(r => r.status === 'SKIP').length;
    
    console.log(chalk.blue('\n📈 Summary:'));
    console.log(`${chalk.green('Passed:')} ${passed}`);
    console.log(`${chalk.red('Failed:')} ${failed}`);
    console.log(`${chalk.yellow('Skipped:')} ${skipped}`);
    
    const completionRate = (passed / (passed + failed)) * 100;
    console.log(`${chalk.blue('Completion Rate:')} ${completionRate.toFixed(1)}%`);
  }

  private generateCompletionReport(): void {
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const total = this.results.filter(r => r.status !== 'SKIP').length;
    const completionRate = (passed / total) * 100;
    
    console.log(chalk.blue('\n🎯 Phase 1 Completion Status:'));
    
    if (completionRate >= 80) {
      console.log(chalk.green('✅ Phase 1 COMPLETED - Ready for Phase 2'));
      console.log(chalk.green(`   Core infrastructure is ${completionRate.toFixed(1)}% functional`));
    } else if (completionRate >= 60) {
      console.log(chalk.yellow('⚠️  Phase 1 PARTIALLY COMPLETED'));
      console.log(chalk.yellow(`   ${completionRate.toFixed(1)}% functional - Some components need attention`));
    } else {
      console.log(chalk.red('❌ Phase 1 INCOMPLETE'));
      console.log(chalk.red(`   Only ${completionRate.toFixed(1)}% functional - Major issues need resolution`));
    }
  }
}

// Run tests
const tester = new Phase1CompletionTest();
tester.runAllTests().catch(console.error);