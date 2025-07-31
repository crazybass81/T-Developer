import { SyncManager, SyncConfig, SyncItem } from './sync-manager';
import { ConflictResolver } from './conflict-resolver';
import { OfflineSyncManager } from './offline-sync';
import { EventEmitter } from 'events';

export interface SyncServiceConfig extends SyncConfig {
  enableOfflineSync: boolean;
  enableConflictResolution: boolean;
}

export class SyncService extends EventEmitter {
  private syncManager: SyncManager;
  private conflictResolver: ConflictResolver;
  private offlineSync?: OfflineSyncManager;
  private syncStats = {
    totalSynced: 0,
    conflicts: 0,
    failures: 0,
    lastSync: new Date(0)
  };

  constructor(private config: SyncServiceConfig) {
    super();
    
    this.syncManager = new SyncManager(config);
    this.conflictResolver = new ConflictResolver();
    
    if (config.enableOfflineSync) {
      this.offlineSync = new OfflineSyncManager(this.syncManager);
      this.setupOfflineHandlers();
    }
    
    this.setupSyncHandlers();
  }

  private setupSyncHandlers(): void {
    this.syncManager.on('sync-completed', (data) => {
      this.syncStats.totalSynced += data.itemCount;
      this.syncStats.lastSync = new Date();
      this.emit('sync-completed', data);
    });

    this.syncManager.on('sync-failed', (error) => {
      this.syncStats.failures++;
      this.emit('sync-failed', error);
    });

    this.syncManager.on('item-synced', (item) => {
      this.emit('item-synced', item);
    });
  }

  private setupOfflineHandlers(): void {
    if (!this.offlineSync) return;

    this.offlineSync.on('online', () => {
      this.emit('connectivity-restored');
    });

    this.offlineSync.on('offline', () => {
      this.emit('connectivity-lost');
    });

    this.offlineSync.on('operation-synced', (op) => {
      this.emit('offline-operation-synced', op);
    });
  }

  async syncItem(item: SyncItem): Promise<void> {
    await this.syncManager.queueForSync(item);
  }

  async createEntity(entityType: string, entityId: string, data: any): Promise<void> {
    if (this.offlineSync) {
      await this.offlineSync.queueOperation({
        type: 'create',
        entityType,
        entityId,
        data
      });
    } else {
      const syncItem: SyncItem = {
        id: entityId,
        type: entityType,
        data,
        version: 1,
        lastModified: new Date(),
        checksum: this.calculateChecksum(data)
      };
      await this.syncItem(syncItem);
    }
  }

  async updateEntity(entityType: string, entityId: string, data: any): Promise<void> {
    if (this.offlineSync) {
      await this.offlineSync.queueOperation({
        type: 'update',
        entityType,
        entityId,
        data
      });
    } else {
      const syncItem: SyncItem = {
        id: entityId,
        type: entityType,
        data,
        version: data.version || 1,
        lastModified: new Date(),
        checksum: this.calculateChecksum(data)
      };
      await this.syncItem(syncItem);
    }
  }

  async deleteEntity(entityType: string, entityId: string): Promise<void> {
    if (this.offlineSync) {
      await this.offlineSync.queueOperation({
        type: 'delete',
        entityType,
        entityId,
        data: { deleted: true }
      });
    }
  }

  async resolveConflict(local: SyncItem, server: SyncItem, strategy?: string): Promise<void> {
    const resolution = await this.conflictResolver.resolve(
      local, 
      server, 
      strategy || this.config.conflictResolution
    );
    
    this.syncStats.conflicts++;
    await this.syncItem(resolution.result);
    this.emit('conflict-resolved', resolution);
  }

  async forcSync(): Promise<void> {
    await this.syncManager.sync();
  }

  getSyncStats(): typeof this.syncStats {
    return { ...this.syncStats };
  }

  getQueueSize(): number {
    return this.syncManager.getQueueSize();
  }

  getPendingOfflineOperations(): number {
    return this.offlineSync?.getOperationCount() || 0;
  }

  isOnline(): boolean {
    return this.offlineSync?.isConnected() ?? true;
  }

  private calculateChecksum(data: any): string {
    return Buffer.from(JSON.stringify(data)).toString('base64');
  }
}

export class SyncCoordinator {
  private services: Map<string, SyncService> = new Map();

  createService(name: string, config: SyncServiceConfig): SyncService {
    const service = new SyncService(config);
    this.services.set(name, service);
    return service;
  }

  getService(name: string): SyncService | undefined {
    return this.services.get(name);
  }

  async syncAll(): Promise<void> {
    const promises = Array.from(this.services.values()).map(service => 
      service.forcSync()
    );
    await Promise.all(promises);
  }

  getGlobalStats(): any {
    const stats = {
      totalServices: this.services.size,
      totalQueued: 0,
      totalOffline: 0,
      servicesOnline: 0
    };

    for (const service of this.services.values()) {
      stats.totalQueued += service.getQueueSize();
      stats.totalOffline += service.getPendingOfflineOperations();
      if (service.isOnline()) stats.servicesOnline++;
    }

    return stats;
  }
}