#!/usr/bin/env ts-node
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
  console.log('🔧 DynamoDB 테이블 생성 중...');

  // Projects 테이블
  const projectsTable = new CreateTableCommand({
    TableName: 'T-Developer-Projects',
    KeySchema: [
      { AttributeName: 'id', KeyType: 'HASH' },
    ],
    AttributeDefinitions: [
      { AttributeName: 'id', AttributeType: 'S' },
      { AttributeName: 'userId', AttributeType: 'S' },
      { AttributeName: 'createdAt', AttributeType: 'S' },
    ],
    GlobalSecondaryIndexes: [
      {
        IndexName: 'UserIdIndex',
        KeySchema: [
          { AttributeName: 'userId', KeyType: 'HASH' },
          { AttributeName: 'createdAt', KeyType: 'RANGE' },
        ],
        Projection: { ProjectionType: 'ALL' },
        ProvisionedThroughput: {
          ReadCapacityUnits: 5,
          WriteCapacityUnits: 5,
        },
      },
    ],
    BillingMode: 'PAY_PER_REQUEST',
  });

  try {
    await client.send(projectsTable);
    console.log('✅ Projects 테이블 생성 완료');
  } catch (error: any) {
    if (error.name === 'ResourceInUseException') {
      console.log('ℹ️ Projects 테이블이 이미 존재합니다');
    } else {
      console.error('❌ Projects 테이블 생성 실패:', error.message);
    }
  }

  console.log('\n✅ 로컬 데이터베이스 설정 완료!');
  console.log('📋 접속 정보:');
  console.log('- DynamoDB Local: http://localhost:8000');
  console.log('- DynamoDB Admin: http://localhost:8001');
  console.log('- Redis: localhost:6379');
}

if (require.main === module) {
  createTables().catch(console.error);
}