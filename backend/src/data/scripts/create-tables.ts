#!/usr/bin/env node
/**
 * T-Developer DynamoDB Table Creation Script
 * 테이블 생성 및 초기화 스크립트
 */

import { 
  DynamoDBClient, 
  CreateTableCommand, 
  DescribeTableCommand,
  ListTablesCommand,
  CreateTableCommandInput,
  AttributeDefinition,
  KeySchemaElement,
  GlobalSecondaryIndex,
  LocalSecondaryIndex,
  Tag,
  BillingMode,
  StreamSpecification,
  SSESpecification,
  TimeToLiveSpecification
} from '@aws-sdk/client-dynamodb';
import { T_DEVELOPER_TABLE, TableDesign } from '../schemas/single-table-design';

const client = new DynamoDBClient({
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.DYNAMODB_ENDPOINT || undefined // For local development
});

/**
 * Convert our TableDesign to AWS CreateTableCommandInput
 */
function buildCreateTableInput(design: TableDesign): CreateTableCommandInput {
  const attributeDefinitions: AttributeDefinition[] = [
    {
      AttributeName: design.partitionKey.name,
      AttributeType: design.partitionKey.type
    }
  ];
  
  const keySchema: KeySchemaElement[] = [
    {
      AttributeName: design.partitionKey.name,
      KeyType: 'HASH'
    }
  ];
  
  // Add sort key if exists
  if (design.sortKey) {
    attributeDefinitions.push({
      AttributeName: design.sortKey.name,
      AttributeType: design.sortKey.type
    });
    keySchema.push({
      AttributeName: design.sortKey.name,
      KeyType: 'RANGE'
    });
  }
  
  // Build GSI definitions
  const globalSecondaryIndexes: GlobalSecondaryIndex[] = design.globalSecondaryIndexes.map(gsi => {
    // Add GSI attributes to definitions
    if (!attributeDefinitions.find(attr => attr.AttributeName === gsi.partitionKey.name)) {
      attributeDefinitions.push({
        AttributeName: gsi.partitionKey.name,
        AttributeType: gsi.partitionKey.type
      });
    }
    
    if (gsi.sortKey && !attributeDefinitions.find(attr => attr.AttributeName === gsi.sortKey.name)) {
      attributeDefinitions.push({
        AttributeName: gsi.sortKey.name,
        AttributeType: gsi.sortKey.type
      });
    }
    
    const gsiKeySchema: KeySchemaElement[] = [
      {
        AttributeName: gsi.partitionKey.name,
        KeyType: 'HASH'
      }
    ];
    
    if (gsi.sortKey) {
      gsiKeySchema.push({
        AttributeName: gsi.sortKey.name,
        KeyType: 'RANGE'
      });
    }
    
    return {
      IndexName: gsi.indexName,
      KeySchema: gsiKeySchema,
      Projection: {
        ProjectionType: gsi.projection,
        NonKeyAttributes: gsi.includedAttributes
      },
      ProvisionedThroughput: gsi.throughput ? {
        ReadCapacityUnits: gsi.throughput.readCapacityUnits,
        WriteCapacityUnits: gsi.throughput.writeCapacityUnits
      } : undefined
    };
  });
  
  // Build LSI definitions
  const localSecondaryIndexes: LocalSecondaryIndex[] | undefined = design.localSecondaryIndexes?.map(lsi => {
    // Add LSI sort key to definitions
    if (!attributeDefinitions.find(attr => attr.AttributeName === lsi.sortKey.name)) {
      attributeDefinitions.push({
        AttributeName: lsi.sortKey.name,
        AttributeType: lsi.sortKey.type
      });
    }
    
    return {
      IndexName: lsi.indexName,
      KeySchema: [
        {
          AttributeName: design.partitionKey.name,
          KeyType: 'HASH'
        },
        {
          AttributeName: lsi.sortKey.name,
          KeyType: 'RANGE'
        }
      ],
      Projection: {
        ProjectionType: lsi.projection,
        NonKeyAttributes: lsi.includedAttributes
      }
    };
  });
  
  // Add other referenced attributes
  ['CreatedAt', 'UpdatedAt', 'Status', 'EntityType', 'EntityId', 'Version', 'Priority'].forEach(attrName => {
    const attr = design.attributes.find(a => a.name === attrName);
    if (attr && !attributeDefinitions.find(a => a.AttributeName === attrName)) {
      attributeDefinitions.push({
        AttributeName: attrName,
        AttributeType: attr.type
      });
    }
  });
  
  // Build tags
  const tags: Tag[] = design.tags ? Object.entries(design.tags).map(([key, value]) => ({
    Key: key,
    Value: value
  })) : [];
  
  // Build stream specification
  const streamSpecification: StreamSpecification | undefined = design.streamSpecification ? {
    StreamEnabled: design.streamSpecification.streamEnabled,
    StreamViewType: design.streamSpecification.streamViewType
  } : undefined;
  
  // Build SSE specification
  const sseSpecification: SSESpecification = {
    Enabled: true,
    SSEType: 'AES256'
  };
  
  const input: CreateTableCommandInput = {
    TableName: design.tableName,
    AttributeDefinitions: attributeDefinitions,
    KeySchema: keySchema,
    GlobalSecondaryIndexes: globalSecondaryIndexes.length > 0 ? globalSecondaryIndexes : undefined,
    LocalSecondaryIndexes: localSecondaryIndexes,
    BillingMode: BillingMode.PAY_PER_REQUEST, // On-demand billing
    StreamSpecification: streamSpecification,
    SSESpecification: sseSpecification,
    Tags: tags.length > 0 ? tags : undefined
  };
  
  return input;
}

