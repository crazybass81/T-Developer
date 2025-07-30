import { BaseRepository, QueryOptions, QueryResult } from './base.repository';
import { Agent } from '../models/agent.model';

export class AgentRepository extends BaseRepository<Agent> {
  constructor(docClient: any) {
    super(docClient, 'AGENT');
  }

  toDynamoItem(agent: Agent): Record<string, any> {
    return {
      PK: `PROJECT#${agent.projectId}`,
      SK: `AGENT#${agent.id}`,
      EntityType: 'AGENT',
      EntityId: agent.id,
      ...agent.toJSON(),
      GSI1PK: `AGENT#${agent.id}`,
      GSI1SK: `STATUS#${agent.status}`,
      GSI2PK: `TYPE#${agent.type}`,
      GSI2SK: agent.createdAt
    };
  }

  fromDynamoItem(item: Record<string, any>): Agent {
    return Agent.fromJSON(item);
  }

  generateKeys(agent: Agent): { PK: string; SK: string } {
    return {
      PK: `PROJECT#${agent.projectId}`,
      SK: `AGENT#${agent.id}`
    };
  }

  protected generateKeysById(id: string): { PK: string; SK: string } {
    // Note: This requires projectId, which we don't have from just ID
    // In practice, you'd need to query GSI1 first or pass projectId
    throw new Error('Use findByAgentId instead - requires GSI lookup');
  }

  async findByAgentId(agentId: string): Promise<Agent | null> {
    const result = await this.query(
      'GSI1PK = :agentId',
      {
        expressionAttributeValues: { ':agentId': `AGENT#${agentId}` },
        limit: 1
      },
      'GSI1'
    );

    return result.items[0] || null;
  }

  async findByProject(projectId: string, options: QueryOptions = {}): Promise<QueryResult<Agent>> {
    return await this.query(
      'PK = :projectId AND begins_with(SK, :prefix)',
      {
        ...options,
        expressionAttributeValues: {
          ':projectId': `PROJECT#${projectId}`,
          ':prefix': 'AGENT#'
        }
      }
    );
  }

  async findByType(type: string, options: QueryOptions = {}): Promise<QueryResult<Agent>> {
    return await this.query(
      'GSI2PK = :type',
      {
        ...options,
        expressionAttributeValues: { ':type': `TYPE#${type}` },
        scanIndexForward: false
      },
      'GSI2'
    );
  }

  async findByStatus(status: string, options: QueryOptions = {}): Promise<QueryResult<Agent>> {
    return await this.query(
      'GSI1SK = :status',
      {
        ...options,
        expressionAttributeValues: { ':status': `STATUS#${status}` }
      },
      'GSI1'
    );
  }

  async updateStatus(agentId: string, status: string): Promise<void> {
    // First find the agent to get projectId
    const agent = await this.findByAgentId(agentId);
    if (!agent) throw new Error('Agent not found');

    const keys = this.generateKeys(agent);
    
    await this.docClient.send({
      TableName: this.tableName,
      Key: keys,
      UpdateExpression: 'SET #status = :status, UpdatedAt = :updatedAt, GSI1SK = :gsi1sk',
      ExpressionAttributeNames: { '#status': 'status' },
      ExpressionAttributeValues: {
        ':status': status,
        ':updatedAt': new Date().toISOString(),
        ':gsi1sk': `STATUS#${status}`
      }
    });
  }

  async findActiveAgents(limit: number = 50): Promise<Agent[]> {
    const result = await this.query(
      'GSI1SK = :status',
      {
        expressionAttributeValues: { ':status': 'STATUS#running' },
        limit
      },
      'GSI1'
    );

    return result.items;
  }
}