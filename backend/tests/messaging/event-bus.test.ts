// Test 1.14.3: EventBus tests
import { EventBus, AgentEventBus } from '../../src/messaging/event-bus';

// Mock AWS SDK
jest.mock('@aws-sdk/client-eventbridge', () => ({
  EventBridgeClient: jest.fn().mockImplementation(() => ({
    send: jest.fn()
  })),
  PutEventsCommand: jest.fn()
}));

describe('EventBus', () => {
  let eventBus: EventBus;
  let mockSend: jest.Mock;

  beforeEach(() => {
    eventBus = new EventBus();
    mockSend = jest.fn();
    (eventBus as any).eventBridge.send = mockSend;
  });

  test('should publish single event', async () => {
    mockSend.mockResolvedValue({});
    
    await eventBus.publish({
      source: 'test-source',
      type: 'TestEvent',
      data: { message: 'hello' }
    });
    
    expect(mockSend).toHaveBeenCalledTimes(1);
  });

  test('should publish batch events', async () => {
    mockSend.mockResolvedValue({});
    
    const events = Array.from({ length: 15 }, (_, i) => ({
      source: 'test',
      type: 'Event',
      data: { id: i }
    }));
    
    await eventBus.publishBatch(events);
    
    expect(mockSend).toHaveBeenCalledTimes(2); // 10 + 5 events
  });
});

describe('AgentEventBus', () => {
  let agentEventBus: AgentEventBus;
  let mockSend: jest.Mock;

  beforeEach(() => {
    agentEventBus = new AgentEventBus();
    mockSend = jest.fn().mockResolvedValue({});
    (agentEventBus as any).eventBridge.send = mockSend;
  });

  test('should publish agent start event', async () => {
    await agentEventBus.publishAgentStart('agent-123', 'nl-input');
    
    expect(mockSend).toHaveBeenCalledTimes(1);
  });

  test('should publish agent complete event', async () => {
    await agentEventBus.publishAgentComplete('agent-123', { success: true });
    
    expect(mockSend).toHaveBeenCalledTimes(1);
  });

  test('should publish agent error event', async () => {
    await agentEventBus.publishAgentError('agent-123', 'Processing failed');
    
    expect(mockSend).toHaveBeenCalledTimes(1);
  });
});