/**
 * Check if table exists
 */
async function tableExists(tableName: string): Promise<boolean> {
  try {
    await client.send(new DescribeTableCommand({ TableName: tableName }));
    return true;
  } catch (error: any) {
    if (error.name === 'ResourceNotFoundException') {
      return false;
    }
    throw error;
  }
}

/**
 * Wait for table to become active
 */
async function waitForTableActive(tableName: string, maxWaitTime: number = 60000): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < maxWaitTime) {
    try {
      const response = await client.send(new DescribeTableCommand({ TableName: tableName }));
      
      if (response.Table?.TableStatus === 'ACTIVE') {
        console.log(`✅ Table ${tableName} is active`);
        return;
      }
      
      console.log(`⏳ Waiting for table ${tableName} to become active... (status: ${response.Table?.TableStatus})`);
    } catch (error) {
      console.error(`Error checking table status:`, error);
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  throw new Error(`Timeout waiting for table ${tableName} to become active`);
}

/**
 * Create table with TTL
 */
async function enableTTL(tableName: string, ttlAttribute: string): Promise<void> {
  try {
    const { UpdateTimeToLiveCommand } = await import('@aws-sdk/client-dynamodb');
    
    const command = new UpdateTimeToLiveCommand({
      TableName: tableName,
      TimeToLiveSpecification: {
        AttributeName: ttlAttribute,
        Enabled: true
      }
    });
    
    await client.send(command);
    console.log(`✅ TTL enabled on attribute ${ttlAttribute}`);
  } catch (error: any) {
    if (error.name === 'ValidationException' && error.message.includes('already enabled')) {
      console.log(`ℹ️ TTL already enabled on ${ttlAttribute}`);
    } else {
      console.error(`⚠️ Failed to enable TTL:`, error.message);
    }
  }
}

/**
 * Main function to create all tables
 */
async function createTables(): Promise<void> {
  console.log('🚀 Starting T-Developer table creation...\n');
  
  try {
    // Check if table already exists
    const exists = await tableExists(T_DEVELOPER_TABLE.tableName);
    
    if (exists) {
      console.log(`ℹ️ Table ${T_DEVELOPER_TABLE.tableName} already exists`);
      
      // Verify table structure
      const response = await client.send(new DescribeTableCommand({ 
        TableName: T_DEVELOPER_TABLE.tableName 
      }));
      
      console.log(`\n📊 Table Details:`);
      console.log(`  - Status: ${response.Table?.TableStatus}`);
      console.log(`  - Item Count: ${response.Table?.ItemCount || 0}`);
      console.log(`  - Size: ${response.Table?.TableSizeBytes || 0} bytes`);
      console.log(`  - GSIs: ${response.Table?.GlobalSecondaryIndexes?.length || 0}`);
      console.log(`  - LSIs: ${response.Table?.LocalSecondaryIndexes?.length || 0}`);
      console.log(`  - Streams: ${response.Table?.StreamSpecification?.StreamEnabled ? 'Enabled' : 'Disabled'}`);
      
      return;
    }
    
    // Create the table
    console.log(`📦 Creating table ${T_DEVELOPER_TABLE.tableName}...`);
    const input = buildCreateTableInput(T_DEVELOPER_TABLE);
    
    const command = new CreateTableCommand(input);
    const response = await client.send(command);
    
    console.log(`✅ Table creation initiated`);
    console.log(`  - Table ARN: ${response.TableDescription?.TableArn}`);
    
    // Wait for table to become active
    await waitForTableActive(T_DEVELOPER_TABLE.tableName);
    
    // Enable TTL if configured
    if (T_DEVELOPER_TABLE.ttl?.enabled) {
      await enableTTL(T_DEVELOPER_TABLE.tableName, T_DEVELOPER_TABLE.ttl.attributeName);
    }
    
    console.log(`\n🎉 Table ${T_DEVELOPER_TABLE.tableName} created successfully!`);
    
    // Print access patterns for reference
    console.log(`\n📋 Access Patterns:`);
    console.log(`  - Main table: PK/SK queries`);
    console.log(`  - GSI1: User/Project relationships`);
    console.log(`  - GSI2: Agent/Task relationships`);
    console.log(`  - GSI3: Time-based queries`);
    console.log(`  - GSI4: Status-based queries`);
    console.log(`  - GSI5: Entity type queries`);
    console.log(`  - LSI1: Version tracking`);
    console.log(`  - LSI2: Priority-based sorting`);
    
  } catch (error) {
    console.error('❌ Error creating tables:', error);
    throw error;
  }
}

/**
 * Delete table (for cleanup/testing)
 */
async function deleteTable(tableName: string): Promise<void> {
  try {
    const { DeleteTableCommand } = await import('@aws-sdk/client-dynamodb');
    
    console.log(`🗑️ Deleting table ${tableName}...`);
    await client.send(new DeleteTableCommand({ TableName: tableName }));
    console.log(`✅ Table ${tableName} deleted`);
  } catch (error: any) {
    if (error.name === 'ResourceNotFoundException') {
      console.log(`ℹ️ Table ${tableName} does not exist`);
    } else {
      throw error;
    }
  }
}

/**
 * List all tables
 */
async function listTables(): Promise<void> {
  try {
    const response = await client.send(new ListTablesCommand({}));
    console.log('\n📋 Available Tables:');
    response.TableNames?.forEach(name => {
      console.log(`  - ${name}`);
    });
  } catch (error) {
    console.error('❌ Error listing tables:', error);
  }
}

// Parse command line arguments
const command = process.argv[2];

switch (command) {
  case 'create':
    createTables().catch(console.error);
    break;
  case 'delete':
    deleteTable(T_DEVELOPER_TABLE.tableName).catch(console.error);
    break;
  case 'list':
    listTables().catch(console.error);
    break;
  case 'recreate':
    deleteTable(T_DEVELOPER_TABLE.tableName)
      .then(() => createTables())
      .catch(console.error);
    break;
  default:
    console.log('Usage: ts-node create-tables.ts [create|delete|list|recreate]');
    console.log('  create   - Create all tables');
    console.log('  delete   - Delete all tables');
    console.log('  list     - List all tables');
    console.log('  recreate - Delete and recreate all tables');
    process.exit(1);
}

export { createTables, deleteTable, tableExists, waitForTableActive };