import { BaseRepository, QueryOptions, QueryResult } from './base.repository';
import { Project } from '../models/project.model';

export class ProjectRepository extends BaseRepository<Project> {
  constructor(docClient: any) {
    super(docClient, 'PROJECT');
  }

  toDynamoItem(project: Project): Record<string, any> {
    return {
      PK: `PROJECT#${project.id}`,
      SK: 'METADATA',
      EntityType: 'PROJECT',
      EntityId: project.id,
      ...project.toJSON(),
      GSI1PK: `USER#${project.ownerId}`,
      GSI1SK: `PROJECT#${project.createdAt}#${project.id}`,
      GSI2PK: `STATUS#${project.status}`,
      GSI2SK: project.createdAt
    };
  }

  fromDynamoItem(item: Record<string, any>): Project {
    return Project.fromJSON(item);
  }

  generateKeys(project: Project): { PK: string; SK: string } {
    return {
      PK: `PROJECT#${project.id}`,
      SK: 'METADATA'
    };
  }

  protected generateKeysById(id: string): { PK: string; SK: string } {
    return {
      PK: `PROJECT#${id}`,
      SK: 'METADATA'
    };
  }

  async findByOwner(ownerId: string, options: QueryOptions = {}): Promise<QueryResult<Project>> {
    return await this.query(
      'GSI1PK = :ownerId AND begins_with(GSI1SK, :prefix)',
      {
        ...options,
        expressionAttributeValues: {
          ':ownerId': `USER#${ownerId}`,
          ':prefix': 'PROJECT#'
        },
        scanIndexForward: false // Latest first
      },
      'GSI1'
    );
  }

  async findByStatus(status: string, options: QueryOptions = {}): Promise<QueryResult<Project>> {
    return await this.query(
      'GSI2PK = :status',
      {
        ...options,
        expressionAttributeValues: { ':status': `STATUS#${status}` },
        scanIndexForward: false
      },
      'GSI2'
    );
  }

  async updateStatus(projectId: string, status: string): Promise<void> {
    const keys = this.generateKeysById(projectId);
    
    await this.docClient.send({
      TableName: this.tableName,
      Key: keys,
      UpdateExpression: 'SET #status = :status, UpdatedAt = :updatedAt, GSI2PK = :gsi2pk',
      ExpressionAttributeNames: { '#status': 'status' },
      ExpressionAttributeValues: {
        ':status': status,
        ':updatedAt': new Date().toISOString(),
        ':gsi2pk': `STATUS#${status}`
      }
    });
  }

  async findRecentProjects(limit: number = 10): Promise<Project[]> {
    const result = await this.query(
      'GSI2PK = :active',
      {
        expressionAttributeValues: { ':active': 'STATUS#active' },
        limit,
        scanIndexForward: false
      },
      'GSI2'
    );

    return result.items;
  }
}