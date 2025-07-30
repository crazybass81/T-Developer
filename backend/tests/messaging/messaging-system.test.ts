// Test 1.14: MessagingSystem integration tests
import { MessagingSystem } from '../../src/messaging';

// Mock all dependencies
jest.mock('@aws-sdk/client-sqs');
jest.mock('@aws-sdk/client-eventbridge');

describe('MessagingSystem', () => {
  let messagingSystem: MessagingSystem;

  beforeEach(() => {
    process.env.AGENT_TASKS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123/agent-tasks';
    process.env.NOTIFICATIONS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123/notifications';
    process.env.DLQ_URL = 'https://sqs.us-east-1.amazonaws.com/123/dlq';
    
    messagingSystem = new MessagingSystem();
  });

  test('should initialize successfully', async () => {
    await messagingSystem.initialize();
    
    expect(messagingSystem.queueManager).toBeDefined();
    expect(messagingSystem.processor).toBeDefined();
    expect(messagingSystem.eventBus).toBeDefined();
    expect(messagingSystem.router).toBeDefined();
  });

  test('should send message with routing', async () => {
    const mockSend = jest.fn().mockResolvedValue({});
    (messagingSystem.queueManager as any).sqsClient.send = mockSend;
    
    await messagingSystem.sendMessage('agent-task', { agentId: '123' }, 'high');
    
    expect(mockSend).toHaveBeenCalled();
  });

  test('should stop processing', () => {
    messagingSystem.stop();
    
    expect((messagingSystem.processor as any).processing).toBe(false);
  });
});

// Integration test with mock AWS services
describe('MessagingSystem Integration', () => {
  test('should handle complete message flow', async () => {
    const system = new MessagingSystem();
    await system.initialize();

    // Mock successful operations
    const mockSend = jest.fn().mockResolvedValue({});
    (system.queueManager as any).sqsClient.send = mockSend;
    (system.eventBus as any).eventBridge.send = mockSend;

    // Send message
    await system.sendMessage('agent-task', {
      agentId: 'test-agent',
      agentType: 'nl-input',
      data: 'test data'
    });

    // Verify message was sent
    expect(mockSend).toHaveBeenCalled();
  });
});