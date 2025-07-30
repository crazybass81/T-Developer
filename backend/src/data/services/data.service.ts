import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { UserRepository } from '../repositories/user.repository';
import { ProjectRepository } from '../repositories/project.repository';
import { RedisCache } from '../../cache/redis-cache';

export class DataService {
  private docClient: DynamoDBDocumentClient;
  private cache: RedisCache;
  
  public users: UserRepository;
  public projects: ProjectRepository;
  
  constructor() {
    // Initialize DynamoDB
    const dynamoClient = new DynamoDBClient({
      region: process.env.AWS_REGION || 'us-east-1'
    });
    
    this.docClient = DynamoDBDocumentClient.from(dynamoClient, {
      marshallOptions: {
        convertEmptyValues: false,
        removeUndefinedValues: true
      }
    });
    
    // Initialize Redis Cache
    this.cache = new RedisCache({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD
    });
    
    // Initialize repositories
    this.users = new UserRepository(this.docClient);
    this.projects = new ProjectRepository(this.docClient);
  }
  
  getCache(): RedisCache {
    return this.cache;
  }
  
  async healthCheck(): Promise<{ dynamodb: boolean; redis: boolean }> {
    const health = { dynamodb: false, redis: false };
    
    try {
      // Test DynamoDB
      await this.docClient.send({
        input: { TableName: 'T-Developer-Main' },
        name: 'DescribeTableCommand'
      } as any);
      health.dynamodb = true;
    } catch (error) {
      console.error('DynamoDB health check failed:', error);
    }
    
    try {
      // Test Redis
      await this.cache.set('health-check', 'ok', { ttl: 10 });
      const result = await this.cache.get('health-check');
      health.redis = result === 'ok';
      await this.cache.del('health-check');
    } catch (error) {
      console.error('Redis health check failed:', error);
    }
    
    return health;
  }
  
  async disconnect(): Promise<void> {
    await this.cache.disconnect();
  }
}