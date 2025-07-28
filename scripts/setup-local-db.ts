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
  } catch (error) {
    console.error('❌ Projects 테이블 생성 실패:', error);
  }
}

createTables();