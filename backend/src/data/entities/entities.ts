// T-Developer Entity Models
export class BaseEntity {
  PK: string = '';
  SK: string = '';
  EntityType: string = '';
  CreatedAt: string = new Date().toISOString();
  UpdatedAt: string = new Date().toISOString();
  GSI1PK?: string;
  GSI1SK?: string;
  GSI2PK?: string;
  GSI2SK?: string;
}

export class UserEntity extends BaseEntity {
  UserId: string;
  Email: string = '';
  Username: string = '';
  Role: 'admin' | 'developer' | 'viewer' = 'developer';
  
  constructor(userId: string) {
    super();
    this.UserId = userId;
    this.EntityType = 'USER';
    this.PK = `USER#${userId}`;
    this.SK = 'METADATA';
  }
}

export class ProjectEntity extends BaseEntity {
  ProjectId: string;
  ProjectName: string = '';
  OwnerId: string;
  Status: 'active' | 'archived' = 'active';
  
  constructor(projectId: string, ownerId: string) {
    super();
    this.ProjectId = projectId;
    this.OwnerId = ownerId;
    this.EntityType = 'PROJECT';
    this.PK = `PROJECT#${projectId}`;
    this.SK = 'METADATA';
  }
}

export class AgentEntity extends BaseEntity {
  AgentId: string;
  ProjectId: string;
  AgentType: string;
  Status: 'idle' | 'running' | 'completed' = 'idle';
  
  constructor(agentId: string, projectId: string, agentType: string) {
    super();
    this.AgentId = agentId;
    this.ProjectId = projectId;
    this.AgentType = agentType;
    this.EntityType = 'AGENT';
    this.PK = `PROJECT#${projectId}`;
    this.SK = `AGENT#${agentId}`;
  }
}