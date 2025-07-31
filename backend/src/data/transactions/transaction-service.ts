// backend/src/data/transactions/transaction-service.ts
import { TransactionManager, TransactionItem } from './transaction-manager';
import { SagaOrchestrator, SagaDefinition } from './saga-orchestrator';
import { OptimisticLockManager } from './optimistic-lock';
import { DistributedLockManager } from './distributed-lock';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';

export interface TransactionServiceConfig {
  tableName: string;
  lockTableName?: string;
  optimisticLock?: {
    maxRetries: number;
    baseDelayMs: number;
  };
}

export class TransactionService {
  private transactionManager: TransactionManager;
  private sagaOrchestrator: SagaOrchestrator;
  private optimisticLockManager: OptimisticLockManager;
  private distributedLockManager: DistributedLockManager;

  constructor(
    private docClient: DynamoDBDocumentClient,
    private config: TransactionServiceConfig
  ) {
    this.transactionManager = new TransactionManager(docClient);
    this.sagaOrchestrator = new SagaOrchestrator();
    this.optimisticLockManager = new OptimisticLockManager(
      docClient,
      config.optimisticLock
    );
    this.distributedLockManager = new DistributedLockManager(
      docClient,
      config.lockTableName
    );
  }

  // Simple transaction operations
  async executeTransaction(items: TransactionItem[]) {
    return this.transactionManager.executeTransaction(items);
  }

  async readTransaction(keys: Array<{ tableName: string; key: any }>) {
    return this.transactionManager.readTransaction(keys);
  }

  // Saga pattern for distributed transactions
  async executeSaga(definition: SagaDefinition, context: any = {}) {
    return this.sagaOrchestrator.executeSaga(definition, context);
  }

  async getSagaExecution(id: string) {
    return this.sagaOrchestrator.getSagaExecution(id);
  }

  // Optimistic locking
  async updateWithOptimisticLock<T>(
    key: any,
    updateFn: (current: T) => Partial<T>,
    options?: { versionField?: string }
  ) {
    return this.optimisticLockManager.updateWithOptimisticLock(
      this.config.tableName,
      key,
      updateFn,
      options
    );
  }

  // Distributed locking
  async acquireLock(resource: string, options?: any) {
    return this.distributedLockManager.acquireLock(resource, options);
  }

  async withLock<T>(resource: string, operation: () => Promise<T>, options?: any) {
    return this.distributedLockManager.withLock(resource, operation, options);
  }

  // High-level transaction patterns
  async createProjectWithAgents(projectData: any, agentsData: any[]) {
    const items: TransactionItem[] = [
      {
        operation: 'Put',
        tableName: this.config.tableName,
        item: {
          ...projectData,
          PK: `PROJECT#${projectData.id}`,
          SK: 'METADATA',
          EntityType: 'PROJECT'
        }
      },
      ...agentsData.map(agent => ({
        operation: 'Put' as const,
        tableName: this.config.tableName,
        item: {
          ...agent,
          PK: `PROJECT#${projectData.id}`,
          SK: `AGENT#${agent.id}`,
          EntityType: 'AGENT'
        }
      }))
    ];

    return this.executeTransaction(items);
  }

  async updateUserWithSession(userId: string, userData: any, sessionData: any) {
    return this.updateWithOptimisticLock(
      { PK: `USER#${userId}`, SK: 'METADATA' },
      (current: any) => ({
        ...userData,
        LastLoginAt: new Date().toISOString(),
        SessionId: sessionData.id
      })
    );
  }

  async transferProjectOwnership(projectId: string, fromUserId: string, toUserId: string) {
    const sagaDefinition: SagaDefinition = {
      name: 'TransferProjectOwnership',
      steps: [
        {
          name: 'ValidateProject',
          execute: async (context) => {
            const project = await this.readTransaction([{
              tableName: this.config.tableName,
              key: { PK: `PROJECT#${projectId}`, SK: 'METADATA' }
            }]);
            
            if (!project[0] || project[0].OwnerId !== fromUserId) {
              throw new Error('Project not found or not owned by user');
            }
            
            return { project: project[0] };
          },
          compensate: async () => {} // No compensation needed
        },
        {
          name: 'UpdateProjectOwner',
          execute: async (context) => {
            await this.executeTransaction([{
              operation: 'Update',
              tableName: this.config.tableName,
              key: { PK: `PROJECT#${projectId}`, SK: 'METADATA' },
              updateExpression: 'SET OwnerId = :newOwner, UpdatedAt = :updatedAt',
              expressionAttributeValues: {
                ':newOwner': toUserId,
                ':updatedAt': new Date().toISOString()
              }
            }]);
            
            return { ownershipTransferred: true };
          },
          compensate: async (context) => {
            // Revert ownership
            await this.executeTransaction([{
              operation: 'Update',
              tableName: this.config.tableName,
              key: { PK: `PROJECT#${projectId}`, SK: 'METADATA' },
              updateExpression: 'SET OwnerId = :originalOwner',
              expressionAttributeValues: {
                ':originalOwner': fromUserId
              }
            }]);
          }
        }
      ]
    };

    return this.executeSaga(sagaDefinition, { projectId, fromUserId, toUserId });
  }
}