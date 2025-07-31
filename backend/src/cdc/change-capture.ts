import { DynamoDBStreamEvent, DynamoDBRecord } from 'aws-lambda';
import { EventEmitter } from 'events';

export interface ChangeEvent {
  id: string;
  eventName: 'INSERT' | 'MODIFY' | 'REMOVE';
  tableName: string;
  timestamp: Date;
  keys: Record<string, any>;
  oldImage?: Record<string, any>;
  newImage?: Record<string, any>;
  sequenceNumber: string;
}

export interface CDCConfig {
  batchSize: number;
  maxRetries: number;
  deadLetterQueue?: string;
  filterPatterns?: string[];
}

export class ChangeDataCapture extends EventEmitter {
  private buffer: ChangeEvent[] = [];
  private processing = false;

  constructor(private config: CDCConfig) {
    super();
  }

  async processStreamRecord(record: DynamoDBRecord): Promise<void> {
    const changeEvent = this.convertToChangeEvent(record);
    
    if (this.shouldProcess(changeEvent)) {
      this.buffer.push(changeEvent);
      
      if (this.buffer.length >= this.config.batchSize) {
        await this.processBatch();
      }
    }
  }

  private convertToChangeEvent(record: DynamoDBRecord): ChangeEvent {
    return {
      id: record.eventID || '',
      eventName: record.eventName as 'INSERT' | 'MODIFY' | 'REMOVE',
      tableName: this.extractTableName(record.eventSourceARN || ''),
      timestamp: new Date(record.dynamodb?.ApproximateCreationDateTime || Date.now()),
      keys: record.dynamodb?.Keys || {},
      oldImage: record.dynamodb?.OldImage,
      newImage: record.dynamodb?.NewImage,
      sequenceNumber: record.dynamodb?.SequenceNumber || ''
    };
  }

  private shouldProcess(event: ChangeEvent): boolean {
    if (!this.config.filterPatterns) return true;
    
    return this.config.filterPatterns.some(pattern => 
      event.tableName.includes(pattern)
    );
  }

  private async processBatch(): Promise<void> {
    if (this.processing || this.buffer.length === 0) return;
    
    this.processing = true;
    const batch = this.buffer.splice(0);
    
    try {
      for (const event of batch) {
        await this.processChangeEvent(event);
      }
    } catch (error) {
      this.emit('error', error, batch);
    } finally {
      this.processing = false;
    }
  }

  private async processChangeEvent(event: ChangeEvent): Promise<void> {
    this.emit('change', event);
    
    // Emit specific events based on operation type
    switch (event.eventName) {
      case 'INSERT':
        this.emit('insert', event);
        break;
      case 'MODIFY':
        this.emit('modify', event);
        break;
      case 'REMOVE':
        this.emit('remove', event);
        break;
    }
  }

  private extractTableName(arn: string): string {
    const parts = arn.split('/');
    return parts[1] || '';
  }

  async flush(): Promise<void> {
    await this.processBatch();
  }
}

export class CDCProcessor {
  private cdc: ChangeDataCapture;
  private handlers: Map<string, Function[]> = new Map();

  constructor(config: CDCConfig) {
    this.cdc = new ChangeDataCapture(config);
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.cdc.on('change', (event: ChangeEvent) => {
      this.handleChange(event);
    });
  }

  registerHandler(eventType: string, handler: Function): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    this.handlers.get(eventType)!.push(handler);
  }

  private async handleChange(event: ChangeEvent): Promise<void> {
    const handlers = this.handlers.get(event.eventName) || [];
    
    for (const handler of handlers) {
      try {
        await handler(event);
      } catch (error) {
        console.error('Handler error:', error);
      }
    }
  }

  async processStream(streamEvent: DynamoDBStreamEvent): Promise<void> {
    for (const record of streamEvent.Records) {
      await this.cdc.processStreamRecord(record);
    }
    await this.cdc.flush();
  }
}

export class CDCMetrics {
  private metrics = {
    eventsProcessed: 0,
    eventsPerSecond: 0,
    lastProcessedTime: Date.now(),
    errorCount: 0
  };

  recordEvent(): void {
    this.metrics.eventsProcessed++;
    this.updateRate();
  }

  recordError(): void {
    this.metrics.errorCount++;
  }

  private updateRate(): void {
    const now = Date.now();
    const timeDiff = (now - this.metrics.lastProcessedTime) / 1000;
    
    if (timeDiff > 0) {
      this.metrics.eventsPerSecond = 1 / timeDiff;
      this.metrics.lastProcessedTime = now;
    }
  }

  getMetrics(): typeof this.metrics {
    return { ...this.metrics };
  }
}