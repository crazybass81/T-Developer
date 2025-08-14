import { get, post, put, del } from './client';
import {
  Agent,
  AgentMetrics,
  ApiResponse,
  PaginatedResponse,
  FilterOptions
} from '@/types';

export const agentsApi = {
  // Get all agents
  getAgents: (filters?: FilterOptions) =>
    get<PaginatedResponse<Agent>>('/api/agents', filters),

  // Get specific agent
  getAgent: (agentId: string) =>
    get<Agent>(`/api/agents/${agentId}`),

  // Create new agent
  createAgent: (agent: Partial<Agent>) =>
    post<Agent>('/api/agents', agent),

  // Update agent
  updateAgent: (agentId: string, updates: Partial<Agent>) =>
    put<Agent>(`/api/agents/${agentId}`, updates),

  // Delete agent
  deleteAgent: (agentId: string) =>
    del<{ message: string }>(`/api/agents/${agentId}`),

  // Get agent metrics
  getAgentMetrics: (agentId: string, timeRange?: string) =>
    get<AgentMetrics>(`/api/agents/${agentId}/metrics`, { timeRange }),

  // Execute agent
  executeAgent: (agentId: string, input: any) =>
    post<{ result: any; executionTime: number }>(`/api/agents/${agentId}/execute`, { input }),

  // Start agent
  startAgent: (agentId: string) =>
    post<{ message: string }>(`/api/agents/${agentId}/start`),

  // Stop agent
  stopAgent: (agentId: string) =>
    post<{ message: string }>(`/api/agents/${agentId}/stop`),

  // Restart agent
  restartAgent: (agentId: string) =>
    post<{ message: string }>(`/api/agents/${agentId}/restart`),

  // Get agent logs
  getAgentLogs: (agentId: string, lines?: number) =>
    get<{ logs: string[] }>(`/api/agents/${agentId}/logs`, { lines }),

  // Test agent
  testAgent: (agentId: string, testData?: any) =>
    post<{
      success: boolean;
      results: any[];
      errors: string[];
      performance: AgentMetrics;
    }>(`/api/agents/${agentId}/test`, testData),

  // Clone agent
  cloneAgent: (agentId: string, name: string) =>
    post<Agent>(`/api/agents/${agentId}/clone`, { name }),

  // Get agent dependencies
  getDependencies: (agentId: string) =>
    get<{
      dependencies: Agent[];
      dependents: Agent[];
      graph: any;
    }>(`/api/agents/${agentId}/dependencies`),

  // Deploy agent to production
  deployAgent: (agentId: string) =>
    post<{
      deploymentId: string;
      status: string;
      url: string;
    }>(`/api/agents/${agentId}/deploy`),

  // Rollback agent version
  rollbackAgent: (agentId: string, version: string) =>
    post<Agent>(`/api/agents/${agentId}/rollback`, { version }),

  // Get agent versions
  getAgentVersions: (agentId: string) =>
    get<{
      current: string;
      versions: {
        version: string;
        createdAt: string;
        changes: string[];
      }[];
    }>(`/api/agents/${agentId}/versions`),

  // Batch operations
  batchStart: (agentIds: string[]) =>
    post<{ success: string[]; failed: string[] }>('/api/agents/batch/start', { agentIds }),

  batchStop: (agentIds: string[]) =>
    post<{ success: string[]; failed: string[] }>('/api/agents/batch/stop', { agentIds }),

  batchDelete: (agentIds: string[]) =>
    post<{ success: string[]; failed: string[] }>('/api/agents/batch/delete', { agentIds }),

  // Get agent statistics
  getStatistics: () =>
    get<{
      total: number;
      active: number;
      idle: number;
      error: number;
      byType: Record<string, number>;
      performance: {
        avgExecutionTime: number;
        avgMemoryUsage: number;
        avgSuccessRate: number;
      };
    }>('/api/agents/statistics'),

  // Search agents
  searchAgents: (query: string) =>
    get<Agent[]>('/api/agents/search', { q: query }),

  // Get agent templates
  getTemplates: () =>
    get<{
      templates: {
        id: string;
        name: string;
        description: string;
        type: string;
        config: any;
      }[];
    }>('/api/agents/templates'),

  // Create agent from template
  createFromTemplate: (templateId: string, config: any) =>
    post<Agent>('/api/agents/from-template', { templateId, config }),
};
