import { DynamoDBDocumentClient, GetCommand, PutCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';
import { BaseEntity } from '../entities/entities';
import { TABLE_SCHEMA } from '../schemas/table-schema';

export class Repository {
  constructor(private docClient: DynamoDBDocumentClient) {}
  
  async get(pk: string, sk: string): Promise<any> {
    const result = await this.docClient.send(new GetCommand({
      TableName: TABLE_SCHEMA.tableName,
      Key: { PK: pk, SK: sk }
    }));
    return result.Item || null;
  }
  
  async put(entity: BaseEntity): Promise<void> {
    await this.docClient.send(new PutCommand({
      TableName: TABLE_SCHEMA.tableName,
      Item: entity
    }));
  }
  
  async query(pk: string, skPrefix?: string): Promise<any[]> {
    const params: any = {
      TableName: TABLE_SCHEMA.tableName,
      KeyConditionExpression: 'PK = :pk',
      ExpressionAttributeValues: { ':pk': pk }
    };
    
    if (skPrefix) {
      params.KeyConditionExpression += ' AND begins_with(SK, :sk)';
      params.ExpressionAttributeValues[':sk'] = skPrefix;
    }
    
    const result = await this.docClient.send(new QueryCommand(params));
    return result.Items || [];
  }
  
  async queryGSI(indexName: string, pk: string, skPrefix?: string): Promise<any[]> {
    const params: any = {
      TableName: TABLE_SCHEMA.tableName,
      IndexName: indexName,
      KeyConditionExpression: `${indexName}PK = :pk`,
      ExpressionAttributeValues: { ':pk': pk }
    };
    
    if (skPrefix) {
      params.KeyConditionExpression += ` AND begins_with(${indexName}SK, :sk)`;
      params.ExpressionAttributeValues[':sk'] = skPrefix;
    }
    
    const result = await this.docClient.send(new QueryCommand(params));
    return result.Items || [];
  }
}