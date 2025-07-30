import { DynamoDBClient, CreateTableCommand, DescribeTableCommand } from '@aws-sdk/client-dynamodb';
import { T_DEVELOPER_TABLE } from '../schemas/single-table-design';

export class TableCreator {
  private dynamoDB: DynamoDBClient;
  
  constructor(region: string = process.env.AWS_REGION || 'us-east-1') {
    this.dynamoDB = new DynamoDBClient({ region });
  }
  
  async createMainTable(): Promise<void> {
    const params = {
      TableName: T_DEVELOPER_TABLE.tableName,
      KeySchema: [
        { AttributeName: 'PK', KeyType: 'HASH' },
        { AttributeName: 'SK', KeyType: 'RANGE' }
      ],
      AttributeDefinitions: [
        { AttributeName: 'PK', AttributeType: 'S' },
        { AttributeName: 'SK', AttributeType: 'S' },
        { AttributeName: 'GSI1PK', AttributeType: 'S' },
        { AttributeName: 'GSI1SK', AttributeType: 'S' },
        { AttributeName: 'GSI2PK', AttributeType: 'S' },
        { AttributeName: 'GSI2SK', AttributeType: 'S' }
      ],
      GlobalSecondaryIndexes: T_DEVELOPER_TABLE.globalSecondaryIndexes.map(gsi => ({
        IndexName: gsi.indexName,
        KeySchema: [
          { AttributeName: gsi.partitionKey.name, KeyType: 'HASH' },
          { AttributeName: gsi.sortKey!.name, KeyType: 'RANGE' }
        ],
        Projection: { ProjectionType: gsi.projection },
        ProvisionedThroughput: {
          ReadCapacityUnits: 5,
          WriteCapacityUnits: 5
        }
      })),
      BillingMode: 'PAY_PER_REQUEST',
      StreamSpecification: {
        StreamEnabled: true,
        StreamViewType: 'NEW_AND_OLD_IMAGES'
      },
      Tags: [
        { Key: 'Project', Value: 'T-Developer' },
        { Key: 'Environment', Value: process.env.NODE_ENV || 'development' }
      ]
    };
    
    try {
      await this.dynamoDB.send(new CreateTableCommand(params));
      console.log(`✅ Table ${T_DEVELOPER_TABLE.tableName} created successfully`);
      
      await this.waitForTableActive(T_DEVELOPER_TABLE.tableName);
      
    } catch (error: any) {
      if (error.name === 'ResourceInUseException') {
        console.log(`ℹ️ Table ${T_DEVELOPER_TABLE.tableName} already exists`);
      } else {
        throw error;
      }
    }
  }
  
  private async waitForTableActive(tableName: string): Promise<void> {
    let isActive = false;
    let attempts = 0;
    
    while (!isActive && attempts < 30) {
      try {
        const result = await this.dynamoDB.send(new DescribeTableCommand({
          TableName: tableName
        }));
        
        if (result.Table?.TableStatus === 'ACTIVE') {
          isActive = true;
        } else {
          await new Promise(resolve => setTimeout(resolve, 2000));
          attempts++;
        }
      } catch (error) {
        attempts++;
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    if (!isActive) {
      throw new Error(`Table ${tableName} did not become active within timeout`);
    }
  }
}

// CLI execution
if (require.main === module) {
  const creator = new TableCreator();
  creator.createMainTable()
    .then(() => console.log('✅ All tables created successfully'))
    .catch(console.error);
}