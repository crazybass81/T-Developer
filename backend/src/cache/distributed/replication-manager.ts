import { RedisClusterManager } from './cluster-manager';
import { ConsistentHashRing, HashNode } from './consistent-hash';

export interface ReplicationConfig {
  factor: number;
  consistency: 'eventual' | 'strong' | 'quorum';
  syncInterval: number;
}

export class ReplicationManager {
  private hashRing: ConsistentHashRing;
  private syncTimer: NodeJS.Timer;

  constructor(
    private cluster: RedisClusterManager,
    private config: ReplicationConfig,
    nodes: HashNode[]
  ) {
    this.hashRing = new ConsistentHashRing(nodes);
    this.startSyncProcess();
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    const nodes = this.hashRing.getNodes(key, this.config.factor);
    
    switch (this.config.consistency) {
      case 'strong':
        await this.strongConsistencyWrite(key, value, ttl, nodes);
        break;
      case 'quorum':
        await this.quorumWrite(key, value, ttl, nodes);
        break;
      case 'eventual':
        await this.eventualConsistencyWrite(key, value, ttl, nodes);
        break;
    }
  }

  async get(key: string): Promise<any> {
    const nodes = this.hashRing.getNodes(key, this.config.factor);
    
    switch (this.config.consistency) {
      case 'strong':
        return await this.strongConsistencyRead(key, nodes);
      case 'quorum':
        return await this.quorumRead(key, nodes);
      case 'eventual':
        return await this.eventualConsistencyRead(key, nodes);
    }
  }

  private async strongConsistencyWrite(
    key: string,
    value: any,
    ttl: number | undefined,
    nodes: HashNode[]
  ): Promise<void> {
    const promises = nodes.map(async (node) => {
      await this.cluster.set(`${node.id}:${key}`, value, ttl);
    });
    
    await Promise.all(promises);
  }

  private async quorumWrite(
    key: string,
    value: any,
    ttl: number | undefined,
    nodes: HashNode[]
  ): Promise<void> {
    const quorumSize = Math.floor(nodes.length / 2) + 1;
    const promises = nodes.map(async (node) => {
      try {
        await this.cluster.set(`${node.id}:${key}`, value, ttl);
        return { success: true, node: node.id };
      } catch (error) {
        return { success: false, node: node.id, error };
      }
    });
    
    const results = await Promise.all(promises);
    const successful = results.filter(r => r.success).length;
    
    if (successful < quorumSize) {
      throw new Error(`Quorum write failed: ${successful}/${quorumSize}`);
    }
  }

  private async eventualConsistencyWrite(
    key: string,
    value: any,
    ttl: number | undefined,
    nodes: HashNode[]
  ): Promise<void> {
    // Write to primary node immediately
    const primaryNode = nodes[0];
    await this.cluster.set(`${primaryNode.id}:${key}`, value, ttl);
    
    // Async replication to other nodes
    const replicationPromises = nodes.slice(1).map(async (node) => {
      try {
        await this.cluster.set(`${node.id}:${key}`, value, ttl);
      } catch (error) {
        // Log error but don't fail the operation
        console.error(`Replication failed for node ${node.id}:`, error);
      }
    });
    
    // Don't wait for replication
    Promise.all(replicationPromises);
  }

  private async strongConsistencyRead(key: string, nodes: HashNode[]): Promise<any> {
    const promises = nodes.map(async (node) => {
      try {
        return await this.cluster.get(`${node.id}:${key}`);
      } catch (error) {
        return null;
      }
    });
    
    const results = await Promise.all(promises);
    const validResults = results.filter(r => r !== null);
    
    if (validResults.length === 0) return null;
    
    // Return the most recent value (assuming timestamp-based versioning)
    return validResults[0];
  }

  private async quorumRead(key: string, nodes: HashNode[]): Promise<any> {
    const quorumSize = Math.floor(nodes.length / 2) + 1;
    const promises = nodes.map(async (node) => {
      try {
        return await this.cluster.get(`${node.id}:${key}`);
      } catch (error) {
        return null;
      }
    });
    
    const results = await Promise.all(promises);
    const validResults = results.filter(r => r !== null);
    
    if (validResults.length >= quorumSize) {
      return validResults[0];
    }
    
    return null;
  }

  private async eventualConsistencyRead(key: string, nodes: HashNode[]): Promise<any> {
    // Try primary node first
    const primaryNode = nodes[0];
    try {
      const value = await this.cluster.get(`${primaryNode.id}:${key}`);
      if (value !== null) return value;
    } catch (error) {
      // Continue to replicas
    }
    
    // Try replicas
    for (const node of nodes.slice(1)) {
      try {
        const value = await this.cluster.get(`${node.id}:${key}`);
        if (value !== null) return value;
      } catch (error) {
        continue;
      }
    }
    
    return null;
  }

  private startSyncProcess(): void {
    this.syncTimer = setInterval(async () => {
      await this.syncReplicas();
    }, this.config.syncInterval);
  }

  private async syncReplicas(): Promise<void> {
    // Implementation for periodic sync between replicas
    // This would involve comparing versions and resolving conflicts
  }

  async addNode(node: HashNode): Promise<void> {
    this.hashRing.addNode(node);
    // Trigger data redistribution
    await this.redistributeData();
  }

  async removeNode(nodeId: string): Promise<void> {
    this.hashRing.removeNode(nodeId);
    // Trigger data redistribution
    await this.redistributeData();
  }

  private async redistributeData(): Promise<void> {
    // Implementation for data redistribution when nodes are added/removed
    // This would involve moving data between nodes based on the new hash ring
  }

  shutdown(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
    }
  }
}