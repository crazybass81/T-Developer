/**
 * T-Developer Table Schema Definitions
 * 테이블 스키마 정의 및 엔티티 매핑
 */

import { AttributeValue } from '@aws-sdk/client-dynamodb';

/**
 * Base Entity Interface
 */
export interface BaseEntity {
  PK: string;
  SK: string;
  EntityType: string;
  EntityId: string;
  Status: EntityStatus;
  CreatedAt: string;
  UpdatedAt: string;
  CreatedBy?: string;
  UpdatedBy?: string;
  Version?: number;
  Priority?: number;
  TTL?: number;
  Data: string;
  Metadata?: string;
  
  // GSI attributes
  GSI1PK?: string;
  GSI1SK?: string;
  GSI2PK?: string;
  GSI2SK?: string;
  GSI3PK?: string;
}

/**
 * Entity Status Enum
 */
export enum EntityStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  ARCHIVED = 'ARCHIVED',
  DELETED = 'DELETED'
}

/**
 * User Entity Schema
 */
export interface UserEntity extends BaseEntity {
  EntityType: 'USER';
  Data: string; // JSON: UserData
}

export interface UserData {
  userId: string;
  username: string;
  email: string;
  fullName?: string;
  avatarUrl?: string;
  role: UserRole;
  permissions: string[];
  preferences: UserPreferences;
  authProviders: AuthProvider[];
  lastLoginAt?: string;
  emailVerified: boolean;
  phoneNumber?: string;
  phoneVerified?: boolean;
  twoFactorEnabled: boolean;
}

export enum UserRole {
  ADMIN = 'ADMIN',
  DEVELOPER = 'DEVELOPER',
  MANAGER = 'MANAGER',
  VIEWER = 'VIEWER'
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
}

export interface AuthProvider {
  provider: 'cognito' | 'google' | 'github' | 'microsoft';
  providerId: string;
  linkedAt: string;
}

/**
 * Project Entity Schema
 */
export interface ProjectEntity extends BaseEntity {
  EntityType: 'PROJECT';
  Data: string; // JSON: ProjectData
}

export interface ProjectData {
  projectId: string;
  name: string;
  description?: string;
  ownerId: string;
  organizationId?: string;
  visibility: 'public' | 'private' | 'organization';
  repository?: {
    type: 'github' | 'gitlab' | 'bitbucket' | 'codecommit';
    url: string;
    branch: string;
  };
  settings: ProjectSettings;
  tags: string[];
  metrics: ProjectMetrics;
}

export interface ProjectSettings {
  autoDeployEnabled: boolean;
  cicdEnabled: boolean;
  monitoringEnabled: boolean;
  alertingEnabled: boolean;
  backupEnabled: boolean;
  maxAgents: number;
  maxTasks: number;
  resourceLimits: {
    cpu: number;
    memory: number;
    storage: number;
  };
}

export interface ProjectMetrics {
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  avgExecutionTime: number;
  lastActivityAt: string;
  storageUsed: number;
  computeHours: number;
}

/**
 * Agent Entity Schema
 */
export interface AgentEntity extends BaseEntity {
  EntityType: 'AGENT';
  Data: string; // JSON: AgentData
}

export interface AgentData {
  agentId: string;
  name: string;
  type: AgentType;
  version: string;
  description?: string;
  projectId: string;
  configuration: AgentConfiguration;
  capabilities: string[];
  dependencies: string[];
  metrics: AgentMetrics;
  health: AgentHealth;
}

export enum AgentType {
  NL_INPUT = 'NL_INPUT',
  UI_SELECTION = 'UI_SELECTION',
  PARSER = 'PARSER',
  COMPONENT_DECISION = 'COMPONENT_DECISION',
  MATCH_RATE = 'MATCH_RATE',
  SEARCH = 'SEARCH',
  GENERATION = 'GENERATION',
  ASSEMBLY = 'ASSEMBLY',
  DOWNLOAD = 'DOWNLOAD',
  CUSTOM = 'CUSTOM'
}

export interface AgentConfiguration {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  timeout?: number;
  retryPolicy?: {
    maxRetries: number;
    backoffMultiplier: number;
  };
  environment?: Record<string, string>;
  resources?: {
    cpu: number;
    memory: number;
  };
}

export interface AgentMetrics {
  totalExecutions: number;
  successfulExecutions: number;
  failedExecutions: number;
  avgResponseTime: number;
  p95ResponseTime: number;
  p99ResponseTime: number;
  lastExecutionAt?: string;
  errorRate: number;
  throughput: number;
}

