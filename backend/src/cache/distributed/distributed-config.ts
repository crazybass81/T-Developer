import { DistributedCacheConfig } from './distributed-cache-service';

export const createDistributedCacheConfig = (): DistributedCacheConfig => {
  const nodeEnv = process.env.NODE_ENV || 'development';
  
  // Base configuration optimized for T-Developer's Agno Framework performance requirements
  const baseConfig: DistributedCacheConfig = {
    nodes: [
      { host: process.env.REDIS_HOST_1 || 'localhost', port: parseInt(process.env.REDIS_PORT_1 || '6379'), weight: 1 },
      { host: process.env.REDIS_HOST_2 || 'localhost', port: parseInt(process.env.REDIS_PORT_2 || '6380'), weight: 1 },
      { host: process.env.REDIS_HOST_3 || 'localhost', port: parseInt(process.env.REDIS_PORT_3 || '6381'), weight: 1 }
    ],
    replication: {
      factor: 3, // High availability for T-Developer agents
      consistency: 'quorum', // Balance between performance and consistency
      syncInterval: 5000 // 5 seconds - optimized for Agno's 3μs agent instantiation
    },
    cluster: {
      healthCheckInterval: 10000, // 10 seconds
      retryAttempts: 3
    }
  };

  // Environment-specific optimizations
  switch (nodeEnv) {
    case 'development':
      return {
        ...baseConfig,
        nodes: [
          { host: 'localhost', port: 6379, weight: 1 }
        ],
        replication: {
          ...baseConfig.replication,
          factor: 1, // Single node for development
          consistency: 'eventual'
        }
      };

    case 'staging':
      return {
        ...baseConfig,
        replication: {
          ...baseConfig.replication,
          factor: 2, // Reduced replication for staging
          syncInterval: 10000 // 10 seconds
        }
      };

    case 'production':
      return {
        ...baseConfig,
        replication: {
          ...baseConfig.replication,
          factor: 3, // Full replication for production
          consistency: 'strong', // Strong consistency for production
          syncInterval: 3000 // 3 seconds - aggressive sync for high performance
        },
        cluster: {
          ...baseConfig.cluster,
          healthCheckInterval: 5000, // More frequent health checks
          retryAttempts: 5
        }
      };

    default:
      return baseConfig;
  }
};

// T-Developer specific cache configurations
export const T_DEVELOPER_CACHE_PATTERNS = {
  // User data - medium TTL, high consistency
  USER: {
    keyPrefix: 'user:',
    defaultTTL: 3600, // 1 hour
    consistency: 'quorum' as const,
    replicationFactor: 2
  },
  
  // Project data - medium TTL, eventual consistency
  PROJECT: {
    keyPrefix: 'project:',
    defaultTTL: 1800, // 30 minutes
    consistency: 'eventual' as const,
    replicationFactor: 2
  },
  
  // Agent results - short TTL, eventual consistency (optimized for Agno's speed)
  AGENT: {
    keyPrefix: 'agent:',
    defaultTTL: 900, // 15 minutes
    consistency: 'eventual' as const,
    replicationFactor: 1 // Single replica for speed
  },
  
  // Session data - short TTL, strong consistency
  SESSION: {
    keyPrefix: 'session:',
    defaultTTL: 1800, // 30 minutes
    consistency: 'strong' as const,
    replicationFactor: 3
  },
  
  // Component cache - long TTL, eventual consistency
  COMPONENT: {
    keyPrefix: 'component:',
    defaultTTL: 7200, // 2 hours
    consistency: 'eventual' as const,
    replicationFactor: 2
  }
};

export const getDistributedCacheConfig = () => createDistributedCacheConfig();