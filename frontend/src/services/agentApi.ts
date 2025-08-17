import apiClient from './apiClient'
import {
  Agent,
  AgentStatus,
  AgentType,
  AgentInput,
  AgentOutput,
  ApiEndpoint,
  PaginationParams
} from '../types/api'

class AgentAPI {
  private statusPollingIntervals: Map<string, NodeJS.Timeout> = new Map()
  private statusCallbacks: Map<string, (status: AgentStatus) => void> = new Map()

  /**
   * Get all agents
   */
  async getAgents(params?: PaginationParams): Promise<Agent[]> {
    const queryParams = new URLSearchParams()
    if (params) {
      if (params.page) queryParams.append('page', params.page.toString())
      if (params.pageSize) queryParams.append('pageSize', params.pageSize.toString())
      if (params.sortBy) queryParams.append('sortBy', params.sortBy)
      if (params.sortOrder) queryParams.append('sortOrder', params.sortOrder)
    }

    const url = queryParams.toString()
      ? `${ApiEndpoint.AGENTS}?${queryParams.toString()}`
      : ApiEndpoint.AGENTS

    return await apiClient.get<Agent[]>(url, {
      cache: {
        key: `agents-${queryParams.toString()}`,
        ttl: 5000 // Cache for 5 seconds
      }
    })
  }

  /**
   * Get a specific agent by ID
   */
  async getAgent(id: string): Promise<Agent> {
    const url = ApiEndpoint.AGENT_BY_ID.replace(':id', id)

    return await apiClient.get<Agent>(url, {
      cache: {
        key: `agent-${id}`,
        ttl: 3000 // Cache for 3 seconds
      }
    })
  }

  /**
   * Get agents by type
   */
  async getAgentsByType(type: AgentType): Promise<Agent[]> {
    const agents = await this.getAgents()
    return agents.filter(agent => agent.type === type)
  }

  /**
   * Get active agents
   */
  async getActiveAgents(): Promise<Agent[]> {
    const agents = await this.getAgents()
    return agents.filter(agent => agent.status === AgentStatus.RUNNING)
  }

  /**
   * Create a new agent
   */
  async createAgent(data: Partial<Agent>): Promise<Agent> {
    return await apiClient.post<Agent>(ApiEndpoint.AGENTS, data)
  }

  /**
   * Update an agent
   */
  async updateAgent(id: string, data: Partial<Agent>): Promise<Agent> {
    const url = ApiEndpoint.AGENT_BY_ID.replace(':id', id)
    return await apiClient.put<Agent>(url, data)
  }

  /**
   * Delete an agent
   */
  async deleteAgent(id: string): Promise<void> {
    const url = ApiEndpoint.AGENT_BY_ID.replace(':id', id)
    await apiClient.delete(url)

    // Stop polling if active
    this.stopStatusPolling(id)
  }

  /**
   * Start an agent
   */
  async startAgent(id: string, input?: AgentInput): Promise<Agent> {
    const url = ApiEndpoint.AGENT_START.replace(':id', id)
    const agent = await apiClient.post<Agent>(url, input)

    // Start polling for status updates
    this.startStatusPolling(id)

    return agent
  }

  /**
   * Stop an agent
   */
  async stopAgent(id: string): Promise<Agent> {
    const url = ApiEndpoint.AGENT_STOP.replace(':id', id)
    const agent = await apiClient.post<Agent>(url)

    // Stop polling
    this.stopStatusPolling(id)

    return agent
  }

  /**
   * Restart an agent
   */
  async restartAgent(id: string): Promise<Agent> {
    const url = ApiEndpoint.AGENT_RESTART.replace(':id', id)
    const agent = await apiClient.post<Agent>(url, null, {
      retry: {
        maxRetries: 3,
        retryDelay: 1000,
        retryCondition: (error) => error.response?.status >= 500
      }
    })

    // Restart polling
    this.stopStatusPolling(id)
    this.startStatusPolling(id)

    return agent
  }

  /**
   * Execute an agent task
   */
  async executeTask(agentId: string, input: AgentInput): Promise<AgentOutput> {
    const url = `${ApiEndpoint.AGENTS}/${agentId}/execute`

    return await apiClient.post<AgentOutput>(url, input, {
      retry: {
        maxRetries: 2,
        retryDelay: 2000,
        retryCondition: (error) => error.response?.status >= 500
      }
    })
  }

