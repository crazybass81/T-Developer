/**
 * Agent Repository Implementation
 * Provides agent-specific data access methods and business logic
 */

import { BaseRepository, QueryResult } from './base.repository';
import { BaseModel } from '../models/base.model';
import { AgentEntity } from '../entities/agent.entity';
import { AgentData, AgentType } from '../schemas/table-schema';
import { SingleTableClient } from '../dynamodb/single-table';
import { BaseEntity } from '../entities/base.entity';

class AgentModel extends BaseModel<AgentEntity, AgentData> {
  protected createEntity(data: AgentData): AgentEntity {
    return new AgentEntity(data);
  }

  protected getEntityType(): string {
    return 'AGENT';
  }

  protected getDefaultSortKey(): string {
    return 'CONFIG';
  }

  protected getEntityClass(): new () => AgentEntity {
    return AgentEntity;
  }
}

export class AgentRepository extends BaseRepository<AgentEntity, AgentData> {
  constructor(client?: SingleTableClient) {
    const agentModel = new AgentModel(client);
    super(agentModel, {
      enableCaching: true,
      cacheExpiration: 300,
      enableMetrics: true,
      enableAuditLog: true
    });
  }

  protected getRepositoryName(): string {
    return 'Agent';
  }

  public async findByProject(projectId: string): Promise<QueryResult<AgentEntity>> {
    const result = await this.client.query({
      indexName: 'GSI1',
      gsi1pk: `PROJECT#${projectId}`,
      gsi1sk: 'AGENT#'
    });

    const entities = result.items.map(item => 
      BaseEntity.fromDynamoDBItem(item, AgentEntity)
    );

    return {
      items: entities,
      lastEvaluatedKey: result.lastEvaluatedKey,
      count: entities.length
    };
  }

  public async findByType(agentType: AgentType): Promise<QueryResult<AgentEntity>> {
    const result = await this.client.query({
      indexName: 'GSI2',
      gsi2pk: `AGENT_TYPE#${agentType}`,
      gsi2sk: 'AGENT#'
    });

    const entities = result.items.map(item => 
      BaseEntity.fromDynamoDBItem(item, AgentEntity)
    );

    return {
      items: entities,
      lastEvaluatedKey: result.lastEvaluatedKey,
      count: entities.length
    };
  }
}