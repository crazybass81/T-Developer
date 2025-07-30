class AgentRegistry {
  constructor() {
    this.agents = new Map();
    this.instances = new Map();
    this.metadata = new Map();
  }
  
  async register(agentMetadata) {
    this.agents.set(agentMetadata.name, agentMetadata);
    this.metadata.set(agentMetadata.name, {
      ...agentMetadata,
      registeredAt: new Date(),
      lastUsed: null,
      usageCount: 0
    });
    
    await this.persistToDatabase(agentMetadata);
  }
  
  async getAgent(name) {
    if (!this.instances.has(name)) {
      await this.instantiateAgent(name);
    }
    
    // Update usage stats
    const metadata = this.metadata.get(name);
    if (metadata) {
      metadata.lastUsed = new Date();
      metadata.usageCount++;
    }
    
    return this.instances.get(name);
  }
  
  async instantiateAgent(name) {
    const metadata = this.agents.get(name);
    if (!metadata) {
      throw new Error(`Agent ${name} not found`);
    }
    
    // Mock agent instantiation
    const agent = {
      name,
      metadata,
      execute: async (task) => ({
        result: `Executed by ${name}`,
        task,
        agent: name,
        timestamp: new Date()
      })
    };
    
    this.instances.set(name, agent);
  }
  
  listAgents() {
    return Array.from(this.agents.values());
  }
  
  getAgentMetadata(name) {
    return this.metadata.get(name);
  }
  
  async unregister(name) {
    this.agents.delete(name);
    this.instances.delete(name);
    this.metadata.delete(name);
    
    console.log(`Agent ${name} unregistered`);
  }
  
  getStats() {
    return {
      totalAgents: this.agents.size,
      activeInstances: this.instances.size,
      agentUsage: Array.from(this.metadata.values()).map(m => ({
        name: m.name,
        usageCount: m.usageCount,
        lastUsed: m.lastUsed
      }))
    };
  }
  
  async persistToDatabase(metadata) {
    // Mock database persistence
    console.log(`Persisting agent metadata: ${metadata.name}`);
  }
}

module.exports = { AgentRegistry };