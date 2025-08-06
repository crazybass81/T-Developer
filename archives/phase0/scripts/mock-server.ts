#!/usr/bin/env ts-node

import { MockServiceManager, WebSocketMockServer } from '../backend/src/dev/mock-system';
import { createServer } from 'http';
import chalk from 'chalk';

class MockServerRunner {
  private mockManager: MockServiceManager;
  private wsServer?: WebSocketMockServer;
  
  constructor() {
    this.mockManager = new MockServiceManager();
  }
  
  async start(): Promise<void> {
    console.log(chalk.blue('🎭 Starting mock services...'));
    
    try {
      // Start all mock services
      await this.mockManager.startAll();
      
      // Start WebSocket mock server
      const httpServer = createServer();
      this.wsServer = new WebSocketMockServer(httpServer);
      
      httpServer.listen(4570, () => {
        console.log(chalk.green('📡 WebSocket mock server running on port 4570'));
      });
      
      console.log(chalk.green('\n✅ All mock services are running!'));
      console.log(chalk.blue('\n📋 Mock Endpoints:'));
      console.log('  🤖 Bedrock: http://localhost:4567');
      console.log('  🗃️  DynamoDB: http://localhost:8000');
      console.log('  ☁️  S3: http://localhost:4568');
      console.log('  🌐 External APIs: http://localhost:4569');
      console.log('  📡 WebSocket: ws://localhost:4570');
      
      console.log(chalk.yellow('\n🔧 Environment Variables:'));
      console.log('  USE_MOCKS=true');
      console.log('  MOCK_BEDROCK=true');
      console.log('  MOCK_DYNAMODB=true');
      console.log('  MOCK_S3=true');
      console.log('  MOCK_EXTERNAL_APIS=true');
      
      // Graceful shutdown
      process.on('SIGINT', async () => {
        console.log(chalk.yellow('\n🛑 Shutting down mock services...'));
        await this.mockManager.stopAll();
        process.exit(0);
      });
      
    } catch (error) {
      console.error(chalk.red('❌ Failed to start mock services:'), error);
      process.exit(1);
    }
  }
}

if (require.main === module) {
  const runner = new MockServerRunner();
  runner.start().catch(console.error);
}

export { MockServerRunner };