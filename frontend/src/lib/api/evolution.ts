import { get, post, put } from './client';
import {
  EvolutionGeneration,
  EvolutionParameters,
  AgentGenome,
  ApiResponse,
  PaginatedResponse
} from '@/types';

export const evolutionApi = {
  // Get current generation
  getCurrentGeneration: () =>
    get<EvolutionGeneration>('/api/evolution/current'),

  // Get generation history
  getGenerationHistory: (params?: { page?: number; pageSize?: number }) =>
    get<PaginatedResponse<EvolutionGeneration>>('/api/evolution/history', params),

  // Get specific generation
  getGeneration: (generationId: string) =>
    get<EvolutionGeneration>(`/api/evolution/generation/${generationId}`),

  // Update evolution parameters
  updateParameters: (params: Partial<EvolutionParameters>) =>
    put<EvolutionParameters>('/api/evolution/parameters', params),

  // Start evolution
  startEvolution: () =>
    post<{ message: string }>('/api/evolution/start'),

  // Stop evolution
  stopEvolution: () =>
    post<{ message: string }>('/api/evolution/stop'),

  // Get fitness metrics
  getFitnessMetrics: () =>
    get<{
      current: number;
      average: number;
      best: number;
      worst: number;
      trend: number[];
    }>('/api/evolution/fitness'),

  // Get diversity metrics
  getDiversityMetrics: () =>
    get<{
      genetic: number;
      phenotypic: number;
      behavioral: number;
      trend: number[];
    }>('/api/evolution/diversity'),

  // Get convergence status
  getConvergenceStatus: () =>
    get<{
      converged: boolean;
      convergenceRate: number;
      estimatedGenerations: number;
      plateauDetected: boolean;
    }>('/api/evolution/convergence'),

  // Get agent genealogy
  getAgentGenealogy: (agentId: string) =>
    get<{
      agent: AgentGenome;
      ancestors: AgentGenome[];
      descendants: AgentGenome[];
      mutations: string[];
    }>(`/api/evolution/genealogy/${agentId}`),

  // Force mutation
  forceMutation: (agentId: string, mutationRate?: number) =>
    post<AgentGenome>(`/api/evolution/mutate/${agentId}`, { mutationRate }),

  // Cross agents
  crossAgents: (parentIds: string[]) =>
    post<AgentGenome>('/api/evolution/cross', { parentIds }),

  // Get evolution statistics
  getStatistics: () =>
    get<{
      totalGenerations: number;
      totalAgents: number;
      averageFitness: number;
      bestFitness: number;
      mutationCount: number;
      crossoverCount: number;
      extinctionEvents: number;
    }>('/api/evolution/statistics'),

  // Get safety metrics
  getSafetyMetrics: () =>
    get<{
      safetyScore: number;
      violations: number;
      quarantinedAgents: number;
      rollbacks: number;
      alerts: string[];
    }>('/api/evolution/safety'),

  // Rollback to previous generation
  rollback: (generationId: string) =>
    post<{ message: string }>(`/api/evolution/rollback/${generationId}`),

  // Export generation data
  exportGeneration: (generationId: string) =>
    get<Blob>(`/api/evolution/export/${generationId}`, { responseType: 'blob' }),

  // Import generation data
  importGeneration: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return post<{ message: string; generationId: string }>('/api/evolution/import', formData);
  },
};
