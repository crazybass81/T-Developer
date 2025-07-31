import { SyncItem } from './sync-manager';

export interface ConflictResolution {
  strategy: 'merge' | 'client-wins' | 'server-wins' | 'manual';
  result: SyncItem;
  metadata: Record<string, any>;
}

export class ConflictResolver {
  async resolve(local: SyncItem, server: SyncItem, strategy: string): Promise<ConflictResolution> {
    switch (strategy) {
      case 'merge':
        return this.mergeStrategy(local, server);
      case 'client-wins':
        return this.clientWinsStrategy(local, server);
      case 'server-wins':
        return this.serverWinsStrategy(local, server);
      case 'last-write-wins':
        return this.lastWriteWinsStrategy(local, server);
      default:
        return this.manualStrategy(local, server);
    }
  }

  private mergeStrategy(local: SyncItem, server: SyncItem): ConflictResolution {
    const merged = this.deepMerge(local.data, server.data);
    
    return {
      strategy: 'merge',
      result: {
        ...local,
        data: merged,
        version: Math.max(local.version, server.version) + 1,
        lastModified: new Date(),
        checksum: this.calculateChecksum(merged)
      },
      metadata: {
        mergedFields: this.getMergedFields(local.data, server.data),
        conflicts: this.getConflicts(local.data, server.data)
      }
    };
  }

  private clientWinsStrategy(local: SyncItem, server: SyncItem): ConflictResolution {
    return {
      strategy: 'client-wins',
      result: {
        ...local,
        version: server.version + 1
      },
      metadata: {
        overriddenServer: server
      }
    };
  }

  private serverWinsStrategy(local: SyncItem, server: SyncItem): ConflictResolution {
    return {
      strategy: 'server-wins',
      result: server,
      metadata: {
        overriddenLocal: local
      }
    };
  }

  private lastWriteWinsStrategy(local: SyncItem, server: SyncItem): ConflictResolution {
    const winner = local.lastModified > server.lastModified ? local : server;
    
    return {
      strategy: 'last-write-wins',
      result: winner,
      metadata: {
        winner: winner === local ? 'local' : 'server',
        loser: winner === local ? server : local
      }
    };
  }

  private manualStrategy(local: SyncItem, server: SyncItem): ConflictResolution {
    return {
      strategy: 'manual',
      result: {
        ...local,
        data: {
          ...local.data,
          _conflict: true,
          _localVersion: local,
          _serverVersion: server
        }
      },
      metadata: {
        requiresManualResolution: true
      }
    };
  }

  private deepMerge(obj1: any, obj2: any): any {
    const result = { ...obj1 };
    
    for (const key in obj2) {
      if (obj2[key] && typeof obj2[key] === 'object' && !Array.isArray(obj2[key])) {
        result[key] = this.deepMerge(result[key] || {}, obj2[key]);
      } else {
        result[key] = obj2[key];
      }
    }
    
    return result;
  }

  private getMergedFields(local: any, server: any): string[] {
    const fields = new Set([...Object.keys(local), ...Object.keys(server)]);
    return Array.from(fields);
  }

  private getConflicts(local: any, server: any): Array<{ field: string; local: any; server: any }> {
    const conflicts = [];
    
    for (const key in local) {
      if (key in server && JSON.stringify(local[key]) !== JSON.stringify(server[key])) {
        conflicts.push({ field: key, local: local[key], server: server[key] });
      }
    }
    
    return conflicts;
  }

  private calculateChecksum(data: any): string {
    return Buffer.from(JSON.stringify(data)).toString('base64');
  }
}