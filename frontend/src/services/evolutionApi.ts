import apiClient from './apiClient'
import {
  EvolutionCycle,
  EvolutionConfig,
  EvolutionStatus,
  StartEvolutionRequest,
  StartEvolutionResponse,
  ApiEndpoint
} from '../types/api'

class EvolutionAPI {
  private pollingInterval: NodeJS.Timeout | null = null
  private statusCallbacks: Map<string, (status: EvolutionStatus) => void> = new Map()

  /**
   * Start a new evolution cycle
   */
  async start(config: EvolutionConfig): Promise<StartEvolutionResponse> {
    const request: StartEvolutionRequest = {
      config,
      context: {
        initiated_by: 'frontend',
        timestamp: new Date().toISOString()
      }
    }

    const response = await apiClient.post<StartEvolutionResponse>(
      ApiEndpoint.EVOLUTION_START,
      request,
      {
        retry: {
          maxRetries: 3,
          retryDelay: 1000,
          retryCondition: (error) => error.response?.status >= 500
        }
      }
    )

    // Start polling for status updates
    if (response.evolution_id) {
      this.startStatusPolling(response.evolution_id)
    }

    return response
  }

  /**
   * Stop the current evolution cycle
   */
  async stop(evolutionId?: string): Promise<void> {
    await apiClient.post(ApiEndpoint.EVOLUTION_STOP, { evolution_id: evolutionId })
    this.stopStatusPolling()
  }

  /**
   * Get current evolution status
   */
  async getStatus(): Promise<EvolutionStatus> {
    const response = await apiClient.get<{ status: EvolutionStatus }>(
      ApiEndpoint.EVOLUTION_STATUS,
      {
        cache: {
          key: 'evolution-status',
          ttl: 1000 // Cache for 1 second
        }
      }
    )
    return response.status
  }

  /**
   * Get all evolution cycles
   */
  async getCycles(limit?: number, offset?: number): Promise<EvolutionCycle[]> {
    const params = new URLSearchParams()
    if (limit) params.append('limit', limit.toString())
    if (offset) params.append('offset', offset.toString())

    const url = params.toString()
      ? `${ApiEndpoint.EVOLUTION_CYCLES}?${params.toString()}`
      : ApiEndpoint.EVOLUTION_CYCLES

    return await apiClient.get<EvolutionCycle[]>(url, {
      cache: {
        key: `evolution-cycles-${limit}-${offset}`,
        ttl: 5000 // Cache for 5 seconds
      }
    })
  }

  /**
   * Get a specific evolution cycle by ID
   */
  async getCycle(id: string): Promise<EvolutionCycle> {
    const url = ApiEndpoint.EVOLUTION_CYCLE_BY_ID.replace(':id', id)

    return await apiClient.get<EvolutionCycle>(url, {
      cache: {
        key: `evolution-cycle-${id}`,
        ttl: 10000 // Cache for 10 seconds
      }
    })
  }

  /**
   * Get the latest evolution cycle
   */
  async getLatestCycle(): Promise<EvolutionCycle | null> {
    const cycles = await this.getCycles(1, 0)
    return cycles.length > 0 ? cycles[0] : null
  }

  /**
   * Start polling for evolution status updates
   */
  startStatusPolling(evolutionId: string, interval: number = 2000): void {
    this.stopStatusPolling() // Clear any existing polling

    this.pollingInterval = setInterval(async () => {
      try {
        const cycle = await this.getCycle(evolutionId)

        // Notify callbacks
        const callback = this.statusCallbacks.get(evolutionId)
        if (callback) {
          callback(cycle.status)
        }

        // Stop polling if evolution is complete
        if (
          cycle.status === EvolutionStatus.SUCCESS ||
          cycle.status === EvolutionStatus.FAILED ||
          cycle.status === EvolutionStatus.CANCELLED
        ) {
          this.stopStatusPolling()
        }
      } catch (error) {
        console.error('Error polling evolution status:', error)
      }
    }, interval)
  }

  /**
   * Public method alias for startStatusPolling
   */
  pollEvolutionStatus(evolutionId: string): void {
    this.startStatusPolling(evolutionId)
  }

  /**
   * Stop polling for status updates
   */
  private stopStatusPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
      this.pollingInterval = null
    }
  }

  /**
   * Register a callback for status updates
   */
  onStatusChange(evolutionId: string, callback: (status: EvolutionStatus) => void): void {
    this.statusCallbacks.set(evolutionId, callback)
  }

  /**
   * Unregister a status callback
   */
  offStatusChange(evolutionId: string): void {
    this.statusCallbacks.delete(evolutionId)
  }

  /**
   * Get evolution progress (0-100)
   */
  async getProgress(evolutionId: string): Promise<number> {
    const cycle = await this.getCycle(evolutionId)

    // Calculate progress based on phase
    const phaseProgress: Record<string, number> = {
      'initialization': 0,
      'research': 20,
      'analysis': 40,
      'planning': 60,
      'implementation': 80,
      'evaluation': 90,
      'completed': 100
    }

    return phaseProgress[cycle.phase] || 0
  }

  /**
   * Get improvement metrics for a cycle
   */
  async getImprovementMetrics(evolutionId: string): Promise<any> {
    const cycle = await this.getCycle(evolutionId)

    if (!cycle.metrics_before || !cycle.metrics_after) {
      return null
    }

    const improvements = {} as any
    const before = cycle.metrics_before
    const after = cycle.metrics_after

    // Calculate improvements for each metric
    for (const key in before) {
      if (after[key as keyof typeof after] !== undefined) {
        const beforeValue = before[key as keyof typeof before]
        const afterValue = after[key as keyof typeof after]
        const improvement = afterValue - beforeValue
        const percentageChange = beforeValue !== 0
          ? ((improvement / beforeValue) * 100).toFixed(2)
          : 'N/A'

        improvements[key] = {
          before: beforeValue,
          after: afterValue,
          improvement,
          percentageChange
        }
      }
    }

    return improvements
  }

  /**
   * Cancel a running evolution
   */
  async cancel(evolutionId: string): Promise<void> {
    await apiClient.post(`${ApiEndpoint.EVOLUTION_CYCLES}/${evolutionId}/cancel`)
    this.stopStatusPolling()
  }

  /**
   * Retry a failed evolution
   */
  async retry(evolutionId: string): Promise<StartEvolutionResponse> {
    const cycle = await this.getCycle(evolutionId)

    // Use the same config as the failed cycle
    const config: EvolutionConfig = {
      target_path: cycle.target_path,
      focus_areas: cycle.focus_areas,
      max_cycles: 1, // Only retry once
      dry_run: false,
      enable_code_modification: true
    }

    return this.start(config)
  }

  /**
   * Export evolution results
   */
  async exportResults(evolutionId: string, format: 'json' | 'csv' = 'json'): Promise<Blob> {
    const response = await apiClient.get(
      `${ApiEndpoint.EVOLUTION_CYCLES}/${evolutionId}/export?format=${format}`,
      {
        responseType: 'blob'
      }
    )

    return new Blob([response], {
      type: format === 'json' ? 'application/json' : 'text/csv'
    })
  }

  /**
   * Get evolution history
   */
  async getHistory(limit: number = 10, offset: number = 0): Promise<EvolutionCycle[]> {
    return this.getCycles(limit, offset)
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    this.stopStatusPolling()
    this.statusCallbacks.clear()
  }
}

// Create and export singleton instance
const evolutionAPI = new EvolutionAPI()

export default evolutionAPI
