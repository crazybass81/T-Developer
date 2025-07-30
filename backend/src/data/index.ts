import { DynamoDBConnectionManager, SingleTableDesign, DynamoDBQueryOptimizer, TransactionManager } from './dynamodb';

// Initialize DynamoDB system
export function initializeDynamoDB() {
  const config = {
    region: process.env.AWS_REGION || 'us-east-1',
    endpoint: process.env.DYNAMODB_ENDPOINT,
    maxRetries: 3,
    timeout: 5000
  };
  
  const connectionManager = new DynamoDBConnectionManager(config);
  const client = connectionManager.getClient();
  
  const singleTable = new SingleTableDesign(client);
  const queryOptimizer = new DynamoDBQueryOptimizer();
  const transactionManager = new TransactionManager(client);
  
  console.log('✅ DynamoDB system initialized');
  
  return {
    connectionManager,
    client,
    singleTable,
    queryOptimizer,
    transactionManager
  };
}

export * from './dynamodb';