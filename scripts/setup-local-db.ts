/**
 * T-Developer MVP - Local Database Setup
 * 
 * 로컬 DynamoDB 테이블 생성
 * 
 * @author T-Developer Team
 * @created 2025-01-31
 */

import { DynamoDBClient, CreateTableCommand } from '@aws-sdk/client-dynamodb';

const client = new DynamoDBClient({
  endpoint: 'http://localhost:8000',
  region: 'us-east-1',
  credentials: {
    accessKeyId: 'local',
    secretAccessKey: 'local'
  }
});

async function createTables() {
  const tables = [
    {
      TableName: 'T-Developer-Projects',
      KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
      AttributeDefinitions: [
        { AttributeName: 'id', AttributeType: 'S' },
        { AttributeName: 'userId', AttributeType: 'S' },
        { AttributeName: 'createdAt', AttributeType: 'S' }
      ],
      GlobalSecondaryIndexes: [{
        IndexName: 'UserIdIndex',
        KeySchema: [
          { AttributeName: 'userId', KeyType: 'HASH' },
          { AttributeName: 'createdAt', KeyType: 'RANGE' }
        ],
        Projection: { ProjectionType: 'ALL' },
        ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 }
      }],
      BillingMode: 'PAY_PER_REQUEST'
    },
    {
      TableName: 'T-Developer-Users',
      KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
      AttributeDefinitions: [
        { AttributeName: 'id', AttributeType: 'S' },
        { AttributeName: 'email', AttributeType: 'S' }
      ],
      GlobalSecondaryIndexes: [{
        IndexName: 'EmailIndex',
        KeySchema: [{ AttributeName: 'email', KeyType: 'HASH' }],
        Projection: { ProjectionType: 'ALL' },
        ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 }
      }],
      BillingMode: 'PAY_PER_REQUEST'
    },
    {
      TableName: 'T-Developer-Components',
      KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
      AttributeDefinitions: [
        { AttributeName: 'id', AttributeType: 'S' },
        { AttributeName: 'category', AttributeType: 'S' },
        { AttributeName: 'name', AttributeType: 'S' }
      ],
      GlobalSecondaryIndexes: [{
        IndexName: 'CategoryIndex',
        KeySchema: [
          { AttributeName: 'category', KeyType: 'HASH' },
          { AttributeName: 'name', KeyType: 'RANGE' }
        ],
        Projection: { ProjectionType: 'ALL' },
        ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 }
      }],
      BillingMode: 'PAY_PER_REQUEST'
    }
  ];

  for (const table of tables) {
    try {
      await client.send(new CreateTableCommand(table));
      console.log(`✅ ${table.TableName} 테이블 생성 완료`);
    } catch (error: any) {
      if (error.name === 'ResourceInUseException') {
        console.log(`ℹ️ ${table.TableName} 테이블이 이미 존재합니다`);
      } else {
        console.error(`❌ ${table.TableName} 테이블 생성 실패:`, error);
      }
    }
  }
}

if (require.main === module) {
  createTables().then(() => {
    console.log('🎉 로컬 데이터베이스 설정 완료!');
    process.exit(0);
  }).catch(error => {
    console.error('💥 데이터베이스 설정 실패:', error);
    process.exit(1);
  });
}