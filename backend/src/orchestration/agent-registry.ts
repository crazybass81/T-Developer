interface AgentMetadata {
  name: string;
  version: string;
  capabilities: string[];
  maxConcurrent: number;
  timeout: number;
}

export class AgentRegistry {
  private agents: Map<string, AgentMetadata> = new Map();
  private instances: Map<string, any> = new Map();
  
  async register(metadata: AgentMetadata): Promise<void> {
    this.agents.set(metadata.name, metadata);
    await this.persistToDatabase(metadata);
    console.log(`✅ Agent metadata registered: ${metadata.name}`);
  }
  
  async getAgent(name: string): Promise<any> {
    if (!this.instances.has(name)) {
      await this.instantiateAgent(name);
    }
    return this.instances.get(name);
  }
  
  getRegisteredAgents(): string[] {
    return Array.from(this.agents.keys());
  }
  
  private async instantiateAgent(name: string): Promise<void> {
    const metadata = this.agents.get(name);
    if (!metadata) {
      throw new Error(`Agent ${name} not found`);
    }
    
    // 동적 에이전트 인스턴스 생성
    const agentInstance = {
      name: metadata.name,
      version: metadata.version,
      capabilities: metadata.capabilities,
      execute: async (task: any) => {
        console.log(`Executing task with ${name}:`, task);
        return { result: 'success', agent: name, task };
      }
    };
    
    this.instances.set(name, agentInstance);
  }
  
  private async persistToDatabase(metadata: AgentMetadata): Promise<void> {
    // DynamoDB에 메타데이터 저장 (추후 구현)
    console.log(`Persisting metadata for ${metadata.name}`);
  }
}