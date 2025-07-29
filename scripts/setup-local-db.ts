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
        Projection: { ProjectionType: 'ALL' }
      },
    ],
    BillingMode: 'PAY_PER_REQUEST'
  });

  // Components 테이블
  const componentsTable = new CreateTableCommand({
    TableName: 'T-Developer-Components',
    KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
    AttributeDefinitions: [{ AttributeName: 'id', AttributeType: 'S' }],
    BillingMode: 'PAY_PER_REQUEST'
  });

  // Agent Executions 테이블
  const executionsTable = new CreateTableCommand({
    TableName: 'T-Developer-Executions',
    KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
    AttributeDefinitions: [{ AttributeName: 'id', AttributeType: 'S' }],
    BillingMode: 'PAY_PER_REQUEST'
  });

  const tables = [
    { command: projectsTable, name: 'Projects' },
    { command: componentsTable, name: 'Components' },
    { command: executionsTable, name: 'Executions' }
  ];

  for (const table of tables) {
    try {
      await client.send(table.command);
      console.log(`✅ ${table.name} 테이블 생성 완료`);
    } catch (error: any) {
      if (error.name === 'ResourceInUseException') {
        console.log(`ℹ️  ${table.name} 테이블이 이미 존재합니다`);
      } else {
        console.error(`❌ ${table.name} 테이블 생성 실패:`, error);
      }
    }
  }
}

createTables();