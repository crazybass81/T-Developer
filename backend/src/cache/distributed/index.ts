export { RedisClusterManager } from './cluster-manager';
export { ConsistentHashRing } from './consistent-hash';
export { ReplicationManager } from './replication-manager';
export { SyncCoordinator } from './sync-coordinator';
export { DistributedCacheService } from './distributed-cache-service';

export type { ClusterNode, ClusterConfig } from './cluster-manager';
export type { HashNode } from './consistent-hash';
export type { ReplicationConfig } from './replication-manager';
export type { SyncEvent, ConflictResolution } from './sync-coordinator';
export type { DistributedCacheConfig } from './distributed-cache-service';