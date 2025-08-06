// Runtime module exports
export { HighAvailabilityManager } from './high-availability';
export { DisasterRecoveryManager, BackupManager } from './disaster-recovery';

// Runtime configuration types
export interface RuntimeConfig {
  primaryRegion: string;
  drRegions: string[];
  backupRetentionDays: number;
  healthCheckInterval: number;
  failoverThreshold: number;
}

// Default runtime configuration
export const defaultRuntimeConfig: RuntimeConfig = {
  primaryRegion: 'us-east-1',
  drRegions: ['us-west-2', 'eu-west-1'],
  backupRetentionDays: 30,
  healthCheckInterval: 30000, // 30 seconds
  failoverThreshold: 3 // 3 consecutive failures
};

// Runtime status types
export interface RuntimeStatus {
  region: string;
  status: 'healthy' | 'degraded' | 'failed';
  lastHealthCheck: Date;
  responseTime: number;
  errorCount: number;
}

// Failover event types
export interface FailoverEvent {
  timestamp: Date;
  fromRegion: string;
  toRegion: string;
  reason: string;
  duration: number;
  success: boolean;
}