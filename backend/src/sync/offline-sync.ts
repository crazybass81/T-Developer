import { SyncManager, SyncItem } from './sync-manager';
import { EventEmitter } from 'events';

export interface OfflineOperation {
  id: string;
  type: 'create' | 'update' | 'delete';
  entityType: string;
  entityId: string;
  data: any;
  timestamp: Date;
  retryCount: number;
}

export class OfflineSyncManager extends EventEmitter {
  private operations: OfflineOperation[] = [];
  private isOnline = true;
  private syncManager: SyncManager;

  constructor(syncManager: SyncManager) {
    super();
    this.syncManager = syncManager;
    this.setupNetworkMonitoring();
  }

  async queueOperation(operation: Omit<OfflineOperation, 'id' | 'timestamp' | 'retryCount'>): Promise<void> {
    const op: OfflineOperation = {
      ...operation,
      id: this.generateId(),
      timestamp: new Date(),
      retryCount: 0
    };

    this.operations.push(op);
    this.emit('operation-queued', op);

    if (this.isOnline) {
      await this.processOperations();
    }
  }

  async processOperations(): Promise<void> {
    if (!this.isOnline || this.operations.length === 0) return;

    const operations = [...this.operations];
    this.operations = [];

    for (const op of operations) {
      try {
        await this.executeOperation(op);
        this.emit('operation-synced', op);
      } catch (error) {
        op.retryCount++;
        if (op.retryCount < 3) {
          this.operations.push(op);
        } else {
          this.emit('operation-failed', { operation: op, error });
        }
      }
    }
  }

  private async executeOperation(operation: OfflineOperation): Promise<void> {
    const syncItem: SyncItem = {
      id: operation.entityId,
      type: operation.entityType,
      data: operation.data,
      version: 1,
      lastModified: operation.timestamp,
      checksum: this.calculateChecksum(operation.data)
    };

    await this.syncManager.queueForSync(syncItem);
  }

  private setupNetworkMonitoring(): void {
    // Monitor network connectivity
    setInterval(() => {
      this.checkConnectivity();
    }, 5000);
  }

  private async checkConnectivity(): Promise<void> {
    try {
      // Simple connectivity check
      const wasOnline = this.isOnline;
      this.isOnline = true; // Simplified - would check actual connectivity
      
      if (!wasOnline && this.isOnline) {
        this.emit('online');
        await this.processOperations();
      }
    } catch {
      if (this.isOnline) {
        this.isOnline = false;
        this.emit('offline');
      }
    }
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private calculateChecksum(data: any): string {
    return Buffer.from(JSON.stringify(data)).toString('base64');
  }

  getPendingOperations(): OfflineOperation[] {
    return [...this.operations];
  }

  getOperationCount(): number {
    return this.operations.length;
  }

  isConnected(): boolean {
    return this.isOnline;
  }
}