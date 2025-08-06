import { IntelligentRouter } from './intelligent-router';

// Example usage of IntelligentRouter
export class RoutingExample {
  private router = new IntelligentRouter();

  async setupExample() {
    // Register sample agents
    this.router.registerAgent({
      id: 'nl-agent-1',
      type: 'NLInputAgent',
      capabilities: ['text-analysis', 'requirement-extraction', 'nlp'],
      currentLoad: 2,
      maxCapacity: 10,
      performance: 0.85
    });

    this.router.registerAgent({
      id: 'code-agent-1',
      type: 'CodeGenerationAgent',
      capabilities: ['code-generation', 'typescript', 'react'],
      currentLoad: 5,
      maxCapacity: 8,
      performance: 0.92
    });

    this.router.registerAgent({
      id: 'ui-agent-1',
      type: 'UISelectionAgent',
      capabilities: ['ui-design', 'component-selection', 'react'],
      currentLoad: 1,
      maxCapacity: 6,
      performance: 0.78
    });

    console.log('✅ Agents registered');
  }

  async routeExampleTasks() {
    const tasks = [
      {
        id: 'task-1',
        type: 'text-analysis',
        description: 'Analyze user requirements from natural language',
        requirements: ['text-analysis', 'nlp'],
        priority: 1,
        createdAt: Date.now()
      },
      {
        id: 'task-2',
        type: 'code-generation',
        description: 'Generate React component code',
        requirements: ['code-generation', 'react'],
        priority: 2,
        createdAt: Date.now()
      },
      {
        id: 'task-3',
        type: 'ui-selection',
        description: 'Select appropriate UI framework',
        requirements: ['ui-design', 'component-selection'],
        priority: 1,
        createdAt: Date.now()
      }
    ];

    console.log('\n🔄 Routing tasks...');
    
    for (const task of tasks) {
      try {
        const selectedAgent = await this.router.routeTask(task);
        console.log(`✅ Task ${task.id} → Agent ${selectedAgent.id} (${selectedAgent.type})`);
        
        // Simulate agent load increase
        this.router.updateAgentLoad(selectedAgent.id, selectedAgent.currentLoad + 1);
      } catch (error) {
        console.log(`❌ Failed to route task ${task.id}: ${(error as Error).message}`);
      }
    }

    // Show routing statistics
    const stats = this.router.getRoutingStats();
    console.log('\n📊 Routing Statistics:');
    console.log(`- Total routed: ${stats.totalRouted}`);
    console.log(`- Average score: ${stats.avgScore.toFixed(3)}`);
    console.log('- Agent utilization:');
    Object.entries(stats.agentUtilization).forEach(([id, util]) => {
      console.log(`  - ${id}: ${(util * 100).toFixed(1)}%`);
    });
  }
}

// Run example if called directly
if (require.main === module) {
  const example = new RoutingExample();
  example.setupExample()
    .then(() => example.routeExampleTasks())
    .catch(console.error);
}