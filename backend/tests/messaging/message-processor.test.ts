// Test 1.14.2: MessageProcessor tests
import { MessageProcessor } from '../../src/messaging/message-processor';

describe('MessageProcessor', () => {
  let processor: MessageProcessor;
  let mockHandler: any;

  beforeEach(() => {
    processor = new MessageProcessor();
    mockHandler = { handle: jest.fn() };
  });

  test('should register and use handler', async () => {
    processor.registerHandler('test-type', mockHandler);
    
    await processor.processMessage({ type: 'test-type', data: 'test' });
    
    expect(mockHandler.handle).toHaveBeenCalledWith({ type: 'test-type', data: 'test' });
  });

  test('should emit messageProcessed event on success', async () => {
    const eventSpy = jest.fn();
    processor.on('messageProcessed', eventSpy);
    processor.registerHandler('test', mockHandler);
    
    await processor.processMessage({ type: 'test' });
    
    expect(eventSpy).toHaveBeenCalledWith({ messageType: 'test', success: true });
  });

  test('should emit error event on handler failure', async () => {
    const eventSpy = jest.fn();
    processor.on('messageProcessed', eventSpy);
    mockHandler.handle.mockRejectedValue(new Error('Handler failed'));
    processor.registerHandler('test', mockHandler);
    
    await expect(processor.processMessage({ type: 'test' }))
      .rejects.toThrow('Handler failed');
    
    expect(eventSpy).toHaveBeenCalledWith({ 
      messageType: 'test', 
      success: false, 
      error: expect.any(Error) 
    });
  });

  test('should throw error for unknown message type', async () => {
    await expect(processor.processMessage({ type: 'unknown' }))
      .rejects.toThrow('No handler for message type: unknown');
  });

  test('should stop processing', () => {
    processor.stop();
    expect((processor as any).processing).toBe(false);
  });
});