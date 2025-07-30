// T-Developer DynamoDB Single Table Schema
export const TABLE_SCHEMA = {
  tableName: 'T-Developer-Main',
  partitionKey: 'PK',
  sortKey: 'SK',
  gsi1: { pk: 'GSI1PK', sk: 'GSI1SK' },
  gsi2: { pk: 'GSI2PK', sk: 'GSI2SK' }
};

export const ACCESS_PATTERNS = {
  getUserById: (userId: string) => ({ PK: `USER#${userId}`, SK: 'METADATA' }),
  getProjectsByUser: (userId: string) => ({ GSI1PK: `USER#${userId}`, GSI1SK: 'PROJECT#' }),
  getAgentsByProject: (projectId: string) => ({ GSI2PK: `PROJECT#${projectId}`, GSI2SK: 'AGENT#' })
};