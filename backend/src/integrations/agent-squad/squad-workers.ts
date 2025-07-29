import { WorkerAgent, Task } from './squad-config';
import { BaseAgent } from '../../agents/framework/base-agent';

// T-Developer specific worker implementations
export class NLInputWorker extends WorkerAgent {
  constructor() {
    super('nl-input', ['natural_language_processing', 'requirement_analysis']);
  }
  
  protected async process(task: Task): Promise<any> {
    console.log(`Processing NL input task: ${task.id}`);
    
    // Simulate natural language processing
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      structured_requirements: {
        project_type: 'web_application',
        features: ['user_auth', 'data_storage'],
        technologies: ['react', 'nodejs'],
        complexity: 'medium'
      },
      confidence: 0.85,
      processed_at: new Date().toISOString()
    };
  }
}

export class UISelectionWorker extends WorkerAgent {
  constructor() {
    super('ui-selection', ['ui_framework_selection', 'design_system_selection']);
  }
  
  protected async process(task: Task): Promise<any> {
    console.log(`Processing UI selection task: ${task.id}`);
    
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return {
      ui_framework: 'react',
      design_system: 'material-ui',
      component_library: '@mui/material',
      reasoning: 'Best fit for project requirements',
      processed_at: new Date().toISOString()
    };
  }
}

export class ComponentSearchWorker extends WorkerAgent {
  constructor() {
    super('component-search', ['component_discovery', 'registry_search']);
  }
  
  protected async process(task: Task): Promise<any> {
    console.log(`Processing component search task: ${task.id}`);
    
    await new Promise(resolve => setTimeout(resolve, 1200));
    
    return {
      found_components: [
        {
          name: 'react-auth-component',
          version: '2.1.0',
          registry: 'npm',
          match_score: 0.92
        },
        {
          name: 'user-dashboard-template',
          version: '1.5.3',
          registry: 'npm',
          match_score: 0.87
        }
      ],
      search_metadata: {
        total_searched: 1500,
        total_found: 25,
        top_matches: 2
      },
      processed_at: new Date().toISOString()
    };
  }
}

// Squad factory for T-Developer agents
export class TDeveloperSquadFactory {
  static createSquad(): {
    supervisor: any;
    workers: WorkerAgent[];
  } {
    const { SupervisorAgent } = require('./squad-config');
    
    const supervisor = new SupervisorAgent({
      name: 'T-Developer-Supervisor',
      role: 'orchestrator' as const,
      capabilities: [
        'task_distribution',
        'load_balancing',
        'error_handling',
        'progress_monitoring'
      ]
    });
    
    const workers = [
      new NLInputWorker(),
      new UISelectionWorker(),
      new ComponentSearchWorker()
    ];
    
    return { supervisor, workers };
  }
  
  static async setupSquad(): Promise<any> {
    const { supervisor, workers } = this.createSquad();
    
    // Add workers to supervisor
    for (const worker of workers) {
      await supervisor.addWorker(worker);
    }
    
    console.log('T-Developer squad setup completed');
    console.log('Squad status:', supervisor.getSquadStatus());
    
    return supervisor;
  }
}

// Integration with T-Developer agent framework
export class SquadAgentAdapter extends BaseAgent {
  private supervisor: any;
  
  constructor(supervisor: any) {
    super('squad-adapter', '1.0.0');
    this.supervisor = supervisor;
  }
  
  protected initialize(): void {
    this.registerCapability({
      name: 'squad_orchestration',
      description: 'Orchestrate tasks using Agent Squad',
      inputSchema: {
        type: 'object',
        properties: {
          tasks: { type: 'array' }
        }
      },
      outputSchema: {
        type: 'object',
        properties: {
          results: { type: 'array' }
        }
      },
      version: '1.0.0'
    });
  }
  
  protected async process(message: any): Promise<any> {
    const { payload } = message;
    
    switch (payload.action) {
      case 'orchestrate_tasks':
        return this.orchestrateTasks(payload.tasks);
      
      case 'get_squad_status':
        return this.supervisor.getSquadStatus();
      
      default:
        throw new Error(`Unknown action: ${payload.action}`);
    }
  }
  
  private async orchestrateTasks(tasks: any[]): Promise<any> {
    const results = [];
    
    for (const taskData of tasks) {
      const task: Task = {
        id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: taskData.type,
        capability: taskData.capability,
        payload: taskData.payload,
        priority: taskData.priority || 1
      };
      
      try {
        await this.supervisor.distributeTask(task);
        results.push({
          taskId: task.id,
          status: 'distributed',
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        results.push({
          taskId: task.id,
          status: 'failed',
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        });
      }
    }
    
    return {
      orchestrated_tasks: results,
      squad_status: this.supervisor.getSquadStatus()
    };
  }
}