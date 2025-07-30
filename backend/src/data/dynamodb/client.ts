import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';

export interface DynamoDBConfig {
  region: string;
  endpoint?: string;
  maxRetries?: number;
  timeout?: number;
}

export class DynamoDBConnectionManager {
  private client!: DynamoDBDocumentClient;
  private config: DynamoDBConfig;
  
  constructor(config: DynamoDBConfig) {
    this.config = config;
    this.initializeClient();
  }
  
  private initializeClient(): void {
    const baseClient = new DynamoDBClient({
      region: this.config.region,
      endpoint: this.config.endpoint,
      maxAttempts: this.config.maxRetries || 3,
      requestHandler: {
        requestTimeout: this.config.timeout || 5000
      }
    });
    
    this.client = DynamoDBDocumentClient.from(baseClient, {
      marshallOptions: {
        convertEmptyValues: false,
        removeUndefinedValues: true
      },
      unmarshallOptions: {
        wrapNumbers: false
      }
    });
  }
  
  getClient(): DynamoDBDocumentClient {
    return this.client;
  }
  
  async healthCheck(): Promise<{ status: string; latency: number }> {
    const start = Date.now();
    
    try {
      await this.client.send({
        name: 'ListTablesCommand',
        input: { Limit: 1 }
      } as any);
      
      return {
        status: 'healthy',
        latency: Date.now() - start
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        latency: Date.now() - start
      };
    }
  }
}