import { BaseModel } from './base.model';

export interface AgentConfiguration {
  model: string;
  temperature: number;
  maxTokens: number;
  timeout: number;
}

export interface AgentMetrics {
  totalExecutions: number;
  successRate: number;
  averageExecutionTime: number;
  lastExecutionAt?: Date;
}

export class Agent extends BaseModel {
  name: string;
  type: 'processing' | 'analysis' | 'generation' | 'integration';
  projectId: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  configuration: AgentConfiguration;
  metrics: AgentMetrics;
  lastResult?: any;

  constructor(data: Partial<Agent>) {
    super(data.id);
    this.name = data.name!;
    this.type = data.type!;
    this.projectId = data.projectId!;
    this.status = data.status || 'idle';
    this.configuration = data.configuration || {
      model: 'claude-3-sonnet',
      temperature: 0.7,
      maxTokens: 2000,
      timeout: 30000
    };
    this.metrics = data.metrics || {
      totalExecutions: 0,
      successRate: 0,
      averageExecutionTime: 0
    };
    this.lastResult = data.lastResult;
  }

  protected getEntityPrefix(): string {
    return 'agent';
  }

  protected serialize(): any {
    return {
      name: this.name,
      type: this.type,
      projectId: this.projectId,
      status: this.status,
      configuration: this.configuration,
      metrics: this.metrics,
      lastResult: this.lastResult
    };
  }

  updateStatus(status: Agent['status']): void {
    this.status = status;
    this.updateVersion();
  }

  recordExecution(success: boolean, executionTime: number, result?: any): void {
    this.metrics.totalExecutions++;
    this.metrics.successRate = (this.metrics.successRate * (this.metrics.totalExecutions - 1) + (success ? 1 : 0)) / this.metrics.totalExecutions;
    this.metrics.averageExecutionTime = (this.metrics.averageExecutionTime * (this.metrics.totalExecutions - 1) + executionTime) / this.metrics.totalExecutions;
    this.metrics.lastExecutionAt = new Date();
    this.lastResult = result;
    this.updateVersion();
  }
}