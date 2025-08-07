/**
 * Migration Manager for Data Schema Changes
 * Handles database schema migrations and data transformations
 */

import { SingleTableClient } from '../dynamodb/single-table';

export interface Migration {
  id: string;
  version: string;
  description: string;
  up: () => Promise<void>;
  down: () => Promise<void>;
  createdAt: string;
}

export interface MigrationRecord {
  id: string;
  version: string;
  appliedAt: string;
  executionTime: number;
}

export class MigrationManager {
  private client: SingleTableClient;
  private migrations: Map<string, Migration> = new Map();

  constructor(client: SingleTableClient) {
    this.client = client;
  }

  public addMigration(migration: Migration): void {
    this.migrations.set(migration.id, migration);
  }

  public async runPendingMigrations(): Promise<MigrationRecord[]> {
    const applied: MigrationRecord[] = [];
    const appliedMigrations = await this.getAppliedMigrations();
    const appliedIds = new Set(appliedMigrations.map(m => m.id));

    for (const migration of this.migrations.values()) {
      if (!appliedIds.has(migration.id)) {
        const startTime = Date.now();
        await migration.up();
        const executionTime = Date.now() - startTime;

        const record: MigrationRecord = {
          id: migration.id,
          version: migration.version,
          appliedAt: new Date().toISOString(),
          executionTime
        };

        await this.recordMigration(record);
        applied.push(record);
      }
    }

    return applied;
  }

  private async getAppliedMigrations(): Promise<MigrationRecord[]> {
    try {
      const result = await this.client.query({
        pk: 'MIGRATION#RECORDS',
        skBeginsWith: 'MIGRATION#'
      });

      return result.items.map(item => JSON.parse(item.Data));
    } catch {
      return [];
    }
  }

  private async recordMigration(record: MigrationRecord): Promise<void> {
    await this.client.putItem({
      PK: 'MIGRATION#RECORDS',
      SK: `MIGRATION#${record.id}`,
      EntityType: 'MIGRATION',
      EntityId: record.id,
      Status: 'COMPLETED',
      CreatedAt: record.appliedAt,
      UpdatedAt: record.appliedAt,
      Data: JSON.stringify(record)
    });
  }
}