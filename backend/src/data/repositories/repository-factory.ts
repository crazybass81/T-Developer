/**
 * Repository Factory Implementation
 * Provides centralized repository instance management with dependency injection
 */

import { SingleTableClient } from '../dynamodb/single-table';
import { UserRepository } from './user.repository';
import { ProjectRepository } from './project.repository';
import { AgentRepository } from './agent.repository';

export interface RepositoryConfig {
  enableCaching?: boolean;
  cacheExpiration?: number;
  enableMetrics?: boolean;
  enableAuditLog?: boolean;
  tableName?: string;
  region?: string;
  endpoint?: string;
}

export class RepositoryFactory {
  private static instance: RepositoryFactory;
  private client: SingleTableClient;
  private config: RepositoryConfig;
  
  // Repository instances
  private userRepository?: UserRepository;
  private projectRepository?: ProjectRepository;
  private agentRepository?: AgentRepository;

  private constructor(config: RepositoryConfig = {}) {
    this.config = {
      enableCaching: true,
      cacheExpiration: 300,
      enableMetrics: true,
      enableAuditLog: true,
      tableName: 'T-Developer-Main',
      region: 'us-east-1',
      ...config
    };

    this.client = new SingleTableClient(
      this.config.tableName,
      this.config.region
    );
  }

  /**
   * Get singleton instance
   */
  public static getInstance(config?: RepositoryConfig): RepositoryFactory {
    if (!RepositoryFactory.instance) {
      RepositoryFactory.instance = new RepositoryFactory(config);
    }
    return RepositoryFactory.instance;
  }

  /**
   * Reset singleton instance (for testing)
   */
  public static resetInstance(): void {
    RepositoryFactory.instance = undefined as any;
  }

  /**
   * Get User Repository
   */
  public getUserRepository(): UserRepository {
    if (!this.userRepository) {
      this.userRepository = new UserRepository(this.client);
    }
    return this.userRepository;
  }

  /**
   * Get Project Repository
   */
  public getProjectRepository(): ProjectRepository {
    if (!this.projectRepository) {
      this.projectRepository = new ProjectRepository(this.client);
    }
    return this.projectRepository;
  }

  /**
   * Get Agent Repository
   */
  public getAgentRepository(): AgentRepository {
    if (!this.agentRepository) {
      this.agentRepository = new AgentRepository(this.client);
    }
    return this.agentRepository;
  }

  /**
   * Get all repositories
   */
  public getAllRepositories() {
    return {
      users: this.getUserRepository(),
      projects: this.getProjectRepository(),
      agents: this.getAgentRepository()
    };
  }

  /**
   * Get underlying DynamoDB client
   */
  public getClient(): SingleTableClient {
    return this.client;
  }

  /**
   * Get factory configuration
   */
  public getConfig(): RepositoryConfig {
    return { ...this.config };
  }

  /**
   * Health check for all repositories
   */
  public async healthCheck(): Promise<{
    healthy: boolean;
    repositories: Record<string, {
      healthy: boolean;
      responseTime: number;
      error?: string;
    }>;
  }> {
    const repositories = this.getAllRepositories();
    const results: Record<string, any> = {};
    let overallHealthy = true;

    // Check each repository
    for (const [name, repo] of Object.entries(repositories)) {
      try {
        const health = await repo.healthCheck();
        results[name] = health;
        if (!health.healthy) {
          overallHealthy = false;
        }
      } catch (error) {
        results[name] = {
          healthy: false,
          responseTime: 0,
          error: error instanceof Error ? error.message : 'Unknown error'
        };
        overallHealthy = false;
      }
    }

    return {
      healthy: overallHealthy,
      repositories: results
    };
  }

  /**
   * Get metrics for all repositories
   */
  public getMetrics() {
    const repositories = this.getAllRepositories();
    const metrics: Record<string, any> = {};

    for (const [name, repo] of Object.entries(repositories)) {
      metrics[name] = repo.getMetrics();
    }

    return metrics;
  }

  /**
   * Clear all caches
   */
  public clearAllCaches(): void {
    const repositories = this.getAllRepositories();
    
    for (const repo of Object.values(repositories)) {
      (repo as any).clearCache();
    }
  }

  /**
   * Reset all metrics
   */
  public resetAllMetrics(): void {
    const repositories = this.getAllRepositories();
    
    for (const repo of Object.values(repositories)) {
      repo.resetMetrics();
    }
  }
}

/**
 * Default factory instance for easy access
 */
export const repositoryFactory = RepositoryFactory.getInstance();

/**
 * Convenience exports for direct repository access
 */
export const userRepository = repositoryFactory.getUserRepository();
export const projectRepository = repositoryFactory.getProjectRepository();
export const agentRepository = repositoryFactory.getAgentRepository();