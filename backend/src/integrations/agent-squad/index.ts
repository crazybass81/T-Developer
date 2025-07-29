export { 
  SupervisorAgent, 
  WorkerAgent, 
  SquadConfig, 
  Task 
} from './squad-config';

export { 
  NLInputWorker, 
  UISelectionWorker, 
  ComponentSearchWorker,
  TDeveloperSquadFactory,
  SquadAgentAdapter
} from './squad-workers';

// Configuration helpers
export function createSquadConfig(
  supervisorName: string,
  role: 'orchestrator' | 'coordinator' | 'monitor' = 'orchestrator'
): SquadConfig {
  return {
    supervisorConfig: {
      name: supervisorName,
      role,
      capabilities: [
        'task_distribution',
        'load_balancing',
        'error_handling',
        'progress_monitoring'
      ]
    },
    workers: [
      {
        name: 'nl-input-workers',
        type: 'nl-input',
        count: 2,
        capabilities: ['natural_language_processing', 'requirement_analysis']
      },
      {
        name: 'ui-selection-workers',
        type: 'ui-selection',
        count: 1,
        capabilities: ['ui_framework_selection', 'design_system_selection']
      },
      {
        name: 'component-search-workers',
        type: 'component-search',
        count: 3,
        capabilities: ['component_discovery', 'registry_search']
      }
    ],
    communication: {
      protocol: 'redis',
      endpoint: process.env.REDIS_URL || 'redis://localhost:6379'
    }
  };
}

// Environment-based configuration
export function getSquadConfigFromEnv(): SquadConfig {
  return createSquadConfig(
    process.env.SQUAD_SUPERVISOR_NAME || 'T-Developer-Squad',
    (process.env.SQUAD_SUPERVISOR_ROLE as any) || 'orchestrator'
  );
}