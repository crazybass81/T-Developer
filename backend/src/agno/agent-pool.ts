import { v4 as uuidv4 } from 'uuid';

interface PoolConfig {
  minSize: number;
  maxSize: number;
  idleTimeout: number;
  preWarm: boolean;
}

interface AgentStats {
  available: number;
  inUse: number;
  total: number;
  created: number;
  destroyed: number;
}

class AgentPool {
  private available: any[] = [];
  private inUse: Map<string, any> = new Map();
  private config: PoolConfig;
  private stats: AgentStats;

  constructor(config: PoolConfig) {
    this.config = config;
    this.stats = { available: 0, inUse: 0, total: 0, created: 0, destroyed: 0 };
    
    if (config.preWarm) {
      this.warmUp();
    }
  }

  private async warmUp(): Promise<void> {
    const promises = [];
    for (let i = 0; i < this.config.minSize; i++) {
      promises.push(this.createAgent());
    }
    
    const agents = await Promise.all(promises);
    this.available.push(...agents);
    this.stats.available = agents.length;
    this.stats.total = agents.length;
  }

  async getAgent(): Promise<any> {
    if (this.available.length > 0) {
      const agent = this.available.pop()!;
      const id = this.generateId();
      this.inUse.set(id, { ...agent, poolId: id });
      
      this.stats.available--;
      this.stats.inUse++;
      
      return { ...agent, poolId: id };
    }

    if (this.inUse.size >= this.config.maxSize) {
      throw new Error('Agent pool exhausted');
    }

    const agent = await this.createAgent();
    const id = this.generateId();
    this.inUse.set(id, { ...agent, poolId: id });
    
    this.stats.inUse++;
    this.stats.total++;
    
    return { ...agent, poolId: id };
  }

  async releaseAgent(agentId: string): Promise<void> {
    const agent = this.inUse.get(agentId);
    if (!agent) return;

    this.inUse.delete(agentId);
    this.stats.inUse--;

    await this.resetAgent(agent);

    if (this.available.length < this.config.maxSize) {
      delete agent.poolId;
      this.available.push(agent);
      this.stats.available++;
    } else {
      await this.destroyAgent(agent);
      this.stats.total--;
      this.stats.destroyed++;
    }
  }

  private async createAgent(): Promise<any> {
    const start = performance.now();
    
    const agent = {
      id: uuidv4(),
      created: Date.now(),
      lightweight: true,
      skipValidation: true,
      useCache: true
    };
    
    const duration = performance.now() - start;
    
    if (duration > 0.003) {
      console.warn(`Agent creation took ${duration}ms`);
    }
    
    this.stats.created++;
    return agent;
  }

  private generateId(): string {
    return `pool_${uuidv4()}`;
  }

  private async resetAgent(agent: any): Promise<void> {
    agent.lastUsed = Date.now();
    agent.resetCount = (agent.resetCount || 0) + 1;
  }

  private async destroyAgent(agent: any): Promise<void> {
    // Cleanup agent resources
    delete agent.id;
    delete agent.created;
  }

  getStats(): AgentStats {
    return { ...this.stats };
  }
}

export { AgentPool, PoolConfig, AgentStats };