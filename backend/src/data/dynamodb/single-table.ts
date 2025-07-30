import { DynamoDBDocumentClient, PutCommand, GetCommand, QueryCommand, UpdateCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb';

export interface KeySchema {
  PK: string;
  SK: string;
}

export interface GSIKeySchema {
  GSI1PK?: string;
  GSI1SK?: string;
  GSI2PK?: string;
  GSI2SK?: string;
}

export class SingleTableDesign {
  private readonly TABLE_NAME = 'T-Developer-Main';
  
  constructor(private docClient: DynamoDBDocumentClient) {}
  
  // Generate primary keys
  generateKeys(entityType: string, entityId: string): KeySchema {
    return {
      PK: `${entityType}#${entityId}`,
      SK: `METADATA#${entityId}`
    };
  }
  
  // Generate GSI keys
  generateGSIKeys(entity: any): GSIKeySchema {
    const gsi: GSIKeySchema = {};
    
    if (entity.userId) {
      gsi.GSI1PK = `USER#${entity.userId}`;
      gsi.GSI1SK = `${entity.entityType}#${entity.createdAt || new Date().toISOString()}`;
    }
    
    if (entity.projectId) {
      gsi.GSI2PK = `PROJECT#${entity.projectId}`;
      gsi.GSI2SK = `${entity.entityType}#${entity.updatedAt || new Date().toISOString()}`;
    }
    
    return gsi;
  }
  
  // Put item
  async putItem(item: any): Promise<void> {
    await this.docClient.send(new PutCommand({
      TableName: this.TABLE_NAME,
      Item: {
        ...item,
        createdAt: item.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    }));
  }
  
  // Get item
  async getItem(keys: KeySchema): Promise<any> {
    const result = await this.docClient.send(new GetCommand({
      TableName: this.TABLE_NAME,
      Key: keys
    }));
    
    return result.Item;
  }
  
  // Query items
  async queryItems(keyCondition: string, values: Record<string, any>, indexName?: string): Promise<any[]> {
    const result = await this.docClient.send(new QueryCommand({
      TableName: this.TABLE_NAME,
      IndexName: indexName,
      KeyConditionExpression: keyCondition,
      ExpressionAttributeValues: values
    }));
    
    return result.Items || [];
  }
  
  // Update item
  async updateItem(keys: KeySchema, updates: Record<string, any>): Promise<void> {
    const updateExpression = 'SET ' + Object.keys(updates).map(key => `#${key} = :${key}`).join(', ') + ', updatedAt = :updatedAt';
    const attributeNames = Object.keys(updates).reduce((acc, key) => ({ ...acc, [`#${key}`]: key }), {});
    const attributeValues = Object.keys(updates).reduce((acc, key) => ({ ...acc, [`:${key}`]: updates[key] }), { ':updatedAt': new Date().toISOString() });
    
    await this.docClient.send(new UpdateCommand({
      TableName: this.TABLE_NAME,
      Key: keys,
      UpdateExpression: updateExpression,
      ExpressionAttributeNames: attributeNames,
      ExpressionAttributeValues: attributeValues
    }));
  }
  
  // Delete item
  async deleteItem(keys: KeySchema): Promise<void> {
    await this.docClient.send(new DeleteCommand({
      TableName: this.TABLE_NAME,
      Key: keys
    }));
  }
  
  // Get items by user
  async getItemsByUser(userId: string, entityType?: string): Promise<any[]> {
    let keyCondition = 'GSI1PK = :pk';
    const values: any = { ':pk': `USER#${userId}` };
    
    if (entityType) {
      keyCondition += ' AND begins_with(GSI1SK, :sk)';
      values[':sk'] = `${entityType}#`;
    }
    
    return this.queryItems(keyCondition, values, 'GSI1');
  }
  
  // Get items by project
  async getItemsByProject(projectId: string, entityType?: string): Promise<any[]> {
    let keyCondition = 'GSI2PK = :pk';
    const values: any = { ':pk': `PROJECT#${projectId}` };
    
    if (entityType) {
      keyCondition += ' AND begins_with(GSI2SK, :sk)';
      values[':sk'] = `${entityType}#`;
    }
    
    return this.queryItems(keyCondition, values, 'GSI2');
  }
}