import { DynamoQueryBuilder, QueryExecutor } from './query-builder';
import { QueryOptimizer } from '../optimization/query-optimizer';

export interface ProjectEntity {
  ProjectId: string;
  ProjectName: string;
  OwnerId: string;
  Status: string;
  CreatedAt: string;
}

export class ProjectQueryService {
  constructor(
    private queryExecutor: QueryExecutor,
    private optimizer: QueryOptimizer,
    private tableName: string
  ) {}
  
  async getProjectsByUser(userId: string, status?: string): Promise<ProjectEntity[]> {
    const query = new DynamoQueryBuilder(this.tableName)
      .useIndex('GSI1')
      .wherePartitionKey('GSI1PK', `USER#${userId}`)
      .andSortKey('GSI1SK', 'begins_with', 'PROJECT#')
      .scanForward(false);
    
    if (status) {
      query.filter('#status = :status', { ':status': status });
    }
    
    const optimizedParams = await this.optimizer.optimizeQuery(query.build());
    return this.queryExecutor.queryAll<ProjectEntity>(optimizedParams);
  }
  
  async getProjectAgents(projectId: string): Promise<any[]> {
    const query = new DynamoQueryBuilder(this.tableName)
      .wherePartitionKey('PK', `PROJECT#${projectId}`)
      .andSortKey('SK', 'begins_with', 'AGENT#')
      .select(['AgentId', 'AgentType', 'Status', 'CreatedAt']);
    
    return this.queryExecutor.queryAll(query.build());
  }
  
  async getRecentProjects(limit: number = 10): Promise<ProjectEntity[]> {
    const query = new DynamoQueryBuilder(this.tableName)
      .useIndex('GSI3')
      .wherePartitionKey('GSI3PK', 'PROJECTS#active')
      .scanForward(false)
      .limit(limit);
    
    const result = await this.queryExecutor.query<ProjectEntity>(query.build());
    return result.items;
  }
}