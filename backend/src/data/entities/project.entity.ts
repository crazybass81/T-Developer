import { BaseEntity } from './base.entity';

export interface ProjectSettings {
  framework: string;
  language: string;
  database: string;
  deployment: string;
}

export class ProjectEntity extends BaseEntity {
  ProjectId: string;
  ProjectName: string = '';
  Description: string = '';
  OwnerId: string;
  Status: 'active' | 'archived' | 'deleted';
  Settings: ProjectSettings;
  Metadata: Record<string, any>;
  
  constructor(projectId: string, ownerId: string) {
    super();
    this.EntityType = 'PROJECT';
    this.EntityId = projectId;
    this.ProjectId = projectId;
    this.OwnerId = ownerId;
    this.Status = 'active';
    this.PK = `PROJECT#${projectId}`;
    this.SK = 'METADATA';
    this.Settings = {
      framework: 'react',
      language: 'typescript',
      database: 'dynamodb',
      deployment: 'aws'
    };
    this.Metadata = {};
  }
  
  toDynamoDBItem(): Record<string, any> {
    return {
      PK: this.PK,
      SK: this.SK,
      EntityType: this.EntityType,
      EntityId: this.EntityId,
      ProjectId: this.ProjectId,
      ProjectName: this.ProjectName,
      Description: this.Description,
      OwnerId: this.OwnerId,
      Status: this.Status,
      Settings: this.Settings,
      Metadata: this.Metadata,
      CreatedAt: this.CreatedAt,
      UpdatedAt: this.UpdatedAt,
      Version: this.Version,
      GSI1PK: `USER#${this.OwnerId}`,
      GSI1SK: `PROJECT#${this.CreatedAt}#${this.ProjectId}`
    };
  }
  
  fromDynamoDBItem(item: Record<string, any>): void {
    Object.assign(this, item);
  }
}