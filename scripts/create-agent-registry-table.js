#!/usr/bin/env node

const { DynamoDBClient, CreateTableCommand, DescribeTableCommand } = require('@aws-sdk/client-dynamodb');

async function createAgentRegistryTable() {
  console.log('🗄️ Creating Agent Registry DynamoDB Table...\n');

  const client = new DynamoDBClient({ 
    region: process.env.AWS_REGION || 'us-east-1',
    endpoint: process.env.DYNAMODB_ENDPOINT || undefined
  });

  const tableName = 't-developer-agents';

  try {
    // Check if table already exists
    try {
      await client.send(new DescribeTableCommand({ TableName: tableName }));
      console.log(`✅ Table ${tableName} already exists`);
      return;
    } catch (error) {
      if (error.name !== 'ResourceNotFoundException') {
        throw error;
      }
    }

    // Create table
    const createParams = {
      TableName: tableName,
      KeySchema: [
        { AttributeName: 'name', KeyType: 'HASH' }
      ],
      AttributeDefinitions: [
        { AttributeName: 'name', AttributeType: 'S' },
        { AttributeName: 'status', AttributeType: 'S' }
      ],
      GlobalSecondaryIndexes: [
        {
          IndexName: 'StatusIndex',
          KeySchema: [
            { AttributeName: 'status', KeyType: 'HASH' }
          ],
          Projection: { ProjectionType: 'ALL' },
          ProvisionedThroughput: {
            ReadCapacityUnits: 5,
            WriteCapacityUnits: 5
          }
        }
      ],
      BillingMode: 'PAY_PER_REQUEST',
      Tags: [
        { Key: 'Project', Value: 'T-Developer' },
        { Key: 'Component', Value: 'AgentRegistry' }
      ]
    };

    await client.send(new CreateTableCommand(createParams));
    console.log(`✅ Table ${tableName} created successfully`);

    // Wait for table to be active
    console.log('⏳ Waiting for table to become active...');
    let tableStatus = 'CREATING';
    while (tableStatus !== 'ACTIVE') {
      await new Promise(resolve => setTimeout(resolve, 2000));
      const response = await client.send(new DescribeTableCommand({ TableName: tableName }));
      tableStatus = response.Table.TableStatus;
      console.log(`   Status: ${tableStatus}`);
    }

    console.log('\n🎉 Agent Registry table ready!');
    console.log(`📊 Table Details:`);
    console.log(`   - Name: ${tableName}`);
    console.log(`   - Primary Key: name (String)`);
    console.log(`   - GSI: StatusIndex on status`);
    console.log(`   - Billing: Pay-per-request`);

  } catch (error) {
    console.error('❌ Failed to create table:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  createAgentRegistryTable();
}

module.exports = { createAgentRegistryTable };