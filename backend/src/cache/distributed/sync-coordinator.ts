import { EventEmitter } from 'events';
import { RedisClusterManager } from './cluster-manager';

export interface SyncEvent {
  type: 'set' | 'delete' | 'expire';
  key: string;
  value?: any;
  timestamp: number;
  nodeId: string;
}

export interface ConflictResolution {
  strategy: 'last-write-wins' | 'version-vector' | 'custom';
  resolver?: (conflicts: SyncEvent[]) => SyncEvent;
}

export class SyncCoordinator extends EventEmitter {
  private eventLog: Map<string, SyncEvent[]> = new Map();
  private syncInProgress = false;
  private conflictResolver: ConflictResolution;

  constructor(
    private cluster: RedisClusterManager,
    private nodeId: string,
    conflictResolution: ConflictResolution = { strategy: 'last-write-wins' }
  ) {
    super();
    this.conflictResolver = conflictResolution;
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.cluster.on('nodeError', ({ node }) => {
      this.handleNodeFailure(node);
    });

    this.cluster.on('ready', () => {
      this.startSyncProcess();
    });
  }

  async recordEvent(event: Omit<SyncEvent, 'nodeId' | 'timestamp'>): Promise<void> {
    const syncEvent: SyncEvent = {
      ...event,
      nodeId: this.nodeId,
      timestamp: Date.now()
    };

    // Store event locally
    if (!this.eventLog.has(event.key)) {
      this.eventLog.set(event.key, []);
    }
    this.eventLog.get(event.key)!.push(syncEvent);

    // Broadcast to other nodes
    await this.broadcastEvent(syncEvent);
  }

  private async broadcastEvent(event: SyncEvent): Promise<void> {
    const eventKey = `sync:event:${event.key}:${event.timestamp}`;
    await this.cluster.set(eventKey, event, 3600); // 1 hour TTL
  }

  async synchronize(): Promise<void> {
    if (this.syncInProgress) return;
    
    this.syncInProgress = true;
    
    try {
      // Collect events from all nodes
      const allEvents = await this.collectEvents();
      
      // Group events by key
      const eventsByKey = this.groupEventsByKey(allEvents);
      
      // Resolve conflicts for each key
      for (const [key, events] of eventsByKey) {
        await this.resolveConflicts(key, events);
      }
      
      // Clean up old events
      await this.cleanupEvents();
      
    } finally {
      this.syncInProgress = false;
    }
  }

  private async collectEvents(): Promise<SyncEvent[]> {
    const eventKeys = await this.cluster.get('sync:event:*');
    const events: SyncEvent[] = [];
    
    if (eventKeys && eventKeys.length > 0) {
      const eventData = await this.cluster.mget(eventKeys);
      events.push(...eventData.filter(Boolean));
    }
    
    return events;
  }

  private groupEventsByKey(events: SyncEvent[]): Map<string, SyncEvent[]> {
    const grouped = new Map<string, SyncEvent[]>();
    
    for (const event of events) {
      if (!grouped.has(event.key)) {
        grouped.set(event.key, []);
      }
      grouped.get(event.key)!.push(event);
    }
    
    return grouped;
  }

  private async resolveConflicts(key: string, events: SyncEvent[]): Promise<void> {
    if (events.length <= 1) return;
    
    // Sort events by timestamp
    events.sort((a, b) => a.timestamp - b.timestamp);
    
    let winningEvent: SyncEvent;
    
    switch (this.conflictResolver.strategy) {
      case 'last-write-wins':
        winningEvent = events[events.length - 1];
        break;
        
      case 'version-vector':
        winningEvent = this.resolveWithVersionVector(events);
        break;
        
      case 'custom':
        if (this.conflictResolver.resolver) {
          winningEvent = this.conflictResolver.resolver(events);
        } else {
          winningEvent = events[events.length - 1];
        }
        break;
        
      default:
        winningEvent = events[events.length - 1];
    }
    
    // Apply the winning event
    await this.applyEvent(winningEvent);
  }

  private resolveWithVersionVector(events: SyncEvent[]): SyncEvent {
    // Simple version vector implementation
    // In a real implementation, this would be more sophisticated
    const nodeVersions = new Map<string, number>();
    
    for (const event of events) {
      const currentVersion = nodeVersions.get(event.nodeId) || 0;
      nodeVersions.set(event.nodeId, Math.max(currentVersion, event.timestamp));
    }
    
    // Return the event with the highest combined version
    return events.reduce((winner, current) => {
      const winnerScore = nodeVersions.get(winner.nodeId) || 0;
      const currentScore = nodeVersions.get(current.nodeId) || 0;
      return currentScore > winnerScore ? current : winner;
    });
  }

  private async applyEvent(event: SyncEvent): Promise<void> {
    switch (event.type) {
      case 'set':
        await this.cluster.set(event.key, event.value);
        break;
        
      case 'delete':
        await this.cluster.del(event.key);
        break;
        
      case 'expire':
        // Handle expiration logic
        break;
    }
    
    this.emit('eventApplied', event);
  }

  private async cleanupEvents(): Promise<void> {
    const cutoffTime = Date.now() - (24 * 60 * 60 * 1000); // 24 hours ago
    const eventKeys = await this.cluster.get('sync:event:*');
    
    if (eventKeys && eventKeys.length > 0) {
      const eventsToDelete: string[] = [];
      
      for (const eventKey of eventKeys) {
        const event = await this.cluster.get(eventKey);
        if (event && event.timestamp < cutoffTime) {
          eventsToDelete.push(eventKey);
        }
      }
      
      if (eventsToDelete.length > 0) {
        await Promise.all(eventsToDelete.map(key => this.cluster.del(key)));
      }
    }
  }

  private async handleNodeFailure(nodeId: string): Promise<void> {
    // Mark node as failed and trigger recovery
    this.emit('nodeFailure', { nodeId, timestamp: Date.now() });
    
    // Initiate data recovery from replicas
    await this.recoverFromFailure(nodeId);
  }

  private async recoverFromFailure(failedNodeId: string): Promise<void> {
    // Implementation for recovering data from a failed node
    // This would involve redistributing data and updating the hash ring
    this.emit('recoveryStarted', { failedNodeId });
    
    // Trigger synchronization to ensure consistency
    await this.synchronize();
    
    this.emit('recoveryCompleted', { failedNodeId });
  }

  private startSyncProcess(): void {
    // Start periodic synchronization
    setInterval(async () => {
      await this.synchronize();
    }, 30000); // Sync every 30 seconds
  }

  async getEventHistory(key: string): Promise<SyncEvent[]> {
    return this.eventLog.get(key) || [];
  }

  async getSyncStatus(): Promise<{
    inProgress: boolean;
    lastSync: number;
    eventCount: number;
  }> {
    return {
      inProgress: this.syncInProgress,
      lastSync: Date.now(), // This would be tracked properly
      eventCount: Array.from(this.eventLog.values()).reduce((sum, events) => sum + events.length, 0)
    };
  }
}