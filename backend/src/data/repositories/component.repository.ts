import { BaseRepository, QueryOptions, QueryResult } from './base.repository';
import { Component } from '../models/component.model';

export class ComponentRepository extends BaseRepository<Component> {
  constructor(docClient: any) {
    super(docClient, 'COMPONENT');
  }

  toDynamoItem(component: Component): Record<string, any> {
    return {
      PK: `COMPONENT#${component.id}`,
      SK: 'METADATA',
      EntityType: 'COMPONENT',
      EntityId: component.id,
      ...component.toJSON(),
      GSI1PK: `CATEGORY#${component.category}`,
      GSI1SK: `DOWNLOADS#${component.downloadCount.toString().padStart(10, '0')}`,
      GSI2PK: `LANGUAGE#${component.language}`,
      GSI2SK: component.createdAt
    };
  }

  fromDynamoItem(item: Record<string, any>): Component {
    return Component.fromJSON(item);
  }

  generateKeys(component: Component): { PK: string; SK: string } {
    return {
      PK: `COMPONENT#${component.id}`,
      SK: 'METADATA'
    };
  }

  protected generateKeysById(id: string): { PK: string; SK: string } {
    return {
      PK: `COMPONENT#${id}`,
      SK: 'METADATA'
    };
  }

  async findByCategory(category: string, options: QueryOptions = {}): Promise<QueryResult<Component>> {
    return await this.query(
      'GSI1PK = :category',
      {
        ...options,
        expressionAttributeValues: { ':category': `CATEGORY#${category}` },
        scanIndexForward: false // Most downloaded first
      },
      'GSI1'
    );
  }

  async findByLanguage(language: string, options: QueryOptions = {}): Promise<QueryResult<Component>> {
    return await this.query(
      'GSI2PK = :language',
      {
        ...options,
        expressionAttributeValues: { ':language': `LANGUAGE#${language}` },
        scanIndexForward: false // Latest first
      },
      'GSI2'
    );
  }

  async searchByTags(tags: string[], options: QueryOptions = {}): Promise<Component[]> {
    // Simple implementation - in production would use more sophisticated search
    const allComponents: Component[] = [];
    
    for (const tag of tags) {
      const result = await this.query(
        'GSI1PK = :tag',
        {
          ...options,
          expressionAttributeValues: { ':tag': `TAG#${tag}` }
        },
        'GSI1'
      );
      allComponents.push(...result.items);
    }

    // Remove duplicates and return
    const uniqueComponents = allComponents.filter((component, index, self) =>
      index === self.findIndex(c => c.id === component.id)
    );

    return uniqueComponents;
  }

  async incrementDownloadCount(componentId: string): Promise<void> {
    const keys = this.generateKeysById(componentId);
    
    await this.docClient.send({
      TableName: this.tableName,
      Key: keys,
      UpdateExpression: 'ADD downloadCount :inc SET UpdatedAt = :updatedAt',
      ExpressionAttributeValues: {
        ':inc': 1,
        ':updatedAt': new Date().toISOString()
      }
    });
  }

  async findPopular(limit: number = 20): Promise<Component[]> {
    const result = await this.query(
      'GSI1PK = :popular',
      {
        expressionAttributeValues: { ':popular': 'POPULAR#true' },
        limit,
        scanIndexForward: false
      },
      'GSI1'
    );

    return result.items;
  }

  async findRecent(limit: number = 20): Promise<Component[]> {
    const result = await this.query(
      'GSI2PK = :recent',
      {
        expressionAttributeValues: { ':recent': 'RECENT#true' },
        limit,
        scanIndexForward: false
      },
      'GSI2'
    );

    return result.items;
  }
}