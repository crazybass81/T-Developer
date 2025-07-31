export { 
  ChangeDataCapture, 
  CDCProcessor, 
  CDCMetrics,
  type ChangeEvent,
  type CDCConfig 
} from './change-capture';

export { 
  ChangeLogger, 
  ChangeAggregator,
  type ChangeLogEntry,
  type FieldChange 
} from './change-log';

export { 
  DataReplicator, 
  ConflictResolver,
  ReplicationMonitor,
  type ReplicationTarget,
  type ReplicationRule 
} from './replication';

export { 
  CDCService, 
  CDCManager,
  type CDCServiceConfig 
} from './cdc-service';