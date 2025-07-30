import { BaseMigration, MigrationResult, MigrationContext } from '../base-migration';
import { DynamoDBClient, CreateTableCommand } from '@aws-sdk/client-dynamodb';

export class InitialSchemaMigration extends BaseMigration {
  readonly version = '001';
  readonly description = 'Create initial T-Developer tables';

  constructor(private dynamoClient: DynamoDBClient) {
    super();
  }

  async up(context: MigrationContext): Promise<MigrationResult> {
    const startTime = Date.now();
    const errors: string[] = [];

    try {
      if (context.dryRun) {
        return this.createResult(true, 1, [], startTime);
      }

      // Create main table
      await this.dynamoClient.send(new CreateTableCommand({
        TableName: 'T-Developer-Main',
        KeySchema: [
          { AttributeName: 'PK', KeyType: 'HASH' },
          { AttributeName: 'SK', KeyType: 'RANGE' }
        ],
        AttributeDefinitions: [
          { AttributeName: 'PK', AttributeType: 'S' },
          { AttributeName: 'SK', AttributeType: 'S' },
          { AttributeName: 'GSI1PK', AttributeType: 'S' },
          { AttributeName: 'GSI1SK', AttributeType: 'S' }
        ],
        GlobalSecondaryIndexes: [{
          IndexName: 'GSI1',
          KeySchema: [
            { AttributeName: 'GSI1PK', KeyType: 'HASH' },
            { AttributeName: 'GSI1SK', KeyType: 'RANGE' }
          ],
          Projection: { ProjectionType: 'ALL' },
          ProvisionedThroughput: {
            ReadCapacityUnits: 5,
            WriteCapacityUnits: 5
          }
        }],
        BillingMode: 'PAY_PER_REQUEST'
      }));

      return this.createResult(true, 1, [], startTime);
    } catch (error) {
      errors.push(error.message);
      return this.createResult(false, 0, errors, startTime);
    }
  }

  async down(context: MigrationContext): Promise<MigrationResult> {
    const startTime = Date.now();
    
    if (context.dryRun) {
      return this.createResult(true, 1, [], startTime);
    }

    // In production, we typically don't drop tables
    return this.createResult(true, 0, ['Table drop skipped for safety'], startTime);
  }
}