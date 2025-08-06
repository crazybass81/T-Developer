#!/usr/bin/env ts-node

import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { seedDevelopmentData } from '../backend/src/utils/data-generator';

async function main() {
  const client = new DynamoDBClient({
    endpoint: process.env.DYNAMODB_ENDPOINT || 'http://localhost:8000',
    region: process.env.AWS_REGION || 'us-east-1',
    credentials: {
      accessKeyId: 'local',
      secretAccessKey: 'local'
    }
  });

  const docClient = DynamoDBDocumentClient.from(client);

  try {
    await seedDevelopmentData(docClient);
    console.log('✅ Development data seeding completed successfully');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error seeding development data:', error);
    process.exit(1);
  }
}

main();