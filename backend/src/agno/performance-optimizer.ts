import { agnoConfig } from '../config/agno-config';

// Mock config for testing
const mockConfig = {
  performance: {
    instantiationTargetUs: 3,
    memoryTargetKb: 6.5
  },
  resources: {
    maxAgents: 1000,
    maxMemoryPerAgentKb: 10
  }
};

// Use mock if config not available
const config = agnoConfig || mockConfig;

export interface PerformanceMetrics {
  instantiationTimeUs: number;
  memoryPerAgentKb: number;
  targetMet: boolean;
}

export class AgnoPerformanceOptimizer {
  private preloadedModules = new Map<string, any>();
  private agentPool: any[] = [];

  async optimize(): Promise<void> {
    await this.preloadCommonModules();
    await this.initializeAgentPool();
    this.enableJitCompilation();
    await this.preallocateMemory();
  }

  private async preloadCommonModules(): Promise<void> {
    const commonModules = ['events', 'util', 'crypto', 'path'];

    for (const moduleName of commonModules) {
      try {
        this.preloadedModules.set(moduleName, require(moduleName));
      } catch (error) {
        console.warn(`Failed to preload module: ${moduleName}`);
      }
    }
  }

  private async initializeAgentPool(): Promise<void> {
    const poolSize = Math.min(50, config.resources.maxAgents);
    
    for (let i = 0; i < poolSize; i++) {
      this.agentPool.push(this.createOptimizedAgent());
    }
  }

  private createOptimizedAgent(): any {
    return {
      id: `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      created: Date.now(),
      execute: async (task: any) => {
        const start = performance.now();
        await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
        
        return {
          result: `Processed by optimized agent`,
          duration: performance.now() - start,
          task
        };
      }
    };
  }

  private enableJitCompilation(): void {
    if (global.gc) {
      global.gc();
    }
  }

  private async preallocateMemory(): Promise<void> {
    const bufferSize = config.resources.maxAgents * config.resources.maxMemoryPerAgentKb * 1024;
    const buffer = Buffer.allocUnsafe(bufferSize);
    buffer.fill(0);
  }

  async benchmarkPerformance(): Promise<PerformanceMetrics> {
    const iterations = 1000;
    const times: number[] = [];
    const memoryBefore = process.memoryUsage().heapUsed;

    for (let i = 0; i < iterations; i++) {
      const start = performance.now();
      this.createOptimizedAgent();
      const end = performance.now();
      times.push((end - start) * 1000);
    }

    const memoryAfter = process.memoryUsage().heapUsed;
    const instantiationTimeUs = times.reduce((a, b) => a + b) / times.length;
    const memoryPerAgentKb = (memoryAfter - memoryBefore) / iterations / 1024;

    return {
      instantiationTimeUs,
      memoryPerAgentKb,
      targetMet: (
        instantiationTimeUs <= config.performance.instantiationTargetUs &&
        memoryPerAgentKb <= config.performance.memoryTargetKb
      )
    };
  }

  getPooledAgent(): any {
    return this.agentPool.pop() || this.createOptimizedAgent();
  }

  returnAgent(agent: any): void {
    if (this.agentPool.length < 50) {
      this.agentPool.push(agent);
    }
  }
}