export interface AgentHealth {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  lastHealthCheck: string;
  issues?: string[];
  uptime: number;
}

/**
 * Task Entity Schema
 */
export interface TaskEntity extends BaseEntity {
  EntityType: 'TASK';
  Data: string; // JSON: TaskData
}

export interface TaskData {
  taskId: string;
  name: string;
  description?: string;
  projectId: string;
  agentId: string;
  type: TaskType;
  input: any;
  output?: any;
  configuration: TaskConfiguration;
  schedule?: TaskSchedule;
  dependencies?: string[];
  result?: TaskResult;
}

export enum TaskType {
  UI_GENERATION = 'UI_GENERATION',
  API_DEVELOPMENT = 'API_DEVELOPMENT',
  DATABASE_DESIGN = 'DATABASE_DESIGN',
  CODE_REVIEW = 'CODE_REVIEW',
  TESTING = 'TESTING',
  DEPLOYMENT = 'DEPLOYMENT',
  MONITORING = 'MONITORING',
  CUSTOM = 'CUSTOM'
}

export interface TaskConfiguration {
  priority: 'low' | 'normal' | 'high' | 'critical';
  timeout: number;
  retries: number;
  parallel: boolean;
  notifications: {
    onStart: boolean;
    onComplete: boolean;
    onFailure: boolean;
  };
}

export interface TaskSchedule {
  type: 'once' | 'recurring' | 'cron';
  expression?: string;
  startTime?: string;
  endTime?: string;
  timezone?: string;
}

export interface TaskResult {
  status: 'success' | 'failure' | 'partial';
  executionTime: number;
  startedAt: string;
  completedAt: string;
  output?: any;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  artifacts?: {
    type: string;
    url: string;
    size: number;
  }[];
}

/**
 * Session Entity Schema
 */
export interface SessionEntity extends BaseEntity {
  EntityType: 'SESSION';
  Data: string; // JSON: SessionData
}

export interface SessionData {
  sessionId: string;
  userId: string;
  projectId?: string;
  type: 'development' | 'debugging' | 'testing' | 'monitoring';
  startTime: string;
  endTime?: string;
  duration?: number;
  context: SessionContext;
  events: SessionEvent[];
  metrics: SessionMetrics;
}

export interface SessionContext {
  environment: string;
  agentIds: string[];
  taskIds: string[];
  resources: Record<string, any>;
  variables: Record<string, any>;
}

export interface SessionEvent {
  timestamp: string;
  type: string;
  source: string;
  data: any;
}

export interface SessionMetrics {
  totalEvents: number;
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  totalAgents: number;
  resourceUsage: {
    cpu: number;
    memory: number;
    network: number;
  };
}

/**
 * Type Guards
 */
export function isUserEntity(entity: BaseEntity): entity is UserEntity {
  return entity.EntityType === 'USER';
}

export function isProjectEntity(entity: BaseEntity): entity is ProjectEntity {
  return entity.EntityType === 'PROJECT';
}

export function isAgentEntity(entity: BaseEntity): entity is AgentEntity {
  return entity.EntityType === 'AGENT';
}

export function isTaskEntity(entity: BaseEntity): entity is TaskEntity {
  return entity.EntityType === 'TASK';
}

export function isSessionEntity(entity: BaseEntity): entity is SessionEntity {
  return entity.EntityType === 'SESSION';
}

/**
 * Entity Serialization Helpers
 */
export class EntitySerializer {
  static serialize<T>(data: T): string {
    return JSON.stringify(data);
  }
  
  static deserialize<T>(data: string): T {
    return JSON.parse(data);
  }
  
  static toItem(entity: BaseEntity): Record<string, AttributeValue> {
    const item: Record<string, AttributeValue> = {};
    
    for (const [key, value] of Object.entries(entity)) {
      if (value === undefined || value === null) continue;
      
      if (typeof value === 'string') {
        item[key] = { S: value };
      } else if (typeof value === 'number') {
        item[key] = { N: value.toString() };
      } else if (typeof value === 'boolean') {
        item[key] = { BOOL: value };
      } else if (typeof value === 'object') {
        item[key] = { S: JSON.stringify(value) };
      }
    }
    
    return item;
  }
  
  static fromItem(item: Record<string, AttributeValue>): BaseEntity {
    const entity: any = {};
    
    for (const [key, value] of Object.entries(item)) {
      if (value.S !== undefined) {
        entity[key] = value.S;
      } else if (value.N !== undefined) {
        entity[key] = parseFloat(value.N);
      } else if (value.BOOL !== undefined) {
        entity[key] = value.BOOL;
      }
    }
    
    return entity as BaseEntity;
  }
}