import { BaseMigration, MigrationResult, MigrationContext } from './base-migration';
import { DynamoDBDocumentClient, PutCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';

export interface MigrationRecord {
  version: string;
  appliedAt: Date;
  success: boolean;
  duration: number;
}

export class MigrationManager {
  private migrations: Map<string, BaseMigration> = new Map();
  private tableName = 'T-Developer-Migrations';

  constructor(private docClient: DynamoDBDocumentClient) {}

  registerMigration(migration: BaseMigration): void {
    this.migrations.set(migration.version, migration);
  }

  async runMigrations(targetVersion?: string, dryRun: boolean = false): Promise<MigrationResult[]> {
    const appliedVersions = await this.getAppliedVersions();
    const pendingMigrations = this.getPendingMigrations(appliedVersions, targetVersion);
    
    const results: MigrationResult[] = [];
    
    for (const migration of pendingMigrations) {
      const context: MigrationContext = {
        version: migration.version,
        timestamp: new Date(),
        dryRun
      };
      
      try {
        const result = await migration.up(context);
        results.push(result);
        
        if (result.success && !dryRun) {
          await this.recordMigration({
            version: migration.version,
            appliedAt: new Date(),
            success: true,
            duration: result.duration
          });
        }
      } catch (error) {
        results.push({
          success: false,
          migratedCount: 0,
          errors: [error.message],
          duration: 0
        });
        break; // Stop on first failure
      }
    }
    
    return results;
  }

  async rollback(targetVersion: string): Promise<MigrationResult[]> {
    const appliedVersions = await this.getAppliedVersions();
    const migrationsToRollback = this.getMigrationsToRollback(appliedVersions, targetVersion);
    
    const results: MigrationResult[] = [];
    
    for (const migration of migrationsToRollback.reverse()) {
      const context: MigrationContext = {
        version: migration.version,
        timestamp: new Date(),
        dryRun: false
      };
      
      try {
        const result = await migration.down(context);
        results.push(result);
        
        if (result.success) {
          await this.removeMigrationRecord(migration.version);
        }
      } catch (error) {
        results.push({
          success: false,
          migratedCount: 0,
          errors: [error.message],
          duration: 0
        });
        break;
      }
    }
    
    return results;
  }

  private async getAppliedVersions(): Promise<string[]> {
    try {
      const result = await this.docClient.send(new QueryCommand({
        TableName: this.tableName,
        KeyConditionExpression: 'PK = :pk',
        ExpressionAttributeValues: {
          ':pk': 'MIGRATION'
        }
      }));
      
      return (result.Items || [])
        .filter(item => item.success)
        .map(item => item.version);
    } catch (error) {
      return []; // Table might not exist yet
    }
  }

  private getPendingMigrations(appliedVersions: string[], targetVersion?: string): BaseMigration[] {
    const allMigrations = Array.from(this.migrations.values())
      .sort((a, b) => a.version.localeCompare(b.version));
    
    return allMigrations.filter(migration => {
      const isApplied = appliedVersions.includes(migration.version);
      const isWithinTarget = !targetVersion || migration.version <= targetVersion;
      return !isApplied && isWithinTarget;
    });
  }

  private getMigrationsToRollback(appliedVersions: string[], targetVersion: string): BaseMigration[] {
    return appliedVersions
      .filter(version => version > targetVersion)
      .map(version => this.migrations.get(version))
      .filter(Boolean) as BaseMigration[];
  }

  private async recordMigration(record: MigrationRecord): Promise<void> {
    await this.docClient.send(new PutCommand({
      TableName: this.tableName,
      Item: {
        PK: 'MIGRATION',
        SK: record.version,
        version: record.version,
        appliedAt: record.appliedAt.toISOString(),
        success: record.success,
        duration: record.duration
      }
    }));
  }

  private async removeMigrationRecord(version: string): Promise<void> {
    await this.docClient.send(new PutCommand({
      TableName: this.tableName,
      Item: {
        PK: 'MIGRATION',
        SK: version,
        version,
        rolledBackAt: new Date().toISOString(),
        success: false,
        duration: 0
      }
    }));
  }
}