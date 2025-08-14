import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import {
  EvolutionGeneration,
  EvolutionParameters,
  AgentGenome
} from '@/types';
import { evolutionApi } from '@/lib/api/evolution';

interface EvolutionStore {
  // State
  currentGeneration: EvolutionGeneration | null;
  generationHistory: EvolutionGeneration[];
  parameters: EvolutionParameters;
  isEvolving: boolean;
  fitnessMetrics: {
    current: number;
    average: number;
    best: number;
    worst: number;
    trend: number[];
  } | null;
  diversityMetrics: {
    genetic: number;
    phenotypic: number;
    behavioral: number;
    trend: number[];
  } | null;
  convergenceStatus: {
    converged: boolean;
    convergenceRate: number;
    estimatedGenerations: number;
    plateauDetected: boolean;
  } | null;
  safetyMetrics: {
    safetyScore: number;
    violations: number;
    quarantinedAgents: number;
    rollbacks: number;
    alerts: string[];
  } | null;
  selectedAgent: AgentGenome | null;

  // Actions
  fetchCurrentGeneration: () => Promise<void>;
  fetchGenerationHistory: (page?: number) => Promise<void>;
  updateParameters: (params: Partial<EvolutionParameters>) => Promise<void>;
  startEvolution: () => Promise<void>;
  stopEvolution: () => Promise<void>;
  fetchMetrics: () => Promise<void>;
  rollbackToGeneration: (generationId: string) => Promise<void>;
  selectAgent: (agent: AgentGenome | null) => void;
  forceMutation: (agentId: string, rate?: number) => Promise<void>;
  crossAgents: (parentIds: string[]) => Promise<void>;
}

export const useEvolutionStore = create<EvolutionStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        currentGeneration: null,
        generationHistory: [],
        parameters: {
          populationSize: 100,
          mutationRate: 0.1,
          crossoverRate: 0.7,
          eliteSize: 10,
          maxGenerations: 1000,
          fitnessThreshold: 0.95,
          diversityWeight: 0.2,
        },
        isEvolving: false,
        fitnessMetrics: null,
        diversityMetrics: null,
        convergenceStatus: null,
        safetyMetrics: null,
        selectedAgent: null,

        // Actions
        fetchCurrentGeneration: async () => {
          try {
            const response = await evolutionApi.getCurrentGeneration();
            if (response.success && response.data) {
              set({ currentGeneration: response.data });
            }
          } catch (error) {
            console.error('Failed to fetch current generation:', error);
          }
        },

        fetchGenerationHistory: async (page = 1) => {
          try {
            const response = await evolutionApi.getGenerationHistory({ page, pageSize: 20 });
            if (response.success && response.data) {
              set({ generationHistory: response.data.items });
            }
          } catch (error) {
            console.error('Failed to fetch generation history:', error);
          }
        },

        updateParameters: async (params) => {
          try {
            const response = await evolutionApi.updateParameters(params);
            if (response.success && response.data) {
              set({ parameters: response.data });
            }
          } catch (error) {
            console.error('Failed to update parameters:', error);
          }
        },

        startEvolution: async () => {
          try {
            set({ isEvolving: true });
            await evolutionApi.startEvolution();
            // Start polling for updates
            const interval = setInterval(async () => {
              if (!get().isEvolving) {
                clearInterval(interval);
                return;
              }
              await get().fetchCurrentGeneration();
              await get().fetchMetrics();
            }, 2000);
          } catch (error) {
            console.error('Failed to start evolution:', error);
            set({ isEvolving: false });
          }
        },

        stopEvolution: async () => {
          try {
            await evolutionApi.stopEvolution();
            set({ isEvolving: false });
          } catch (error) {
            console.error('Failed to stop evolution:', error);
          }
        },

        fetchMetrics: async () => {
          try {
            const [fitness, diversity, convergence, safety] = await Promise.all([
              evolutionApi.getFitnessMetrics(),
              evolutionApi.getDiversityMetrics(),
              evolutionApi.getConvergenceStatus(),
              evolutionApi.getSafetyMetrics(),
            ]);

            set({
              fitnessMetrics: fitness.data || null,
              diversityMetrics: diversity.data || null,
              convergenceStatus: convergence.data || null,
              safetyMetrics: safety.data || null,
            });
          } catch (error) {
            console.error('Failed to fetch metrics:', error);
          }
        },

        rollbackToGeneration: async (generationId) => {
          try {
            await evolutionApi.rollback(generationId);
            await get().fetchCurrentGeneration();
            await get().fetchGenerationHistory();
          } catch (error) {
            console.error('Failed to rollback:', error);
          }
        },

        selectAgent: (agent) => {
          set({ selectedAgent: agent });
        },

        forceMutation: async (agentId, rate) => {
          try {
            const response = await evolutionApi.forceMutation(agentId, rate);
            if (response.success) {
              await get().fetchCurrentGeneration();
            }
          } catch (error) {
            console.error('Failed to force mutation:', error);
          }
        },

        crossAgents: async (parentIds) => {
          try {
            const response = await evolutionApi.crossAgents(parentIds);
            if (response.success) {
              await get().fetchCurrentGeneration();
            }
          } catch (error) {
            console.error('Failed to cross agents:', error);
          }
        },
      }),
      {
        name: 'evolution-store',
        partialize: (state) => ({
          parameters: state.parameters,
        }),
      }
    )
  )
);
