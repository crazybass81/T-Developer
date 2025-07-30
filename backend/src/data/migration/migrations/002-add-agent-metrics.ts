import { BaseMigration, MigrationResult, MigrationContext } from '../base-migration';
import { DynamoDBDocumentClient, ScanCommand, UpdateCommand } from '@aws-sdk/lib-dynamodb';

export class AddAgentMetricsMigration extends BaseMigration {
  readonly version = '002';
  readonly description = 'Add metrics fields to existing agents';

  constructor(private docClient: DynamoDBDocumentClient) {
    super();
  }

  async up(context: MigrationContext): Promise<MigrationResult> {
    const startTime = Date.now();
    let migratedCount = 0;
    const errors: string[] = [];

    try {
      // Find all agent records
      const agents = await this.scanAgents();
      
      if (context.dryRun) {
        return this.createResult(true, agents.length, [], startTime);
      }

      // Update agents with default metrics
      await this.batchProcess(agents, async (agent) => {
        if (!agent.metrics) {
          await this.docClient.send(new UpdateCommand({
            TableName: 'T-Developer-Main',
            Key: { PK: agent.PK, SK: agent.SK },
            UpdateExpression: 'SET metrics = :metrics',
            ExpressionAttributeValues: {
              ':metrics': {
                executionCount: 0,
                successCount: 0,
                failureCount: 0,
                averageExecutionTime: 0,
                lastExecutionTime: 0
              }
            }
          }));
          migratedCount++;
        }
      });

      return this.createResult(true, migratedCount, [], startTime);
    } catch (error) {
      errors.push(error.message);
      return this.createResult(false, migratedCount, errors, startTime);
    }
  }

  async down(context: MigrationContext): Promise<MigrationResult> {
    const startTime = Date.now();
    let migratedCount = 0;

    if (context.dryRun) {
      const agents = await this.scanAgents();
      return this.createResult(true, agents.length, [], startTime);
    }

    // Remove metrics field from agents
    const agents = await this.scanAgents();
    await this.batchProcess(agents, async (agent) => {
      if (agent.metrics) {
        await this.docClient.send(new UpdateCommand({
          TableName: 'T-Developer-Main',
          Key: { PK: agent.PK, SK: agent.SK },
          UpdateExpression: 'REMOVE metrics'
        }));
        migratedCount++;
      }
    });

    return this.createResult(true, migratedCount, [], startTime);
  }

  private async scanAgents(): Promise<any[]> {
    const result = await this.docClient.send(new ScanCommand({
      TableName: 'T-Developer-Main',
      FilterExpression: 'begins_with(PK, :prefix)',
      ExpressionAttributeValues: {
        ':prefix': 'AGENT#'
      }
    }));
    
    return result.Items || [];
  }
}