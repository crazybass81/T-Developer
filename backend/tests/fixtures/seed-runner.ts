import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { TestDataSeeder } from './seed-data';

async function runSeeder() {
  console.log('🌱 테스트 데이터 시딩 시작...\n');

  const client = new DynamoDBClient({
    endpoint: 'http://localhost:8000',
    region: 'us-east-1',
    credentials: {
      accessKeyId: 'test',
      secretAccessKey: 'test'
    }
  });

  const docClient = DynamoDBDocumentClient.from(client);
  const seeder = new TestDataSeeder(docClient);

  try {
    await seeder.seedAll();
    console.log('\n🎉 테스트 데이터 시딩 완료!');
  } catch (error) {
    console.error('❌ 시딩 실패:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  runSeeder();
}