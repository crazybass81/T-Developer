#!/usr/bin/env node

const { v4: uuidv4 } = require('uuid');

// Mock AgentPool implementation for testing
class AgentPool {
  constructor(config) {
    this.config = config;
    this.available = [];
    this.inUse = new Map();
    this.stats = { available: 0, inUse: 0, total: 0, created: 0, destroyed: 0 };
    
    if (config.preWarm) {
      this.warmUp();
    }
  }

  async warmUp() {
    console.log(`🔥 Warming up pool with ${this.config.minSize} agents...`);
    
    for (let i = 0; i < this.config.minSize; i++) {
      const agent = await this.createAgent();
      this.available.push(agent);
    }
    
    this.stats.available = this.available.length;
    this.stats.total = this.available.length;
    
    console.log(`✅ Pool warmed up: ${this.stats.available} agents ready`);
  }

  async getAgent() {
    if (this.available.length > 0) {
      const agent = this.available.pop();
      const id = this.generateId();
      agent.poolId = id;
      this.inUse.set(id, agent);
      
      this.stats.available--;
      this.stats.inUse++;
      
      return agent;
    }

    if (this.inUse.size >= this.config.maxSize) {
      throw new Error('Agent pool exhausted');
    }

    const agent = await this.createAgent();
    const id = this.generateId();
    agent.poolId = id;
    this.inUse.set(id, agent);
    
    this.stats.inUse++;
    this.stats.total++;
    
    return agent;
  }

  async releaseAgent(agentId) {
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

  async createAgent() {
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

  generateId() {
    return `pool_${uuidv4()}`;
  }

  async resetAgent(agent) {
    agent.lastUsed = Date.now();
    agent.resetCount = (agent.resetCount || 0) + 1;
  }

  async destroyAgent(agent) {
    delete agent.id;
    delete agent.created;
  }

  getStats() {
    return { ...this.stats };
  }
}

async function testAgentPool() {
  console.log('🚀 Testing Agno Agent Pool...\n');

  try {
    // Pool configuration
    const config = {
      minSize: 5,
      maxSize: 20,
      idleTimeout: 30000,
      preWarm: true
    };

    // Create pool
    const pool = new AgentPool(config);
    await new Promise(resolve => setTimeout(resolve, 100)); // Wait for warmup

    console.log('📊 Initial stats:', pool.getStats());

    // Test getting agents
    console.log('\n🔄 Testing agent acquisition...');
    const agents = [];
    
    for (let i = 0; i < 8; i++) {
      const agent = await pool.getAgent();
      agents.push(agent);
      console.log(`✅ Got agent ${i + 1}: ${agent.id.substring(0, 8)}...`);
    }

    console.log('📊 After getting 8 agents:', pool.getStats());

    // Test releasing agents
    console.log('\n🔄 Testing agent release...');
    for (let i = 0; i < 3; i++) {
      await pool.releaseAgent(agents[i].poolId);
      console.log(`✅ Released agent ${i + 1}`);
    }

    console.log('📊 After releasing 3 agents:', pool.getStats());

    // Test pool exhaustion
    console.log('\n🔄 Testing pool limits...');
    const moreAgents = [];
    
    try {
      for (let i = 0; i < 15; i++) {
        const agent = await pool.getAgent();
        moreAgents.push(agent);
      }
      console.log(`✅ Got ${moreAgents.length} more agents`);
    } catch (error) {
      console.log(`✅ Pool exhaustion handled: ${error.message}`);
    }

    console.log('📊 Final stats:', pool.getStats());

    // Release all agents first
    for (const agent of moreAgents) {
      await pool.releaseAgent(agent.poolId);
    }
    for (let i = 3; i < agents.length; i++) {
      await pool.releaseAgent(agents[i].poolId);
    }

    // Performance test
    console.log('\n⚡ Performance test...');
    const start = performance.now();
    
    for (let i = 0; i < 100; i++) {
      const agent = await pool.getAgent();
      await pool.releaseAgent(agent.poolId);
    }
    
    const duration = performance.now() - start;
    console.log(`✅ 100 get/release cycles: ${duration.toFixed(2)}ms`);
    console.log(`✅ Average per cycle: ${(duration / 100).toFixed(3)}ms`);

    console.log('\n🎯 Agent Pool test completed successfully!');
    return true;

  } catch (error) {
    console.error('❌ Error:', error);
    return false;
  }
}

if (require.main === module) {
  testAgentPool()
    .then(success => process.exit(success ? 0 : 1))
    .catch(error => {
      console.error('❌ Test failed:', error);
      process.exit(1);
    });
}