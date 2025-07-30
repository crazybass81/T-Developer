import { CacheManager } from './cache-manager';
import { User } from '../data/models/user.model';
import { Project } from '../data/models/project.model';
import { Agent } from '../data/models/agent.model';

export class CacheService {
  constructor(private cacheManager: CacheManager) {}

  // User caching
  async getUser(userId: string, loader?: () => Promise<User>): Promise<User | null> {
    const key = `user:${userId}`;
    return this.cacheManager.get(key, loader);
  }

  async setUser(user: User): Promise<void> {
    const key = `user:${user.id}`;
    await this.cacheManager.set(key, user, 'user');
  }

  async invalidateUser(userId: string): Promise<void> {
    await this.cacheManager.del(`user:${userId}`);
    await this.cacheManager.invalidateByPattern(`user:${userId}:*`);
  }

  // Project caching
  async getProject(projectId: string, loader?: () => Promise<Project>): Promise<Project | null> {
    const key = `project:${projectId}`;
    return this.cacheManager.get(key, loader);
  }

  async setProject(project: Project): Promise<void> {
    const key = `project:${project.id}`;
    await this.cacheManager.set(key, project, 'project');
  }

  async getUserProjects(userId: string, loader?: () => Promise<Project[]>): Promise<Project[] | null> {
    const key = `user:${userId}:projects`;
    return this.cacheManager.get(key, loader);
  }

  async invalidateProject(projectId: string): Promise<void> {
    await this.cacheManager.del(`project:${projectId}`);
    await this.cacheManager.invalidateByPattern(`project:${projectId}:*`);
    await this.cacheManager.invalidateByTag('project');
  }

  // Agent caching
  async getAgent(agentId: string, loader?: () => Promise<Agent>): Promise<Agent | null> {
    const key = `agent:${agentId}`;
    return this.cacheManager.get(key, loader);
  }

  async setAgent(agent: Agent): Promise<void> {
    const key = `agent:${agent.id}`;
    await this.cacheManager.set(key, agent, 'agent');
  }

  async getProjectAgents(projectId: string, loader?: () => Promise<Agent[]>): Promise<Agent[] | null> {
    const key = `project:${projectId}:agents`;
    return this.cacheManager.get(key, loader);
  }

  async invalidateAgent(agentId: string): Promise<void> {
    await this.cacheManager.del(`agent:${agentId}`);
    await this.cacheManager.invalidateByTag('agent');
  }

  // Query result caching
  async cacheQueryResult<T>(queryKey: string, result: T, ttl?: number): Promise<void> {
    await this.cacheManager.set(`query:${queryKey}`, result, 'query');
  }

  async getQueryResult<T>(queryKey: string): Promise<T | null> {
    return this.cacheManager.get(`query:${queryKey}`);
  }

  // Session caching for Agno agents (ultra-fast access)
  async cacheAgentSession(sessionId: string, context: any): Promise<void> {
    const key = `session:${sessionId}`;
    await this.cacheManager.set(key, context, 'agent'); // Short TTL for sessions
  }

  async getAgentSession(sessionId: string): Promise<any | null> {
    const key = `session:${sessionId}`;
    return this.cacheManager.get(key);
  }

  async invalidateSession(sessionId: string): Promise<void> {
    await this.cacheManager.del(`session:${sessionId}`);
  }

  // Bulk operations for performance
  async warmupUserData(userId: string, loaders: {
    user: () => Promise<User>;
    projects: () => Promise<Project[]>;
  }): Promise<void> {
    await this.cacheManager.warmCache([
      { key: `user:${userId}`, loader: loaders.user, strategy: 'user' },
      { key: `user:${userId}:projects`, loader: loaders.projects, strategy: 'project' }
    ]);
  }

  async getMetrics() {
    return this.cacheManager.getMetrics();
  }
}