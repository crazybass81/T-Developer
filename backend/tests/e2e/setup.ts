import { spawn, ChildProcess } from 'child_process';
import { DynamoDBClient, CreateTableCommand } from '@aws-sdk/client-dynamodb';

export class E2ETestEnvironment {
  private processes: ChildProcess[] = [];
  private dynamoClient: DynamoDBClient;
  
  constructor() {
    this.dynamoClient = new DynamoDBClient({
      endpoint: 'http://localhost:8000',
      region: 'us-east-1',
      credentials: {
        accessKeyId: 'test',
        secretAccessKey: 'test'
      }
    });
  }
  
  async setup(): Promise<void> {
    console.log('🔧 Setting up E2E test environment...');
    
    // 1. DynamoDB Local 시작
    await this.startDynamoDBLocal();
    
    // 2. Redis 시작
    await this.startRedis();
    
    // 3. 테스트 테이블 생성
    await this.createTestTables();
    
    // 4. 애플리케이션 서버 시작
    await this.startAppServer();
    
    console.log('✅ E2E test environment ready!');
  }
  
  async teardown(): Promise<void> {
    console.log('🧹 Cleaning up E2E test environment...');
    
    // 모든 프로세스 종료
    this.processes.forEach(process => {
      process.kill('SIGTERM');
    });
    
    // 프로세스 종료 대기
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('✅ E2E test environment cleaned up!');
  }
  
  private async startDynamoDBLocal(): Promise<void> {
    const dynamodb = spawn('docker', [
      'run',
      '--rm',
      '-p', '8000:8000',
      'amazon/dynamodb-local',
      '-jar', 'DynamoDBLocal.jar',
      '-inMemory'
    ]);
    
    this.processes.push(dynamodb);
    
    // DynamoDB 시작 대기
    await this.waitForPort(8000, 10000);
  }
  
  private async startRedis(): Promise<void> {
    const redis = spawn('docker', [
      'run',
      '--rm',
      '-p', '6379:6379',
      'redis:7-alpine'
    ]);
    
    this.processes.push(redis);
    
    // Redis 시작 대기
    await this.waitForPort(6379, 10000);
  }
  
  private async createTestTables(): Promise<void> {
    const tables = [
      {
        TableName: 'test-projects',
        KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
        AttributeDefinitions: [{ AttributeName: 'id', AttributeType: 'S' }],
        BillingMode: 'PAY_PER_REQUEST'
      }
    ];
    
    for (const table of tables) {
      try {
        await this.dynamoClient.send(new CreateTableCommand(table));
      } catch (error: any) {
        if (error.name !== 'ResourceInUseException') {
          throw error;
        }
      }
    }
  }
  
  private async startAppServer(): Promise<void> {
    const app = spawn('npm', ['run', 'start:test'], {
      env: {
        ...process.env,
        NODE_ENV: 'test',
        PORT: '8080'
      }
    });
    
    this.processes.push(app);
    
    // 앱 서버 시작 대기
    await this.waitForPort(8080, 30000);
  }
  
  private async waitForPort(port: number, timeout: number): Promise<void> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        const response = await fetch(`http://localhost:${port}`);
        if (response.ok || response.status === 404) {
          return;
        }
      } catch (error) {
        // 연결 실패, 재시도
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error(`Port ${port} did not become available within ${timeout}ms`);
  }
}