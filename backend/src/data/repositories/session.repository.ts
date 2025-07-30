import { BaseRepository, QueryOptions, QueryResult } from './base.repository';
import { Session } from '../models/session.model';

export class SessionRepository extends BaseRepository<Session> {
  constructor(docClient: any) {
    super(docClient, 'SESSION');
  }

  toDynamoItem(session: Session): Record<string, any> {
    return {
      PK: `SESSION#${session.id}`,
      SK: 'METADATA',
      EntityType: 'SESSION',
      EntityId: session.id,
      ...session.toJSON(),
      GSI1PK: `USER#${session.userId}`,
      GSI1SK: `SESSION#${session.createdAt}#${session.id}`,
      GSI2PK: `STATUS#${session.status}`,
      GSI2SK: session.lastActivityAt,
      TTL: Math.floor((new Date(session.expiresAt).getTime()) / 1000) // DynamoDB TTL
    };
  }

  fromDynamoItem(item: Record<string, any>): Session {
    return Session.fromJSON(item);
  }

  generateKeys(session: Session): { PK: string; SK: string } {
    return {
      PK: `SESSION#${session.id}`,
      SK: 'METADATA'
    };
  }

  protected generateKeysById(id: string): { PK: string; SK: string } {
    return {
      PK: `SESSION#${id}`,
      SK: 'METADATA'
    };
  }

  async findByUser(userId: string, options: QueryOptions = {}): Promise<QueryResult<Session>> {
    return await this.query(
      'GSI1PK = :userId AND begins_with(GSI1SK, :prefix)',
      {
        ...options,
        expressionAttributeValues: {
          ':userId': `USER#${userId}`,
          ':prefix': 'SESSION#'
        },
        scanIndexForward: false // Latest first
      },
      'GSI1'
    );
  }

  async findActiveByUser(userId: string): Promise<Session[]> {
    const result = await this.findByUser(userId, {
      filterExpression: '#status = :status',
      expressionAttributeValues: { ':status': 'active' }
    });

    return result.items;
  }

  async findByStatus(status: string, options: QueryOptions = {}): Promise<QueryResult<Session>> {
    return await this.query(
      'GSI2PK = :status',
      {
        ...options,
        expressionAttributeValues: { ':status': `STATUS#${status}` },
        scanIndexForward: false // Most recent activity first
      },
      'GSI2'
    );
  }

  async updateLastActivity(sessionId: string): Promise<void> {
    const keys = this.generateKeysById(sessionId);
    const now = new Date().toISOString();
    
    await this.docClient.send({
      TableName: this.tableName,
      Key: keys,
      UpdateExpression: 'SET lastActivityAt = :timestamp, UpdatedAt = :updatedAt, GSI2SK = :gsi2sk',
      ExpressionAttributeValues: {
        ':timestamp': now,
        ':updatedAt': now,
        ':gsi2sk': now
      }
    });
  }

  async expireSession(sessionId: string): Promise<void> {
    const keys = this.generateKeysById(sessionId);
    
    await this.docClient.send({
      TableName: this.tableName,
      Key: keys,
      UpdateExpression: 'SET #status = :status, UpdatedAt = :updatedAt, GSI2PK = :gsi2pk',
      ExpressionAttributeNames: { '#status': 'status' },
      ExpressionAttributeValues: {
        ':status': 'expired',
        ':updatedAt': new Date().toISOString(),
        ':gsi2pk': 'STATUS#expired'
      }
    });
  }

  async cleanupExpiredSessions(): Promise<number> {
    const expiredSessions = await this.findByStatus('expired', { limit: 100 });
    
    const deletePromises = expiredSessions.items.map(session => 
      this.delete(session.id)
    );
    
    await Promise.all(deletePromises);
    
    return expiredSessions.items.length;
  }

  async findActiveSessions(limit: number = 100): Promise<Session[]> {
    const result = await this.findByStatus('active', { limit });
    return result.items;
  }
}