/**
 * Project Repository Implementation
 * Provides project-specific data access methods and business logic
 */

import { BaseRepository, QueryResult, AdvancedQueryOptions } from './base.repository';
import { BaseModel } from '../models/base.model';
import { ProjectEntity } from '../entities/project.entity';
import { ProjectData, EntityStatus } from '../schemas/table-schema';
import { SingleTableClient } from '../dynamodb/single-table';
import { ValidationError } from '../validation/validator';
import { BaseEntity } from '../entities/base.entity';

class ProjectModel extends BaseModel<ProjectEntity, ProjectData> {
  protected createEntity(data: ProjectData): ProjectEntity {
    return new ProjectEntity(data);
  }

  protected getEntityType(): string {
    return 'PROJECT';
  }

  protected getDefaultSortKey(): string {
    return 'METADATA';
  }

  protected getEntityClass(): new () => ProjectEntity {
    return ProjectEntity;
  }
}

export class ProjectRepository extends BaseRepository<ProjectEntity, ProjectData> {
  constructor(client?: SingleTableClient) {
    const projectModel = new ProjectModel(client);
    super(projectModel, {
      enableCaching: true,
      cacheExpiration: 300,
      enableMetrics: true,
      enableAuditLog: true
    });
  }

  protected getRepositoryName(): string {
    return 'Project';
  }

  public async findByOwner(ownerId: string): Promise<QueryResult<ProjectEntity>> {
    const result = await this.client.query({
      indexName: 'GSI1',
      gsi1pk: `USER#${ownerId}`,
      gsi1sk: 'PROJECT#'
    });

    const entities = result.items.map(item => 
      BaseEntity.fromDynamoDBItem(item, ProjectEntity)
    );

    return {
      items: entities,
      lastEvaluatedKey: result.lastEvaluatedKey,
      count: entities.length
    };
  }

  public async findByOrganization(organizationId: string): Promise<QueryResult<ProjectEntity>> {
    const result = await this.client.query({
      indexName: 'GSI2',
      gsi2pk: `ORG#${organizationId}`,
      gsi2sk: 'PROJECT#'
    });

    const entities = result.items.map(item => 
      BaseEntity.fromDynamoDBItem(item, ProjectEntity)
    );

    return {
      items: entities,
      lastEvaluatedKey: result.lastEvaluatedKey,
      count: entities.length
    };
  }
}