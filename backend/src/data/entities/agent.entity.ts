import { BaseEntity } from './base.entity';

export interface AgentConfiguration {
  model: string;
  temperature: number;
  maxTokens: number;
  timeout: number;
}

export interface AgentMetrics {
  executionCount: number;
  averageExecutionTime: number;
  successRate: number;
  lastExecutionTime?: number;
}

export class AgentEntity extends BaseEntity {
  AgentId: string;
  AgentType: string;
  ProjectId: string;
  Name: string = '';
  Status: 'idle' | 'running' | 'completed' | 'failed';
  Configuration: AgentConfiguration;
  LastExecutionAt?: string;
  Metrics: AgentMetrics;
  
  constructor(agentId: string, projectId: string, agentType: string) {
    super();
    this.EntityType = 'AGENT';
    this.EntityId = agentId;
    this.AgentId = agentId;
    this.ProjectId = projectId;
    this.AgentType = agentType;
    this.Status = 'idle';
    this.PK = `PROJECT#${projectId}`;
    this.SK = `AGENT#${agentId}`;
    this.Configuration = {
      model: 'claude-3-sonnet',
      temperature: 0.7,
      maxTokens: 4096,
      timeout: 300000
    };
    this.Metrics = {
      executionCount: 0,
      averageExecutionTime: 0,
      successRate: 1.0
    };
  }
  
  toDynamoDBItem(): Record<string, any> {
    return {
      PK: this.PK,
      SK: this.SK,
      EntityType: this.EntityType,
      EntityId: this.EntityId,
      AgentId: this.AgentId,
      AgentType: this.AgentType,
      ProjectId: this.ProjectId,
      Name: this.Name,
      Status: this.Status,
      Configuration: this.Configuration,
      LastExecutionAt: this.LastExecutionAt,
      Metrics: this.Metrics,
      CreatedAt: this.CreatedAt,
      UpdatedAt: this.UpdatedAt,
      Version: this.Version,
      GSI2PK: `AGENT#${this.AgentId}`,
      GSI2SK: `STATUS#${this.Status}`
    };
  }
  
  fromDynamoDBItem(item: Record<string, any>): void {
    Object.assign(this, item);
  }
}