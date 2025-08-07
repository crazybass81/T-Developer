/**
 * T-Developer Single Table Design for DynamoDB
 * 단일 테이블 설계 패턴 구현
 */

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
  projection: 'ALL' | 'KEYS_ONLY' | 'INCLUDE';
  includedAttributes?: string[];
  purpose: string;
  throughput?: {
    readCapacityUnits: number;
    writeCapacityUnits: number;
  };
}

export interface LSI {
  indexName: string;
  sortKey: AttributeDefinition;
  projection: 'ALL' | 'KEYS_ONLY' | 'INCLUDE';
  includedAttributes?: string[];
  purpose: string;
}

export interface TableDesign {
  tableName: string;
  partitionKey: AttributeDefinition;
  sortKey?: AttributeDefinition;
  globalSecondaryIndexes: GSI[];
  localSecondaryIndexes?: LSI[];
  attributes: AttributeDefinition[];
  streamSpecification?: {
    streamEnabled: boolean;
    streamViewType: 'NEW_IMAGE' | 'OLD_IMAGE' | 'NEW_AND_OLD_IMAGES' | 'KEYS_ONLY';
  };
  ttl?: {
    attributeName: string;
    enabled: boolean;
  };
  tags?: Record<string, string>;
}

/**
 * T-Developer 메인 테이블 설계
 * 단일 테이블 패턴으로 모든 엔티티를 하나의 테이블에 저장
 */
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
      purpose: 'Query by User/Project relationships',
      throughput: {
        readCapacityUnits: 5,
        writeCapacityUnits: 5
      }
    },
    {
      indexName: 'GSI2',
      partitionKey: { name: 'GSI2PK', type: 'S' },
      sortKey: { name: 'GSI2SK', type: 'S' },
      projection: 'ALL',
      purpose: 'Query by Agent/Task relationships',
      throughput: {
        readCapacityUnits: 5,
        writeCapacityUnits: 5
      }
    },
    {
      indexName: 'GSI3',
      partitionKey: { name: 'GSI3PK', type: 'S' },
      sortKey: { name: 'CreatedAt', type: 'S' },
      projection: 'ALL',
      purpose: 'Time-based queries',
      throughput: {
        readCapacityUnits: 5,
        writeCapacityUnits: 5
      }
    },
    {
      indexName: 'GSI4',
      partitionKey: { name: 'Status', type: 'S' },
      sortKey: { name: 'UpdatedAt', type: 'S' },
      projection: 'ALL',
      purpose: 'Status-based queries',
      throughput: {
        readCapacityUnits: 5,
        writeCapacityUnits: 5
      }
    },
    {
      indexName: 'GSI5',
      partitionKey: { name: 'EntityType', type: 'S' },
      sortKey: { name: 'EntityId', type: 'S' },
      projection: 'ALL',
      purpose: 'Entity type queries',
      throughput: {
        readCapacityUnits: 5,
        writeCapacityUnits: 5
      }
    }
  ],
  
  localSecondaryIndexes: [
    {
      indexName: 'LSI1',
      sortKey: { name: 'Version', type: 'N' },
      projection: 'ALL',
      purpose: 'Version tracking'
    },
    {
      indexName: 'LSI2',
      sortKey: { name: 'Priority', type: 'N' },
      projection: 'ALL',
      purpose: 'Priority-based sorting'
    }
  ],
  
  attributes: [
    { name: 'EntityType', type: 'S', required: true },
    { name: 'EntityId', type: 'S', required: true },
    { name: 'Status', type: 'S', required: true },
    { name: 'CreatedAt', type: 'S', required: true },
    { name: 'UpdatedAt', type: 'S', required: true },
    { name: 'CreatedBy', type: 'S', required: false },
    { name: 'UpdatedBy', type: 'S', required: false },
    { name: 'Version', type: 'N', required: false },
    { name: 'Priority', type: 'N', required: false },
    { name: 'TTL', type: 'N', required: false },
    { name: 'Data', type: 'S', required: true, description: 'JSON serialized entity data' },
    { name: 'Metadata', type: 'S', required: false, description: 'JSON serialized metadata' }
  ],
  
  streamSpecification: {
    streamEnabled: true,
    streamViewType: 'NEW_AND_OLD_IMAGES'
  },
  
  ttl: {
    attributeName: 'TTL',
    enabled: true
  },
  
  tags: {
    Environment: 'production',
    Project: 'T-Developer',
    ManagedBy: 'terraform'
  }
};

