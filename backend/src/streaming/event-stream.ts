import { EventEmitter } from 'events';
import { DynamoDBStreamEvent, DynamoDBRecord } from 'aws-lambda';
import { KinesisClient, PutRecordCommand } from '@aws-sdk/client-kinesis';

export interface StreamEvent {
  id: string;
  type: string;
  source: string;
  timestamp: Date;
  data: any;
  metadata?: Record<string, any>;
}

export interface StreamConfig {
  streamName: string;
  partitionKey: string;
  batchSize?: number;
  maxRetries?: number;
}

export class EventStream extends EventEmitter {
  private kinesis: KinesisClient;
  private buffer: StreamEvent[] = [];
  private flushTimer?: NodeJS.Timeout;

  constructor(private config: StreamConfig) {
    super();
    this.kinesis = new KinesisClient({ region: process.env.AWS_REGION });
    this.startBufferFlush();
  }

  async publish(event: StreamEvent): Promise<void> {
    this.buffer.push(event);
    
    if (this.buffer.length >= (this.config.batchSize || 100)) {
      await this.flush();
    }
  }

  private async flush(): Promise<void> {
    if (this.buffer.length === 0) return;

    const events = this.buffer.splice(0);
    
    for (const event of events) {
      try {
        await this.kinesis.send(new PutRecordCommand({
          StreamName: this.config.streamName,
          PartitionKey: this.config.partitionKey,
          Data: Buffer.from(JSON.stringify(event))
        }));
        
        this.emit('published', event);
      } catch (error) {
        this.emit('error', error, event);
      }
    }
  }

  private startBufferFlush(): void {
    this.flushTimer = setInterval(() => {
      this.flush();
    }, 5000); // Flush every 5 seconds
  }

  async close(): Promise<void> {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    await this.flush();
  }
}

export class DynamoDBStreamProcessor {
  private eventStream: EventStream;

  constructor(streamConfig: StreamConfig) {
    this.eventStream = new EventStream(streamConfig);
  }

  async processRecord(record: DynamoDBRecord): Promise<void> {
    const event: StreamEvent = {
      id: record.eventID || '',
      type: record.eventName || 'UNKNOWN',
      source: 'dynamodb',
      timestamp: new Date(record.dynamodb?.ApproximateCreationDateTime || Date.now()),
      data: {
        keys: record.dynamodb?.Keys,
        newImage: record.dynamodb?.NewImage,
        oldImage: record.dynamodb?.OldImage
      },
      metadata: {
        tableName: record.eventSourceARN?.split('/')[1],
        sequenceNumber: record.dynamodb?.SequenceNumber
      }
    };

    await this.eventStream.publish(event);
  }

  async processStream(event: DynamoDBStreamEvent): Promise<void> {
    for (const record of event.Records) {
      await this.processRecord(record);
    }
  }
}

export class EventStreamManager {
  private streams: Map<string, EventStream> = new Map();

  createStream(name: string, config: StreamConfig): EventStream {
    const stream = new EventStream(config);
    this.streams.set(name, stream);
    return stream;
  }

  getStream(name: string): EventStream | undefined {
    return this.streams.get(name);
  }

  async closeAll(): Promise<void> {
    for (const stream of this.streams.values()) {
      await stream.close();
    }
    this.streams.clear();
  }
}