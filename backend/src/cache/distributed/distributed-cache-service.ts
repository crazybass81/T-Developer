import { RedisClusterManager } from './cluster-manager';
import { ReplicationManager } from './replication-manager';
import { SyncCoordinator } from './sync-coordinator';
import { ConsistentHashRing, HashNode } from './consistent-hash';

export interface DistributedCacheConfig {
  nodes: Array<{ host: string; port: number; weight?: number }>;
  replication: {
    factor: number;
    consistency: 'eventual' | 'strong' | 'quorum';
    syncInterval: number;
  };
  cluster: {
    healthCheckInterval: number;
    retryAttempts: number;
  };
}

export class DistributedCacheService {
  private clusterManager: RedisClusterManager;
  private replicationManager: ReplicationManager;
  private syncCoordinator: SyncCoordinator;
  private nodeId: string;

  constructor(private config: DistributedCacheConfig) {
    this.nodeId = `node-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.initialize();
  }

  private initialize(): void {
    // Initialize cluster manager
    this.clusterManager = new RedisClusterManager({
      nodes: this.config.nodes,
      options: {
        enableReadyCheck: true,
        maxRetriesPerRequest: this.config.cluster.retryAttempts
      },
      healthCheckInterval: this.config.cluster.healthCheckInterval
    });

    // Initialize replication manager
    const hashNodes: HashNode[] = this.config.nodes.map((node, index) => ({
      id: `${node.host}:${node.port}`,
      weight: node.weight || 1
    }));

    this.replicationManager = new ReplicationManager(
      this.clusterManager,
      this.config.replication,
      hashNodes
    );

    // Initialize sync coordinator
    this.syncCoordinator = new SyncCoordinator(
      this.clusterManager,
      this.nodeId,
      { strategy: 'last-write-wins' }
    );

    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.clusterManager.on('error', (error) => {
      console.error('Cluster error:', error);
    });

    this.syncCoordinator.on('eventApplied', (event) => {
      console.log('Sync event applied:', event);
    });

    this.syncCoordinator.on('nodeFailure', ({ nodeId }) => {
      console.warn(`Node ${nodeId} failed, initiating recovery`);
    });
  }

  // Core cache operations with distributed support
  async get(key: string): Promise<any> {
    try {
      return await this.replicationManager.get(key);
    } catch (error) {
      console.error(`Failed to get key ${key}:`, error);
      return null;
    }
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    try {
      await this.replicationManager.set(key, value, ttl);
      
      // Record sync event
      await this.syncCoordinator.recordEvent({
        type: 'set',
        key,
        value
      });
    } catch (error) {
      console.error(`Failed to set key ${key}:`, error);
      throw error;
    }
  }

  async del(key: string): Promise<void> {
    try {
      await this.clusterManager.del(key);
      
      // Record sync event
      await this.syncCoordinator.recordEvent({
        type: 'delete',
        key
      });
    } catch (error) {
      console.error(`Failed to delete key ${key}:`, error);
      throw error;
    }
  }

  async mget(keys: string[]): Promise<any[]> {
    try {
      const results = await Promise.all(
        keys.map(key => this.get(key))
      );
      return results;
    } catch (error) {
      console.error('Failed to mget keys:', error);
      return keys.map(() => null);
    }
  }

  async mset(pairs: Array<{ key: string; value: any; ttl?: number }>): Promise<void> {
    try {
      await Promise.all(
        pairs.map(({ key, value, ttl }) => this.set(key, value, ttl))
      );
    } catch (error) {
      console.error('Failed to mset pairs:', error);
      throw error;
    }
  }

  // T-Developer specific cache operations
  async cacheUser(userId: string, userData: any, ttl: number = 3600): Promise<void> {
    await this.set(`user:${userId}`, userData, ttl);
  }

  async getCachedUser(userId: string): Promise<any> {
    return await this.get(`user:${userId}`);
  }

  async cacheProject(projectId: string, projectData: any, ttl: number = 1800): Promise<void> {
    await this.set(`project:${projectId}`, projectData, ttl);
  }

  async getCachedProject(projectId: string): Promise<any> {
    return await this.get(`project:${projectId}`);
  }

  async cacheAgentResult(agentId: string, taskId: string, result: any, ttl: number = 900): Promise<void> {
    await this.set(`agent:${agentId}:task:${taskId}`, result, ttl);
  }

  async getCachedAgentResult(agentId: string, taskId: string): Promise<any> {
    return await this.get(`agent:${agentId}:task:${taskId}`);
  }

  // Cache invalidation with distributed coordination
  async invalidatePattern(pattern: string): Promise<number> {
    // This would need to be implemented with proper pattern matching
    // For now, we'll implement a simple prefix-based invalidation
    const keys = await this.findKeysByPattern(pattern);
    
    await Promise.all(keys.map(key => this.del(key)));
    
    return keys.length;
  }

  private async findKeysByPattern(pattern: string): Promise<string[]> {
    // Simplified pattern matching - in production, this would use Redis SCAN
    // For now, return empty array as this requires more complex implementation
    return [];
  }

  // Health and monitoring
  async getHealthStatus(): Promise<{
    cluster: Record<string, boolean>;
    sync: { inProgress: boolean; lastSync: number; eventCount: number };
    nodeId: string;
  }> {
    return {
      cluster: this.clusterManager.getHealthStatus(),
      sync: await this.syncCoordinator.getSyncStatus(),
      nodeId: this.nodeId
    };
  }

  async getStats(): Promise<{
    totalNodes: number;
    healthyNodes: number;
    replicationFactor: number;
    consistency: string;
  }> {
    const healthStatus = this.clusterManager.getHealthStatus();
    const healthyCount = Object.values(healthStatus).filter(Boolean).length;
    
    return {
      totalNodes: Object.keys(healthStatus).length,
      healthyNodes: healthyCount,
      replicationFactor: this.config.replication.factor,
      consistency: this.config.replication.consistency
    };
  }

  // Graceful shutdown
  async shutdown(): Promise<void> {
    console.log('Shutting down distributed cache service...');
    
    // Stop replication manager
    this.replicationManager.shutdown();
    
    // Shutdown cluster manager
    await this.clusterManager.shutdown();
    
    console.log('Distributed cache service shutdown complete');
  }
}