/**
 * Entity Access Patterns
 * 각 엔티티 타입별 접근 패턴 정의
 */
export const ACCESS_PATTERNS = {
  // User patterns
  getUserById: {
    pk: 'USER#{userId}',
    sk: 'PROFILE'
  },
  getUserProjects: {
    pk: 'USER#{userId}',
    sk: 'PROJECT#'
  },
  getUserSessions: {
    pk: 'USER#{userId}',
    sk: 'SESSION#'
  },
  
  // Project patterns
  getProjectById: {
    pk: 'PROJECT#{projectId}',
    sk: 'METADATA'
  },
  getProjectMembers: {
    pk: 'PROJECT#{projectId}',
    sk: 'MEMBER#'
  },
  getProjectAgents: {
    pk: 'PROJECT#{projectId}',
    sk: 'AGENT#'
  },
  
  // Agent patterns
  getAgentById: {
    pk: 'AGENT#{agentId}',
    sk: 'CONFIG'
  },
  getAgentTasks: {
    pk: 'AGENT#{agentId}',
    sk: 'TASK#'
  },
  getAgentMetrics: {
    pk: 'AGENT#{agentId}',
    sk: 'METRIC#'
  },
  
  // Task patterns
  getTaskById: {
    pk: 'TASK#{taskId}',
    sk: 'DETAILS'
  },
  getTaskExecutions: {
    pk: 'TASK#{taskId}',
    sk: 'EXECUTION#'
  },
  getTaskResults: {
    pk: 'TASK#{taskId}',
    sk: 'RESULT#'
  },
  
  // Session patterns
  getSessionById: {
    pk: 'SESSION#{sessionId}',
    sk: 'DATA'
  },
  getSessionEvents: {
    pk: 'SESSION#{sessionId}',
    sk: 'EVENT#'
  },
  
  // GSI1 patterns - User/Project relationships
  getProjectsByUser: {
    gsi1pk: 'USER#{userId}',
    gsi1sk: 'PROJECT#'
  },
  getUsersByProject: {
    gsi1pk: 'PROJECT#{projectId}',
    gsi1sk: 'USER#'
  },
  
  // GSI2 patterns - Agent/Task relationships
  getTasksByAgent: {
    gsi2pk: 'AGENT#{agentId}',
    gsi2sk: 'TASK#'
  },
  getAgentsByTask: {
    gsi2pk: 'TASK#{taskId}',
    gsi2sk: 'AGENT#'
  },
  
  // GSI3 patterns - Time-based queries
  getRecentItems: {
    gsi3pk: 'ENTITY#{entityType}',
    sortByCreatedAt: true
  },
  
  // GSI4 patterns - Status queries
  getItemsByStatus: {
    status: 'ACTIVE|PENDING|COMPLETED|FAILED',
    sortByUpdatedAt: true
  },
  
  // GSI5 patterns - Entity type queries
  getAllByEntityType: {
    entityType: 'USER|PROJECT|AGENT|TASK|SESSION'
  }
};

/**
 * Composite Key Helpers
 */
export class CompositeKeyBuilder {
  static buildPK(entityType: string, entityId: string): string {
    return `${entityType}#${entityId}`;
  }
  
  static buildSK(relationType: string, ...parts: (string | number)[]): string {
    return [relationType, ...parts].join('#');
  }
  
  static parsePK(pk: string): { entityType: string; entityId: string } {
    const [entityType, entityId] = pk.split('#');
    return { entityType, entityId };
  }
  
  static parseSK(sk: string): string[] {
    return sk.split('#');
  }
  
  static buildGSI1Keys(entityType: string, entityId: string, relatedType: string, relatedId: string) {
    return {
      GSI1PK: `${entityType}#${entityId}`,
      GSI1SK: `${relatedType}#${relatedId}`
    };
  }
  
  static buildGSI2Keys(agentId: string, taskId: string) {
    return {
      GSI2PK: `AGENT#${agentId}`,
      GSI2SK: `TASK#${taskId}`
    };
  }
  
  static buildGSI3Keys(entityType: string, createdAt: Date | string) {
    const timestamp = typeof createdAt === 'string' ? createdAt : createdAt.toISOString();
    return {
      GSI3PK: `ENTITY#${entityType}`,
      CreatedAt: timestamp
    };
  }
}