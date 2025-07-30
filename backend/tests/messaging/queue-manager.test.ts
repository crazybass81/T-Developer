// Test 1.14.1: QueueManager tests
import { QueueManager } from '../../src/messaging/queue-manager';

// Mock AWS SDK
jest.mock('@aws-sdk/client-sqs', () => ({
  SQSClient: jest.fn().mockImplementation(() => ({
    send: jest.fn()
  })),
  SendMessageCommand: jest.fn(),
  ReceiveMessageCommand: jest.fn(),
  DeleteMessageCommand: jest.fn()
}));

describe('QueueManager', () => {
  let queueManager: QueueManager;
  let mockSend: jest.Mock;

  beforeEach(() => {
    process.env.AGENT_TASKS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123/agent-tasks';
    process.env.NOTIFICATIONS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123/notifications';
    process.env.DLQ_URL = 'https://sqs.us-east-1.amazonaws.com/123/dlq';
    
    queueManager = new QueueManager();
    mockSend = jest.fn();
    (queueManager as any).sqsClient.send = mockSend;
  });

  test('should send message successfully', async () => {
    mockSend.mockResolvedValue({});
    
    await queueManager.sendMessage('agent-tasks', { type: 'test', data: 'hello' });
    
    expect(mockSend).toHaveBeenCalledTimes(1);
  });

  test('should receive messages', async () => {
    const mockMessages = [{
      MessageId: '123',
      Body: JSON.stringify({ type: 'test' }),
      ReceiptHandle: 'receipt-123'
    }];
    
    mockSend.mockResolvedValue({ Messages: mockMessages });
    
    const messages = await queueManager.receiveMessages('agent-tasks');
    
    expect(messages).toHaveLength(1);
    expect(messages[0].body.type).toBe('test');
  });

  test('should delete message', async () => {
    mockSend.mockResolvedValue({});
    
    await queueManager.deleteMessage('agent-tasks', 'receipt-123');
    
    expect(mockSend).toHaveBeenCalledTimes(1);
  });

  test('should throw error for unknown queue', async () => {
    await expect(queueManager.sendMessage('unknown', {}))
      .rejects.toThrow('Queue not found: unknown');
  });
});