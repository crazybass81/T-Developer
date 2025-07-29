export { ConnectionPool, DynamoDBPool, RedisPool, BedrockPool, PoolManager } from './connection-pool';
export { DatabaseOptimizer } from './database-optimizer';
export { CacheManager, MultiLevelCache } from './cache-manager';
export { QueueManager, JobWorker, AgentExecutionWorker, JobType, JobPriority } from './job-queue';
export { LambdaOptimizer, DynamicImportManager, PrefetchManager, backendWebpackConfig, frontendViteConfig } from './bundle-optimizer';

// Initialize performance systems
export async function initializePerformanceSystems(): Promise<void> {
  const poolManager = PoolManager.getInstance();
  const queueManager = new QueueManager();
  await queueManager.initialize();
  console.log('✅ Performance systems initialized');
}