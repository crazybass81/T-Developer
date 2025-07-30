// T-Developer Single Table Design for DynamoDB
export interface TableDesign {
  tableName: string;
  partitionKey: AttributeDefinition;
  sortKey?: AttributeDefinition;
  globalSecondaryIndexes: GSI[];
  attributes: AttributeDefinition[];
}

export interface AttributeDefinition {
  name: string;
  type: 'S' | 'N' | 'B';
  required?: boolean;
  description?: string;
}

export interface GSI {
  indexName: string;
  partitionKey: AttributeDefinition;
  sortKey?: AttributeDefinition;
  projection: 'ALL' | 'KEYS_ONLY';
  purpose: string;
}

export const T_DEVELOPER_TABLE: TableDesign = {
  tableName: 'T-Developer-Main',
  partitionKey: {
    name: 'PK',
    type: 'S',
    description: 'Partition Key - Format: {EntityType}#{EntityId}'
  },
  sortKey: {
    name: 'SK',
    type: 'S', 
    description: 'Sort Key - Format: {RelationType}#{Timestamp}#{Id}'
  },
  globalSecondaryIndexes: [
    {
      indexName: 'GSI1',
      partitionKey: { name: 'GSI1PK', type: 'S' },
      sortKey: { name: 'GSI1SK', type: 'S' },
      projection: 'ALL',
      purpose: 'Query by User/Project relationships'
    },
    {
      indexName: 'GSI2',
      partitionKey: { name: 'GSI2PK', type: 'S' },
      sortKey: { name: 'GSI2SK', type: 'S' },
      projection: 'ALL',
      purpose: 'Query by Agent/Task relationships'
    }
  ],
  attributes: [
    { name: 'EntityType', type: 'S', required: true },
    { name: 'EntityId', type: 'S', required: true },
    { name: 'Status', type: 'S', required: true },
    { name: 'CreatedAt', type: 'S', required: true },
    { name: 'UpdatedAt', type: 'S', required: true }
  ]
};

// Access Patterns
export const ACCESS_PATTERNS = {
  getUserById: {
    index: 'Primary',
    PK: 'USER#{userId}',
    SK: 'METADATA'
  },
  getProjectsByUser: {
    index: 'GSI1',
    GSI1PK: 'USER#{userId}',
    GSI1SK: 'PROJECT#'
  },
  getAgentsByProject: {
    index: 'GSI2',
    GSI2PK: 'PROJECT#{projectId}',
    GSI2SK: 'AGENT#'
  }
};