  /**
   * Get agent execution history
   */
  async getExecutionHistory(agentId: string, limit: number = 10): Promise<AgentOutput[]> {
    const url = `${ApiEndpoint.AGENTS}/${agentId}/history?limit=${limit}`

    return await apiClient.get<AgentOutput[]>(url, {
      cache: {
        key: `agent-history-${agentId}-${limit}`,
        ttl: 10000 // Cache for 10 seconds
      }
    })
  }

  /**
   * Get agent metrics
   */
  async getAgentMetrics(agentId: string): Promise<any> {
    const url = `${ApiEndpoint.AGENTS}/${agentId}/metrics`

    return await apiClient.get(url, {
      cache: {
        key: `agent-metrics-${agentId}`,
        ttl: 5000 // Cache for 5 seconds
      }
    })
  }

  /**
   * Check agent health
   */
  async checkHealth(agentId: string): Promise<boolean> {
    try {
      const agent = await this.getAgent(agentId)
      return agent.status !== AgentStatus.FAILED && !agent.error
    } catch {
      return false
    }
  }

  /**
   * Start polling for agent status updates
   */
  private startStatusPolling(agentId: string, interval: number = 2000): void {
    // Clear any existing polling for this agent
    this.stopStatusPolling(agentId)

    const pollInterval = setInterval(async () => {
      try {
        const agent = await this.getAgent(agentId)

        // Notify callbacks
        const callback = this.statusCallbacks.get(agentId)
        if (callback) {
          callback(agent.status)
        }

        // Stop polling if agent is idle or failed
        if (
          agent.status === AgentStatus.IDLE ||
          agent.status === AgentStatus.COMPLETED ||
          agent.status === AgentStatus.FAILED ||
          agent.status === AgentStatus.STOPPED
        ) {
          this.stopStatusPolling(agentId)
        }
      } catch (error) {
        console.error(`Error polling agent ${agentId} status:`, error)
      }
    }, interval)

    this.statusPollingIntervals.set(agentId, pollInterval)
  }

  /**
   * Stop polling for agent status updates
   */
  private stopStatusPolling(agentId: string): void {
    const interval = this.statusPollingIntervals.get(agentId)
    if (interval) {
      clearInterval(interval)
      this.statusPollingIntervals.delete(agentId)
    }
  }

  /**
   * Register a callback for status updates
   */
  onStatusChange(agentId: string, callback: (status: AgentStatus) => void): void {
    this.statusCallbacks.set(agentId, callback)
  }

  /**
   * Unregister a status callback
   */
  offStatusChange(agentId: string): void {
    this.statusCallbacks.delete(agentId)
  }

  /**
   * Batch execute multiple agents
   */
  async batchExecute(tasks: Array<{ agentId: string; input: AgentInput }>): Promise<AgentOutput[]> {
    const promises = tasks.map(task =>
      this.executeTask(task.agentId, task.input)
    )

    return await Promise.all(promises)
  }

  /**
   * Get agent dependencies
   */
  async getAgentDependencies(agentId: string): Promise<string[]> {
    const url = `${ApiEndpoint.AGENTS}/${agentId}/dependencies`
    return await apiClient.get<string[]>(url)
  }

  /**
   * Validate agent configuration
   */
  async validateConfig(agentId: string, config: any): Promise<{ valid: boolean; errors?: string[] }> {
    const url = `${ApiEndpoint.AGENTS}/${agentId}/validate`
    return await apiClient.post(url, { config })
  }

  /**
   * Get agent logs
   */
  async getAgentLogs(agentId: string, limit: number = 100): Promise<any[]> {
    const url = `${ApiEndpoint.AGENTS}/${agentId}/logs?limit=${limit}`

    return await apiClient.get(url, {
      cache: {
        key: `agent-logs-${agentId}-${limit}`,
        ttl: 2000 // Cache for 2 seconds
      }
    })
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    // Stop all polling intervals
    this.statusPollingIntervals.forEach((_, agentId) => {
      this.stopStatusPolling(agentId)
    })

    // Clear callbacks
    this.statusCallbacks.clear()
  }
}

// Create and export singleton instance
const agentAPI = new AgentAPI()

export default agentAPI
