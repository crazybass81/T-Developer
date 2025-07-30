export interface MigrationResult {
  success: boolean;
  migratedCount: number;
  errors: string[];
  duration: number;
}

export interface MigrationContext {
  version: string;
  timestamp: Date;
  dryRun: boolean;
}

export abstract class BaseMigration {
  abstract readonly version: string;
  abstract readonly description: string;

  abstract up(context: MigrationContext): Promise<MigrationResult>;
  abstract down(context: MigrationContext): Promise<MigrationResult>;

  protected createResult(
    success: boolean,
    migratedCount: number = 0,
    errors: string[] = [],
    startTime: number = Date.now()
  ): MigrationResult {
    return {
      success,
      migratedCount,
      errors,
      duration: Date.now() - startTime
    };
  }

  protected async batchProcess<T>(
    items: T[],
    processor: (item: T) => Promise<void>,
    batchSize: number = 100
  ): Promise<void> {
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      await Promise.all(batch.map(processor));
    }
  }
}