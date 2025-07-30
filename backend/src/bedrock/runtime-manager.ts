// backend/src/bedrock/runtime-manager.ts
import { AgentCoreRuntime, AgentCoreConfig } from './agentcore-runtime';

export interface RuntimeInstance {
  id: string;
  runtime: AgentCoreRuntime;
  config: AgentCoreConfig;
  createdAt: Date;
  lastUsed: Date;
  sessionCount: number;
}

export class RuntimeManager {
  private runtimes: Map<string, RuntimeInstance> = new Map();
  private defaultConfig: Partial<AgentCoreConfig>;

  constructor() {
    this.defaultConfig = {
      region: process.env.AWS_BEDROCK_REGION || 'us-east-1',
      agentId: process.env.BEDROCK_AGENT_ID,
      agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID || 'TSTALIASID'
    };
  }

  createRuntime(config?: Partial<AgentCoreConfig>): string {
    const runtimeId = this.generateRuntimeId();
    const fullConfig = { ...this.defaultConfig, ...config } as AgentCoreConfig;
    
    const runtime = new AgentCoreRuntime(fullConfig);
    
    const instance: RuntimeInstance = {
      id: runtimeId,
      runtime,
      config: fullConfig,
      createdAt: new Date(),
      lastUsed: new Date(),
      sessionCount: 0
    };

    this.runtimes.set(runtimeId, instance);
    return runtimeId;
  }

  getRuntime(runtimeId: string): AgentCoreRuntime | null {
    const instance = this.runtimes.get(runtimeId);
    if (!instance) return null;

    instance.lastUsed = new Date();
    return instance.runtime;
  }

  async invokeAgent(
    runtimeId: string,
    inputText: string,
    sessionId?: string
  ): Promise<any> {
    const runtime = this.getRuntime(runtimeId);
    if (!runtime) {
      throw new Error(`Runtime not found: ${runtimeId}`);
    }

    const instance = this.runtimes.get(runtimeId)!;
    instance.sessionCount++;

    return await runtime.invokeAgent(inputText, sessionId);
  }

  removeRuntime(runtimeId: string): boolean {
    return this.runtimes.delete(runtimeId);
  }

  listRuntimes(): RuntimeInstance[] {
    return Array.from(this.runtimes.values());
  }

  getStats(): {
    totalRuntimes: number;
    totalSessions: number;
    oldestRuntime?: Date;
  } {
    const instances = Array.from(this.runtimes.values());
    
    return {
      totalRuntimes: instances.length,
      totalSessions: instances.reduce((sum, inst) => sum + inst.sessionCount, 0),
      oldestRuntime: instances.length > 0 
        ? new Date(Math.min(...instances.map(inst => inst.createdAt.getTime())))
        : undefined
    };
  }

  private generateRuntimeId(): string {
    return `runtime_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}