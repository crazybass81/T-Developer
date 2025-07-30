import { BaseRepository, QueryOptions, QueryResult } from './base.repository';
import { User } from '../models/user.model';

export class UserRepository extends BaseRepository<User> {
  constructor(docClient: any) {
    super(docClient, 'USER');
  }

  toDynamoItem(user: User): Record<string, any> {
    return {
      PK: `USER#${user.id}`,
      SK: 'METADATA',
      EntityType: 'USER',
      EntityId: user.id,
      ...user.toJSON(),
      GSI1PK: `EMAIL#${user.email}`,
      GSI1SK: user.id
    };
  }

  fromDynamoItem(item: Record<string, any>): User {
    return User.fromJSON(item);
  }

  generateKeys(user: User): { PK: string; SK: string } {
    return {
      PK: `USER#${user.id}`,
      SK: 'METADATA'
    };
  }

  protected generateKeysById(id: string): { PK: string; SK: string } {
    return {
      PK: `USER#${id}`,
      SK: 'METADATA'
    };
  }

  async findByEmail(email: string): Promise<User | null> {
    const result = await this.query(
      'GSI1PK = :email',
      {
        expressionAttributeValues: { ':email': `EMAIL#${email}` },
        limit: 1
      },
      'GSI1'
    );

    return result.items[0] || null;
  }

  async findByRole(role: string, options: QueryOptions = {}): Promise<QueryResult<User>> {
    return await this.query(
      'GSI2PK = :role',
      {
        ...options,
        expressionAttributeValues: { ':role': `ROLE#${role}` }
      },
      'GSI2'
    );
  }

  async updateLastLogin(userId: string): Promise<void> {
    const keys = this.generateKeysById(userId);
    
    await this.docClient.send({
      TableName: this.tableName,
      Key: keys,
      UpdateExpression: 'SET LastLoginAt = :timestamp, UpdatedAt = :updatedAt',
      ExpressionAttributeValues: {
        ':timestamp': new Date().toISOString(),
        ':updatedAt': new Date().toISOString()
      }
    });
  }
}