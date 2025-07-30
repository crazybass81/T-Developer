// Task 1.14.2: 메시지 처리 엔진
import { EventEmitter } from 'events';

interface MessageHandler {
  handle(message: any): Promise<void>;
}

export class MessageProcessor extends EventEmitter {
  private handlers: Map<string, MessageHandler> = new Map();
  private processing = false;

  registerHandler(messageType: string, handler: MessageHandler): void {
    this.handlers.set(messageType, handler);
  }

  async processMessage(message: any): Promise<void> {
    const messageType = message.type || 'default';
    const handler = this.handlers.get(messageType);
    
    if (!handler) {
      throw new Error(`No handler for message type: ${messageType}`);
    }

    try {
      await handler.handle(message);
      this.emit('messageProcessed', { messageType, success: true });
    } catch (error) {
      this.emit('messageProcessed', { messageType, success: false, error });
      throw error;
    }
  }

  async startProcessing(queueManager: any, queueName: string): Promise<void> {
    this.processing = true;
    
    while (this.processing) {
      try {
        const messages = await queueManager.receiveMessages(queueName, 5);
        
        for (const message of messages) {
          await this.processMessage(message.body);
          await queueManager.deleteMessage(queueName, message.receiptHandle);
        }
        
        if (messages.length === 0) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      } catch (error) {
        this.emit('error', error);
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }

  stop(): void {
    this.processing = false;
  }
}