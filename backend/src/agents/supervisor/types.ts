export interface Intent {
  type: string;
  description: string;
  confidence: number;
  entities: Record<string, any>;
  context: Record<string, any>;
}

export interface Decision {
  agentName: string;
  confidence: number;
  reasoning: string;
  alternativeAgents?: string[];
}

export interface WorkflowPlan {
  id: string;
  name: string;
  steps: WorkflowPlanStep[];
  estimatedDuration: number;
  requiredAgents: string[];
}

export interface WorkflowPlanStep {
  id: string;
  name: string;
  agents: string[];
  parallel: boolean;
  task: any;
  dependencies: string[];
}