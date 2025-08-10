import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { mockClient } from 'aws-sdk-client-mock';

// DynamoDB Test Client
export const dynamoDBTestClient = mockClient(DynamoDBDocumentClient);

// 테스트 데이터 생성기
export class TestDataGenerator {
  static project(overrides?: Partial<any>) {
    return {
      id: `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId: 'user_test_123',
      name: 'Test Project',
      description: 'A test project description',
      status: 'analyzing',
      createdAt: new Date().toISOString(),
      ...overrides
    };
  }
  
  static agentExecution(overrides?: Partial<any>) {
    return {
      id: `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      projectId: 'proj_test_123',
      agentName: 'TestAgent',
      agentType: 'test',
      status: 'completed',
      startedAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      ...overrides
    };
  }
  
  static user(overrides?: Partial<any>) {
    return {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      email: 'test@example.com',
      role: 'user',
      createdAt: new Date().toISOString(),
      ...overrides
    };
  }
}

// 비동기 테스트 헬퍼
export async function waitFor(
  condition: () => boolean | Promise<boolean>,
  timeout = 5000,
  interval = 100
): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  throw new Error('Timeout waiting for condition');
}

// 테스트 타이머 헬퍼
export class TestTimer {
  private timers: NodeJS.Timeout[] = [];
  
  setTimeout(fn: () => void, delay: number): NodeJS.Timeout {
    const timer = setTimeout(fn, delay);
    this.timers.push(timer);
    return timer;
  }
  
  clearAll(): void {
    this.timers.forEach(timer => clearTimeout(timer));
    this.timers = [];
  }
}

// 테스트 환경 변수 설정
export function setupTestEnvironment(vars: Record<string, string>): () => void {
  const original = { ...process.env };
  
  Object.entries(vars).forEach(([key, value]) => {
    process.env[key] = value;
  });
  
  return () => {
    process.env = original;
  };
}