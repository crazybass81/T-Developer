#!/usr/bin/env node
import { Command } from 'commander';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { MigrationManager } from './migration-manager';
import { InitialSchemaMigration } from './migrations/001-initial-schema';
import { AddAgentMetricsMigration } from './migrations/002-add-agent-metrics';

const program = new Command();

async function setupMigrationManager(): Promise<MigrationManager> {
  const dynamoClient = new DynamoDBClient({ region: process.env.AWS_REGION || 'us-east-1' });
  const docClient = DynamoDBDocumentClient.from(dynamoClient);
  
  const manager = new MigrationManager(docClient);
  
  // Register migrations
  manager.registerMigration(new InitialSchemaMigration(dynamoClient));
  manager.registerMigration(new AddAgentMetricsMigration(docClient));
  
  return manager;
}

program
  .name('t-dev-migrate')
  .description('T-Developer database migration tool')
  .version('1.0.0');

program
  .command('up')
  .description('Run pending migrations')
  .option('--target <version>', 'Target version to migrate to')
  .option('--dry-run', 'Show what would be migrated without executing')
  .action(async (options) => {
    const manager = await setupMigrationManager();
    const results = await manager.runMigrations(options.target, options.dryRun);
    
    console.log('Migration Results:');
    results.forEach((result, index) => {
      console.log(`  ${index + 1}. ${result.success ? '✅' : '❌'} ${result.migratedCount} items (${result.duration}ms)`);
      if (result.errors.length > 0) {
        result.errors.forEach(error => console.log(`     Error: ${error}`));
      }
    });
  });

program
  .command('down')
  .description('Rollback to target version')
  .requiredOption('--target <version>', 'Target version to rollback to')
  .action(async (options) => {
    const manager = await setupMigrationManager();
    const results = await manager.rollback(options.target);
    
    console.log('Rollback Results:');
    results.forEach((result, index) => {
      console.log(`  ${index + 1}. ${result.success ? '✅' : '❌'} ${result.migratedCount} items (${result.duration}ms)`);
    });
  });

program.parse();